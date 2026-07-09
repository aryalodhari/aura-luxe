from app import create_app, db
from app.models import (
    Category, Product, User,
    DiscountCode
)
from werkzeug.security import generate_password_hash
from datetime import datetime

#create app context
app = create_app()

with app.app_context():
    print("🗑️  Dropping all tables...")
    db.drop_all()
    
    # Create all tables
    print("🏗️  Creating all tables...")
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            email='admin@aurabyhoneyy.com',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created successfully!")

        # Categories
    print("\n📂 Creating categories...")

    categories_data = [
        {'name': 'Bags', 'description': 'Hand Bags accessories'},
        {'name': 'Sunglasses', 'description': 'Sunglasses accessories'},
        {'name': 'Shoes', 'description': 'Shoes snd sneaker products'},
    ]

    categories = []
    for c_data in categories_data:
        category = Category(
            name=c_data['name'],
            description=c_data['description']
        )
        db.session.add(category)
        categories.append(category)
    db.session.commit()
    print(f"✅ Created {Category.query.count()} categories")

    #  product data
    print("\n📦 Creating products...")
    
    product_data = [
        #Bags
        {
            'name': 'Quilted Noir Shoulder Bag',
            'description': 'A soft quilted black shoulder bag with a compact luxury silhouette',
            'price': 3499,
            'stock': 12,
            'category_id': 1,
            'image_url': 'product_1.jpg',
            'sku': 'AURA-SHOULDER_BAG-001'
        },
        {
            'name': 'Gold Chain Mini Crossbody',
            'description': 'Black textured mini crossbody with refined gold chain detailing.',
            'price': 4299,
            'stock': 8,
            'category_id': 1,
            'image_url': 'product_2.jpg',
            'sku': 'AURA-CROSSBODY_BAG-GOLD'
        },
        {
            'name': 'Signature Tote Mini',
            'description': 'A structured mini tote designed for statement daily styling.',
            'price': 3999,
            'stock': 10,
            'category_id': 1,
            'image_url': 'product_3.jpg',
            'sku': 'AURA-TOTE_MINI_BAG-001'

        },
        {
            'name': 'Quilted Chain Sling',
            'description': 'Glossy quilted sling bag with gold-tone chain and compact finish',
            'price': 4999,
            'stock': 7,
            'category_id': 1,
            'image_url': 'product_11.jpg',
            'sku': 'AURA-QUILTED_BAG-001'
        },
        {
            'name': 'Canvas City Tote',
            'description': 'Soft beige city tote for casual luxury styling.',
            'price': 3799,
            'stock': 10,
            'category_id': 1,
            'image_url': 'product_12.jpg',
            'sku': 'AURA-CITY-TOTE_BAG-001'
        },
        {
            'name': 'Executive Black Handbag',
            'description': 'Structured black handbag with premium strap detail.',
            'price': 55399,
            'stock': 5,
            'category_id': 1,
            'image_url': 'product_13.jpg',
            'sku': 'AURA-HANDBAG-BLACK'
        },
        {
            'name': 'Wine Label Tote',
            'description': 'Black tote with statement cream branded handles.',
            'price': 4899,
            'stock': 6,
            'category_id': 1,
            'image_url': 'product_14.jpg',
            'sku': 'AURA-TOTE_BAG-CREAM'
        },
        
        # Sunglasses
        {
            'name': 'Classic Black Sunglasses',
            'description': 'Sharp black sunglasses with timeless everyday appeal.',
            'price': 1499,
            'stock': 20,
            'category_id': 2,
            'image_url': 'product_4.jpg',
            'sku': 'AURA-SUNGLASSES-BLACK'
        },
        {
            'name': 'Oversized Luxe Shades',
            'description': 'Bold oversized sunglasses for a confident luxury look.',
            'price': 2299,
            'stock': 15,
            'category_id': 2,
            'image_url': 'product_5.jpg',
            'sku': 'AURA-OVERSIZED-BOLD'
        },
        {
            'name': 'Square Frame Sunglasses',
            'description': 'Premium square frames with modern edge and UV-style finish.',
            'price': 1999,
            'stock': 18,
            'category_id': 2,
            'image_url': 'product_6.jpg',
            'sku': 'AURA-FRAME-SQUARE'
        },
        {
            'name': 'Designer Detail Sunglasses',
            'description': 'Fashion-forward sunglasses with sculpted side detail.',
            'price': 2499,
            'stock': 14,
            'category_id': 2,
            'image_url': 'product_7.jpg',
            'sku': 'AURA-SUNGLASSES-001'
        },
        {
            'name': 'Runway Rectangle Shades',
            'description': 'Rectangle sunglasses with a bold runway-inspired profile.',
            'price': 2699,
            'stock': 14,
            'category_id': 2,
            'image_url': 'product_15.jpg',
            'sku': 'AURA-RUNWAY-REC'
        },
        {
            'name': 'Mono Line Sunglasses',
            'description': 'Black sunglasses with crisp white line detailing.',
            'price': 2199,
            'stock': 16,
            'category_id': 2,
            'image_url': 'product_16.jpg',
            'sku': 'AURA-MONO-001'
        },
        {
            'name': 'Tortoise Premium Shades',
            'description': 'Warm tortoise frame sunglasses with luxe hardware.',
            'price': 2899,
            'stock': 8,
            'category_id': 2,
            'image_url': 'product_17.jpg',
            'sku': 'AURA-TORTOISE-001'
        },
        {
            'name': 'Gradient Glam Sunglasses',
            'description': 'Oversized gradient sunglasses for a glamorous finish.',
            'price': 2599,
            'stock': 13,
            'category_id': 2,
            'image_url': 'product_18.jpg',
            'sku': 'AURA-GLAM-001'
        },
        #shoes
        {
            'name': 'Black Minimal Sneakers',
            'description': 'Clean black sneakers with premium casual styling.',
            'price': 3499,
            'stock': 9,
            'category_id': 3,
            'image_url': 'product_8.jpg',
            'sku': 'AURA-SNEAKERS-BLACK'
        },
        {
            'name': 'White Slip-On Sneakers',
            'description': 'Elegant white slip-on sneakers with contrast strap detail.',
            'price': 2999,
            'stock': 11,
            'category_id': 3,
            'image_url': 'product_9.jpg',
            'sku': 'AURA-SNEAKERS-WHITE'
        },
        {
            'name': 'Cloud Runner Sneakers',
            'description': 'Comfort-focused neutral sneakers for modern streetwear.',
            'price': 4599,
            'stock': 6,
            'category_id': 3,
            'image_url': 'product_10.jpg',
            'sku': 'AURA-SNEAKERS-001'
        }
    ]

    products = []
    for p_data in product_data:
        product = Product(
            name=p_data['name'],
            description=p_data['description'],
            price=p_data['price'],
            stock=p_data['stock'],
            category_id=p_data['category_id'],
            image_url=p_data['image_url']
        )
        db.session.add(product)
        products.append(product)
    db.session.commit()
    print(f"✅ Created {Product.query.count()} products")

    # Discount Codes
    print("\n🎉 Creating discount codes...")

    discounts_codes = [
        {'code': 'WELCOME10', 'discount_percent': 10, 'is_active': True, 'description': 'Welcome discount - 10% off'},
        {'code': 'AURA20', 'discount_percent': 20, 'is_active': True, 'description': '20% off orders over ₹2000'},
        {'code': 'SUMMER15', 'discount_percent': 15, 'is_active': True, 'description': '15% off orders over ₹1000'},
    ]

    for disc_data in discounts_codes:
        discount = DiscountCode(
            code=disc_data['code'],
            description=disc_data['description'],
            discount_percent=disc_data['discount_percent'],
            is_active=disc_data['is_active']
        )
        db.session.add(discount)
    
    db.session.commit()
    print(f"✅ Created {DiscountCode.query.count()} discount codes")




