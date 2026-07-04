from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from app import db
from app.models import (
    User, Product, Category, Cart, CartItem, Order, OrderItem,
    Review, WishList, DiscountCode, ContactMessage
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from sqlalchemy import select

bp = Blueprint('main',__name__)

# --------------- Public And Home routes -----------------------------------------
@bp.route('/')
def index():
    #Get Featured product first(6)
    featured_products = Product.query.filter_by(is_active=True).limit(6).all()

    return render_template('index.html', featured_products=featured_products,page_title='Home - Aura By Honeyyy')

@bp.route('/shop')
def shop():
    # for get the parameter from the url
    url_params = request.args.get("category",type=int)

    #get all active products
    products = Product.query.filter_by(is_active=True).all()

    #get all categories
    categories = Category.query.all()

    # filter by the parameters
    if url_params:
        products = Product.query.filter(Product.category_id == url_params).all()

    return render_template('shop.html',products=products, categories=categories,page_title='Shop - Aura by Honeyy')

@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    
    product = db.session.get(Product, int(product_id))

    reviews = Review.query.filter_by(product_id=product_id).all()

    similar_products = Product.query.filter(Product.category_id == product.category_id, Product.id != product_id).limit(3).all()

    return render_template('product_detail.html', product=product, reviews=reviews, similar_products=similar_products, page_title=f"{product.name} - Aura by Honeyy")

@bp.route('/about')
def about():
    return render_template('about.html',page_title='About Us - Aura By Honeyy')


# ----------------------------- Authentication Routes -----------------------------------
@bp.route('/register', methods=['GET','POST'])
def register():
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        #validation
        if not username or not email or not password:
            return render_template('register.html', error='All Fields are required')

        if password != confirm_password:
            return render_template('register.html', error='Password do not match')
        
        #check if user exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html',error='User already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already exists')
        
        #create new user 
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        #create cart for new user
        new_cart = Cart(user_id=new_user.id)
        db.session.add(new_cart)
        db.session.commit()

        return redirect (url_for('main.login'))
    return render_template('register.html',page_title='Register - Aura By Honeyy')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        #find user
        user = User.query.filter_by(username=username).first()

        #verify password
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin

            return redirect(url_for('main.shop'))
        else:
            return render_template('login.html',error='Invalid Username and Password')
        
    return render_template('login.html', page_title='Login - Aura By Honeyy')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

# --------------------------------Shopping cart routes ------------------------------------
@bp.route('/cart')
def view_cart():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        cart_items = []
        total = 0
    else:
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
        total = sum(item.price * item.quantity for item in cart_items if len(cart_items) > 0)

    return render_template('cart.html', cart_items=cart_items, total=total, page_title='Shopping Cart - Aura By Honeyy')

@bp.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    quantity = request.form.get('quantity', 1, type=int)

    user_id = session['user_id']
    cart = Cart.query.filter_by(user_id=user_id).first()
    product = Product.query.get_or_404(product_id)

    print(user_id)

    if product:
        product_price = product.price

    #create cart
    if not cart:
        cart = Cart(user_id=user_id,quantity=quantity,price=product_price)
        db.session.add(cart)
    
    db.session.commit()

    #check if product already in cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            cart_id = cart.id,
            product_id=product_id,
            quantity=quantity,
            price=product_price
        )
        db.session.add(cart_item)
    db.session.commit()

    # update the 
    return redirect(url_for('main.view_cart'))
    
@bp.route('/cart/remove/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    db.session.delete(cart_item)
    db.session.commit()
    
    return redirect(url_for('main.view_cart'))

@bp.route('/cart/update/<int:cart_item_id>', methods=['POST'])
def update_cart_item(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity > 0:
        cart_item.quantity = quantity
    else:
        db.session.delete(cart_item)

    db.session.commit()
    return redirect(url_for('main.view_cart'))

# ---------------------- product interaction cart -------------------------------
@bp.route('/product/<int:product_id>/review', methods=['POST'])
def add_review(product_id):
    """Add product review"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment')

    # find the user first in the database with the same product_id
    existingReviewUser = Review.query.filter(user_id == user_id, product_id == product_id).first()

    if existingReviewUser:
        flash("Review already submitted", "danger")
        return redirect(url_for('main.product_detail', product_id=product_id))
    else:
        review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        comment=comment,
        is_verified=True
    )
    
    db.session.add(review)
    db.session.commit()
    
    return redirect(url_for('main.product_detail', product_id=product_id))

@bp.route('/product/<int:product_id>/wishlist', methods=['POST'])
def toggle_wishlist(product_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    
    # Check if already in wishlist
    wish = WishList.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()
    
    if wish:
        # Remove from wishlist
        db.session.delete(wish)
    else:
        # Add to wishlist
        wish = WishList(user_id=user_id, product_id=product_id)
        db.session.add(wish)
    
    db.session.commit()
    return redirect(url_for('main.product_detail', product_id=product_id))

# ------------------------ contact route -----------------------------------

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        contact_msg = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        
        db.session.add(contact_msg)
        db.session.commit()
        
        return render_template(
            'contact.html',
            success='Message sent successfully!',
            page_title='Contact Us - Aura by Honeyy'
        )
    
    return render_template(
        'contact.html',
        page_title='Contact Us - Aura by Honeyy'
    )

# --------------------------------------- Handles Errors --------------------------------------

@bp.errorhandler(404)
def not_found(error):
    """404 error page"""
    return render_template('404.html', page_title='Page Not Found'), 404


@bp.errorhandler(500)
def server_error(error):
    """500 error page"""
    return render_template('500.html', page_title='Server Error'), 500

# -------------------------------------Checkout and orders ----------------------------------
@bp.route('/checkout', methods=['GET','POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        user_id = session['user_id']
        user = User.query.get(user_id)
        cart = Cart.query.filter_by(user_id=user_id).first()

        if not cart:
            return redirect(url_for('main.view_cart'))
        
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()

        if not cart_items:
            return redirect(url_for('main.view_cart'))
        
        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        #create order
        order = Order(
            user_id=user_id,
            order_number=f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            total_amount=total_amount,
            final_amount=total_amount,
            shipping_address=request.form.get('address'),
            status='pending'
        )

        db.session.add(order)
        db.session.commit()

        #Add order item
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)
        db.session.commit()

        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        return redirect(url_for('main.order_success', order_id=order.id))
    
    user_id = session['user_id']
    cart = Cart.query.filter_by(user_id=user_id).first()
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all() if cart else []
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    return render_template(
        'checkout.html',
        cart_items=cart_items,
        total=total,
        page_title='Checkout - Aura by Honeyy'
    )

@bp.route('/order_success/<int:order_id>')
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    order_item = OrderItem.query.filter_by(order_id=order_id).all()

    return render_template('order_success.html', order=order, order_item=order_item, page_title='Order Confirmed - Aura By Honeyy')

@bp.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    return render_template('orders.html', orders=orders, order_len=len(orders), product_details=orders, page_title='My Orders - Aura By Honeyy')