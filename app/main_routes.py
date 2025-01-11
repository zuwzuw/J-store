from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import User, Product, CartItem, favorites, Review, Order, OrderItem
from .forms import RegistrationForm, LoginForm

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

# ------------------------------------------------
# User Registration and Login
# ------------------------------------------------
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('A user with this email already exists.')
            return redirect(url_for('main_bp.register'))
        
        hashed_pwd = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_pwd
        )

        # Check if there is already an admin
        admin_exists = User.query.filter_by(role='admin').first()
        if not admin_exists:
            # If no admins exist, this user becomes the admin
            new_user.role = 'admin'
            flash('Since there were no administrators, you are now an administrator.')

        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You may log in.')
        return redirect(url_for('main_bp.login'))
    return render_template('register.html', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('You are now logged in.')
            return redirect(url_for('main_bp.index'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out.')
    return redirect(url_for('main_bp.index'))

# ------------------------------------------------
# Product List and Filters
# ------------------------------------------------
@main_bp.route('/products')
def product_list():
    # Get all unique categories, colors, and materials from the database
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    colors = db.session.query(Product.color).distinct().all()
    colors = [c[0] for c in colors if c[0]]

    materials = db.session.query(Product.material).distinct().all()
    materials = [m[0] for m in materials if m[0]]

    # Get filter parameters from GET request
    selected_category = request.args.get('category')
    selected_color = request.args.get('color')
    selected_material = request.args.get('material')
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    sort_by = request.args.get('sort_by')

    query = Product.query

    # Apply filters
    if selected_category:
        query = query.filter_by(category=selected_category)
    if selected_color:
        query = query.filter_by(color=selected_color)
    if selected_material:
        query = query.filter_by(material=selected_material)
    if price_min is not None:
        query = query.filter(Product.price >= price_min)
    if price_max is not None:
        query = query.filter(Product.price <= price_max)

    # Apply sorting
    if sort_by == 'price':
        query = query.order_by(Product.price)
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc())
    elif sort_by == 'created':
        query = query.order_by(Product.created_at.desc())

    products = query.all()

    # Pass data to the template
    return render_template('product_list.html', 
                           products=products,
                           categories=categories,
                           colors=colors,
                           materials=materials,
                           selected_category=selected_category,
                           selected_color=selected_color,
                           selected_material=selected_material,
                           price_min=price_min,
                           price_max=price_max,
                           sort_by=sort_by)


@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()
    from sqlalchemy import func
    avg_rating = db.session.query(func.avg(Review.rating)).filter(Review.product_id == product_id).scalar()

    if avg_rating is None:
        avg_rating = 0  # If no reviews, default rating is 0

    # Handle missing data
    if not hasattr(product, "stock_quantity"):
        product.stock_quantity = 0

    return render_template('product_detail.html', product=product, reviews=reviews, avg_rating=avg_rating)

# ------------------------------------------------
# Cart Functionality
# ------------------------------------------------
@main_bp.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@main_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    existing_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing_item:
        existing_item.quantity += quantity
    else:
        new_cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)
    db.session.commit()
    flash('Product added to cart.')
    return redirect(url_for('main_bp.cart'))

@main_bp.route('/cart/remove/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_item_id):
    item = CartItem.query.get_or_404(cart_item_id)
    if item.user_id != current_user.id:
        flash('Cannot remove an item from someone else’s cart.')
        return redirect(url_for('main_bp.cart'))
    
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from cart.')
    return redirect(url_for('main_bp.cart'))

# ------------------------------------------------
# Favorites Functionality
# ------------------------------------------------
@main_bp.route('/favorite/<int:product_id>', methods=['POST'])
@login_required
def add_favorite(product_id):
    product = Product.query.get_or_404(product_id)
    # Check if already in favorites
    stmt = favorites.insert().values(user_id=current_user.id, product_id=product.id)
    try:
        db.session.execute(stmt)
        db.session.commit()
        flash('Added to favorites.')
    except:
        flash('This product is already in your favorites.')
    return redirect(url_for('main_bp.index'))

@main_bp.route('/favorites')
@login_required
def favorites_list():
    # Get current user's favorites
    user_favorites = Product.query.join(
        favorites, Product.id == favorites.c.product_id
    ).filter(favorites.c.user_id == current_user.id).all()

    return render_template('favorites.html', products=user_favorites)

# ------------------------------------------------
# Reviews Functionality
# ------------------------------------------------
@main_bp.route('/review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '')
    if rating < 1 or rating > 5:
        flash('Rating must be between 1 and 5.')
        return redirect(url_for('main_bp.product_detail', product_id=product_id))

    # Check if the user has already left a review
    existing_review = Review.query.filter_by(product_id=product_id, user_id=current_user.id).first()
    if existing_review:
        flash('You have already reviewed this product.')
        return redirect(url_for('main_bp.product_detail', product_id=product_id))

    new_review = Review(product_id=product_id, user_id=current_user.id, rating=rating, comment=comment)
    db.session.add(new_review)
    db.session.commit()
    flash('Review added!')
    return redirect(url_for('main_bp.product_detail', product_id=product_id))

@main_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    # Get all items in the cart
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Cannot checkout an empty cart.')
        return redirect(url_for('main_bp.cart'))

    # Create a new order
    new_order = Order(user_id=current_user.id, status='processing')
    db.session.add(new_order)
    db.session.commit()

    # Add items to the OrderItem table
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.session.add(order_item)

    # Clear the cart
    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    flash(f'Order #{new_order.id} placed successfully!')
    return redirect(url_for('main_bp.my_orders'))

@main_bp.route('/my_orders')
@login_required
def my_orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('my_orders.html', orders=user_orders)
@main_bp.route('/cart/update_quantity', methods=['POST'])
@login_required
def update_quantity():
    data = request.get_json()
    cart_item_id = data.get('cart_item_id')
    new_quantity = data.get('quantity')

    cart_item = CartItem.query.filter_by(id=cart_item_id, user_id=current_user.id).first()
    if not cart_item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    if new_quantity < 1:
        return jsonify({'success': False, 'error': 'Invalid quantity'}), 400

    cart_item.quantity = new_quantity
    db.session.commit()

    # Recalculate item total and cart total
    item_total = cart_item.product.price * cart_item.quantity
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(i.product.price * i.quantity for i in cart_items)

    return jsonify({'success': True, 'item_total': item_total, 'total': total})


@main_bp.route('/cart/remove_item', methods=['POST'])
@login_required
def remove_item():
    data = request.get_json()
    cart_item_id = data.get('cart_item_id')

    cart_item = CartItem.query.filter_by(id=cart_item_id, user_id=current_user.id).first()
    if not cart_item:
        return jsonify({'success': False, 'error': 'Item not found'}), 404

    db.session.delete(cart_item)
    db.session.commit()

    # Recalculate cart total
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(i.product.price * i.quantity for i in cart_items)

    return jsonify({'success': True, 'total': total})


@main_bp.route('/remove_favorite/<int:product_id>', methods=['POST'])
@login_required
def remove_favorite(product_id):
    # Check if the product exists
    product = Product.query.get_or_404(product_id)

    # Check if the product is in favorites
    user_favorites = Product.query.join(
        favorites, Product.id == favorites.c.product_id
    ).filter(favorites.c.user_id == current_user.id, Product.id == product_id).first()

    if user_favorites:
        # Remove from favorites
        db.session.execute(
            favorites.delete().where(
                (favorites.c.user_id == current_user.id) & 
                (favorites.c.product_id == product_id)
            )
        )
        db.session.commit()
        flash(f'The product "{product.name}" has been removed from favorites.')
    else:
        flash('This product was not found in your favorites.')

    return redirect(url_for('main_bp.favorites_list'))
