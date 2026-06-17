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
