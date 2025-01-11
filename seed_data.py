from app.models import db, Product
import random

# Очистка старых данных
db.session.query(Product).delete()
db.session.commit()

# Примерные категории сувениров
categories = ["Traditional Crafts", "Ceramics", "Textiles", "Accessories", "Wooden Toys"]
materials = ["Wood", "Ceramic", "Fabric", "Glass", "Metal"]
colors = ["Red", "Blue", "Green", "Yellow", "Black", "White"]

# Генерация данных для сувениров
for i in range(1, 21):  # Создать 20 товаров
    product = Product(
        name=f"Souvenir {i}",
        description=f"Unique handmade souvenir {i} with excellent craftsmanship.",
        price=round(random.uniform(10.0, 150.0), 2),
        category=random.choice(categories),
        color=random.choice(colors),
        material=random.choice(materials),
        image_url=f"/static/images/souvenir{i}.jpg",  # Предположительно изображения уже загружены
        stock_quantity=random.randint(1, 50),
    )
    db.session.add(product)

# Сохранение данных в базе
db.session.commit()

print("Данные для сувениров успешно сгенерированы!")
