from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from app import db
from app.models import (
    User, Product, Category, Order, OrderItem, Review, 
    AdminLog, SalesReport, StockHistory, ProductAnalytics, Refund
)
 
# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
 
# --------------- ADMIN ONLY DECORATOR ---------------
def admin_required(f):
    """Check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied! Admin only.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
 
 
# ------------ HELPER FUNCTION --------------
def log_admin_action(action, entity_type, entity_id, description):
    """Log admin action to AdminLog"""
    try:
        log = AdminLog(
            admin_id=current_user.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging admin action: {e}")
 
 
# ----------------- DASHBOARD -----------------
 
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with key metrics"""
    
    # Get today's date
    today = datetime.now().date()
    
    # Get today's sales report
    today_sales = SalesReport.query.filter_by(report_date=today).first()
    
    if today_sales:
        total_orders = today_sales.total_orders
        total_revenue = today_sales.total_revenue
        items_sold = today_sales.total_items_sold
    else:
        # Calculate if not in database
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        orders = Order.query.filter(
            Order.created_at >= today_start,
            Order.created_at <= today_end
        ).all()
        
        total_orders = len(orders)
        total_revenue = sum(o.final_amount for o in orders)
        items_sold = sum(len(o.order_items) for o in orders)
    
    # Get total products
    total_products = Product.query.count()
    
    # Get total customers
    total_customers = User.query.filter_by(is_admin=False).count()
    
    # Get recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Get top products
    top_products = db.session.query(Product, ProductAnalytics).join(
        ProductAnalytics, Product.id == ProductAnalytics.product_id
    ).order_by(ProductAnalytics.units_sold.desc()).limit(5).all()
    
    # Get low stock products
    low_stock = Product.query.filter(Product.stock < 10).all()
    
    return render_template('admin/dashboard.html',
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         items_sold=items_sold,
                         total_products=total_products,
                         total_customers=total_customers,
                         recent_orders=recent_orders,
                         top_products=top_products,
                         low_stock=low_stock)
 
 
# ---------------- PRODUCTS MANAGEMENT ------------------
 
@admin_bp.route('/products')
@login_required
@admin_required
def products():
    """List all products"""
    page = request.args.get('page', 1, type=int)
    products_list = Product.query.paginate(page=page, per_page=10)
    return render_template('admin/products.html', products=products_list)
 
 
@admin_bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    """Edit product"""
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        # Update product
        product.name = request.form.get('name')
        product.slug = request.form.get('slug')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        product.category_id = int(request.form.get('category_id'))
        product.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        
        # Log action
        log_admin_action('update', 'Product', product_id, f'Updated product: {product.name}')
        
        flash(f'Product {product.name} updated successfully!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/edit_product.html', product=product, categories=categories)
 
 
@admin_bp.route('/product/delete/<int:product_id>')
@login_required
@admin_required
def delete_product(product_id):
    """Delete product"""
    product = Product.query.get_or_404(product_id)
    product_name = product.name
    
    db.session.delete(product)
    db.session.commit()
    
    # Log action
    log_admin_action('delete', 'Product', product_id, f'Deleted product: {product_name}')
    
    flash(f'Product {product_name} deleted successfully!', 'success')
    return redirect(url_for('admin.products'))
 
 
# ----------------- ORDERS MANAGEMENT -----------------
 
@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    """List all orders"""
    page = request.args.get('page', 1, type=int)
    orders_list = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/orders.html', orders=orders_list)
 
 
@admin_bp.route('/order/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    """View order details"""
    order = Order.query.get_or_404(order_id)
    refund = Refund.query.filter_by(order_id=order_id).first()
    
    return render_template('admin/order_detail.html', order=order, refund=refund)
 
 
@admin_bp.route('/order/update-status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    status = request.json.get('status')
    
    valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
    
    if status in valid_statuses:
        order.status = status
        db.session.commit()
        
        # Log action
        log_admin_action('update', 'Order', order_id, f'Updated status to: {status}')
        
        return jsonify({'success': True, 'message': f'Order status updated to {status}'})
    
    return jsonify({'success': False, 'message': 'Invalid status'})
 
 
# ------------------ REFUND MANAGEMENT ------------------
 
@admin_bp.route('/refunds')
@login_required
@admin_required
def refunds():
    """List all refund requests"""
    page = request.args.get('page', 1, type=int)
    refunds_list = Refund.query.order_by(Refund.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/refunds.html', refunds=refunds_list)
 
 
@admin_bp.route('/refund/<int:refund_id>')
@login_required
@admin_required
def refund_detail(refund_id):
    """View refund details"""
    refund = Refund.query.get_or_404(refund_id)
    order = Order.query.get(refund.order_id)
    return render_template('admin/refund_detail.html', refund=refund, order=order)
 
 
@admin_bp.route('/refund/approve/<int:refund_id>', methods=['POST'])
@login_required
@admin_required
def approve_refund(refund_id):
    """Approve refund request"""
    refund = Refund.query.get_or_404(refund_id)
    
    refund.status = 'approved'
    refund.notes = request.json.get('notes', '')
    db.session.commit()
    
    # Log action
    log_admin_action('update', 'Refund', refund_id, f'Approved refund for order {refund.order_id}')
    
    return jsonify({'success': True, 'message': 'Refund approved!'})
 
 
@admin_bp.route('/refund/reject/<int:refund_id>', methods=['POST'])
@login_required
@admin_required
def reject_refund(refund_id):
    """Reject refund request"""
    refund = Refund.query.get_or_404(refund_id)
    
    refund.status = 'rejected'
    refund.notes = request.json.get('notes', '')
    db.session.commit()
    
    # Log action
    log_admin_action('update', 'Refund', refund_id, f'Rejected refund for order {refund.order_id}')
    
    return jsonify({'success': True, 'message': 'Refund rejected!'})
 
 
@admin_bp.route('/refund/process/<int:refund_id>', methods=['POST'])
@login_required
@admin_required
def process_refund(refund_id):
    """Process (complete) refund"""
    refund = Refund.query.get_or_404(refund_id)
    
    refund.status = 'processed'
    refund.processed_at = datetime.now()
    db.session.commit()
    
    # Log action
    log_admin_action('update', 'Refund', refund_id, f'Processed refund of ₹{refund.refund_amount} for order {refund.order_id}')
    
    return jsonify({'success': True, 'message': f'Refund of ₹{refund.refund_amount} processed!'})
 
 
# ---------------- INVENTORY MANAGEMENT ------------------
 
@admin_bp.route('/inventory')
@login_required
@admin_required
def inventory():
    """Inventory management"""
    page = request.args.get('page', 1, type=int)
    
    # Get products with low stock
    products_list = Product.query.all()
    
    # Get stock history
    stock_history = StockHistory.query.order_by(StockHistory.created_at.desc()).limit(20).all()
    
    return render_template('admin/inventory.html', products=products_list, stock_history=stock_history)
 
 
@admin_bp.route('/inventory/adjust-stock/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def adjust_stock(product_id):
    """Adjust product stock"""
    product = Product.query.get_or_404(product_id)
    
    old_quantity = product.stock
    new_quantity = int(request.json.get('quantity'))
    reason = request.json.get('reason', 'Manual adjustment')
    
    # Create stock history
    history = StockHistory(
        product_id=product_id,
        previous_quantity=old_quantity,
        new_quantity=new_quantity,
        change_type='adjustment',
        reason=reason,
        admin_id=current_user.id
    )
    
    # Update product stock
    product.stock = new_quantity
    
    db.session.add(history)
    db.session.commit()
    
    # Log action
    log_admin_action('update', 'Product', product_id, f'Adjusted stock from {old_quantity} to {new_quantity}')
    
    return jsonify({'success': True, 'message': f'Stock updated from {old_quantity} to {new_quantity}'})
 
 
# -------------------- ANALYTICS -------------------
 
@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics and reports"""
    
    # Get sales data for last 7 days
    today = datetime.now().date()
    last_7_days = today - timedelta(days=6)
    
    sales_data = SalesReport.query.filter(
        SalesReport.report_date >= last_7_days,
        SalesReport.report_date <= today
    ).all()
    
    # Get top products by sales
    top_products = db.session.query(
        Product,
        ProductAnalytics
    ).join(
        ProductAnalytics,
        Product.id == ProductAnalytics.product_id
    ).order_by(
        ProductAnalytics.units_sold.desc()
    ).limit(10).all()
    
    # Get products by revenue
    top_revenue = db.session.query(
        Product,
        ProductAnalytics
    ).join(
        ProductAnalytics,
        Product.id == ProductAnalytics.product_id
    ).order_by(
        ProductAnalytics.revenue.desc()
    ).limit(5).all()
    
    return render_template('admin/analytics.html',
                         sales_data=sales_data,
                         top_products=top_products,
                         top_revenue=top_revenue)
 
 
# ---------------- ADMIN LOGS -------------------
 
@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    """View admin action logs"""
    page = request.args.get('page', 1, type=int)
    logs_list = AdminLog.query.order_by(AdminLog.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/logs.html', logs=logs_list)
 
 
# -------------- STATISTICS API ---------------
 
@admin_bp.route('/api/stats')
@login_required
@admin_required
def get_stats():
    """Get dashboard statistics (JSON API)"""
    
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Today's stats
    today_orders = Order.query.filter(
        Order.created_at >= today_start,
        Order.created_at <= today_end
    ).all()
    
    today_revenue = sum(o.final_amount for o in today_orders)
    
    # Total products and customers
    total_products = Product.query.count()
    total_customers = User.query.filter_by(is_admin=False).count()
    
    # Low stock count
    low_stock_count = Product.query.filter(Product.stock < 10).count()
    
    # Pending orders
    pending_orders = Order.query.filter_by(status='pending').count()
    
    # Pending refunds
    pending_refunds = Refund.query.filter_by(status='pending').count()
    
    return jsonify({
        'today_orders': len(today_orders),
        'today_revenue': float(today_revenue),
        'total_products': total_products,
        'total_customers': total_customers,
        'low_stock': low_stock_count,
        'pending_orders': pending_orders,
        'pending_refunds': pending_refunds
    })