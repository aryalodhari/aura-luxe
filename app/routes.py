from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app import db
from app.models import (
    User, Product, Category, Cart, CartItem, Order, OrderItem,
    Review, WishList, DiscountCode, ContactMessage
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

bp = Blueprint('main',__name__)

# --------------- Public And Home routes -----------------------------------------
@bp.route('/')
def index():
    #Get Featured product first(6)
    featured_products = Product.query.filter_by(is_active=True).limit(6).all()

    return render_template('index.html', featured_products=featured_products,page_title='Home - Aura By Honeyyy')

@bp.route('/shop')
def shop():
    #get all active products
    products = Product.query.filter_by(is_active=True).all()

    #get all categories
    categories = Category.query.all()

    return render_template('shop.html',products=products, categories=categories,page_title='Shop - Aura by Honeyy')

@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    
    product = Product.query.get_or_404(product_id)

    reviews = Review.query.filter_by(product_id=product_id).all()

    similar_products = Product.filter(Product.category_id == product.category_id, Product.id != product_id).limit(4).all()

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
        user = User.query.fitler_by(username=username).first()

        #verify password
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin

            return redirect(url_for('main.shop'))
        else:
            return render_template('login.html',error='Invaliud Username and Password')
        
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
        cart_items = Cart.query.filter_by(cart_id=cart.id).all()
        total = sum(item.product.price * item.quantity for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total=total, page_title='Shopping Cart - Aura By Honeyy')

@bp.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    quantity = request.form.get('quantity', 1, type=int)

    user_id = session['user_id']
    cart = Cart.query.filter_by(user_id=user_id).first()

    #create cart
    if not cart:
        cart = Cart(user_id=user_id)
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
            quantity=quantity
        )
        db.session.add(cart_item)
    db.session.commit()
    return redirect(url_for('main.view_cart'))
    
@bp.route('/cart/remove/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    db.session.delete(cart_item)
    db.session.commit()
    
    return redirect(url_for('main.view_cart'))

@bp.route('/cart/update/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
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