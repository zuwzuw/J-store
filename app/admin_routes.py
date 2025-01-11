from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import User, Product, Order, OrderItem
from .forms import ProductForm

admin_bp = Blueprint('admin_bp', __name__)

def admin_required(func):
    """Decorator to check for 'admin' role."""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied: insufficient permissions.')
            return redirect(url_for('main_bp.index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    return render_template('admin_dashboard.html', 
                           total_users=total_users,
                           total_products=total_products,
                           total_orders=total_orders)

@admin_bp.route('/products')
@login_required
@admin_required
def admin_products():
    products = Product.query.all()
    return render_template('admin_products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            color=form.color.data,
            material=form.material.data,
            stock_quantity=form.stock_quantity.data or 0
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added.')
        return redirect(url_for('admin_bp.admin_products'))

    return render_template('admin_products.html', form=form, mode='add')

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category = form.category.data
        product.color = form.color.data
        product.material = form.material.data
        product.stock_quantity = form.stock_quantity.data
        db.session.commit()
        flash('Product updated.')
        return redirect(url_for('admin_bp.admin_products'))
    return render_template('admin_products.html', form=form, product=product, mode='edit')

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.')
    return redirect(url_for('admin_bp.admin_products'))

@admin_bp.route('/orders')
@login_required
@admin_required
def admin_orders():
    orders = Order.query.all()
    return render_template('admin_orders.html', orders=orders)

@admin_bp.route('/orders/update_status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    new_status = request.form.get('status')
    order = Order.query.get_or_404(order_id)
    order.status = new_status
    db.session.commit()
    flash('Order status updated.')
    return redirect(url_for('admin_bp.admin_orders'))

@admin_bp.route('/reports/orders')
@login_required
@admin_required
def order_reports():
    orders = Order.query.all()
    return render_template('admin_order_reports.html', orders=orders)

@admin_bp.route('/reports/products')
@login_required
@admin_required
def product_reports():
    products = Product.query.all()
    return render_template('admin_product_reports.html', products=products)
