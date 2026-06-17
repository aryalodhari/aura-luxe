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