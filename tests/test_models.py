import unittest
from app import create_app, db
from app.models import User, Product, Order, CartItem

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the application and database context
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Configure in-memory SQLite database for tests
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app.config['TESTING'] = True
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        user = User(username="testuser", email="test@example.com", password_hash="hashed_password")
        db.session.add(user)
        db.session.commit()
        
        retrieved_user = User.query.filter_by(email="test@example.com").first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, "testuser")

    def test_favorites_relationship(self):
        user = User(username="testuser", email="test@example.com", password_hash="hashed_password")
        product = Product(name="Chair", price=50.0)
        db.session.add(user)
        db.session.add(product)
        db.session.commit()

        user.favorites.append(product)
        db.session.commit()

        self.assertIn(product, user.favorites)
        self.assertIn(user, product.favorited_by)

    def test_product_creation(self):
        product = Product(name="Table", description="Wooden dining table", price=150.0, category="Furniture", stock_quantity=10)
        db.session.add(product)
        db.session.commit()

        retrieved_product = Product.query.filter_by(name="Table").first()
        self.assertIsNotNone(retrieved_product)
        self.assertEqual(retrieved_product.description, "Wooden dining table")
        self.assertEqual(retrieved_product.category, "Furniture")
        self.assertEqual(retrieved_product.stock_quantity, 10)

    def test_cart_item_relationship(self):
        user = User(username="testuser", email="test@example.com", password_hash="hashed_password")
        product = Product(name="Sofa", price=500.0)
        db.session.add(user)
        db.session.add(product)
        db.session.commit()

        cart_item = CartItem(user_id=user.id, product_id=product.id, quantity=2)
        db.session.add(cart_item)
        db.session.commit()

        retrieved_cart_item = CartItem.query.filter_by(user_id=user.id, product_id=product.id).first()
        self.assertIsNotNone(retrieved_cart_item)
        self.assertEqual(retrieved_cart_item.quantity, 2)
        self.assertEqual(retrieved_cart_item.product.name, "Sofa")

if __name__ == "__main__":
    unittest.main()
