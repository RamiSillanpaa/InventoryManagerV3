# app/views/main.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from ..models import Product, Batch, BatchLocation, ShelfLocation, WarehouseArea, db

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def dashboard():
    """Main dashboard with inventory overview."""
    # Total number of unique products
    total_products = Product.query.count()
    
    # Total inventory quantity
    total_inventory = db.session.query(
        func.sum(BatchLocation.quantity)
    ).scalar() or 0
    
    # Low stock products
    low_stock_products = db.session.query(Product).join(Batch).join(BatchLocation)\
        .group_by(Product)\
        .having(func.sum(BatchLocation.quantity) < Product.minimum_stock)\
        .all()
    
    # Recent batches
    recent_batches = Batch.query.order_by(Batch.received_date.desc()).limit(5).all()
    
    # Warehouse areas
    warehouse_areas = WarehouseArea.query.all()
    
    return render_template(
        'main/dashboard.html', 
        total_products=total_products,
        total_inventory=total_inventory,
        low_stock_products=low_stock_products,
        recent_batches=recent_batches,
        warehouse_areas=warehouse_areas
    )

@bp.route('/search', methods=['GET'])
@login_required
def search():
    """Global search functionality."""
    query = request.args.get('q', '')
    
    # Search across different models
    products = Product.query.filter(
        db.or_(
            Product.name.ilike(f'%{query}%'),
            Product.internal_code.ilike(f'%{query}%'),
            Product.manufacturer_code.ilike(f'%{query}%')
        )
    ).all()
    
    batches = Batch.query.filter(
        db.or_(
            Batch.batch_number.ilike(f'%{query}%')
        )
    ).all()
    
    shelf_locations = ShelfLocation.query.filter(
        ShelfLocation.location_code.ilike(f'%{query}%')
    ).all()
    
    return render_template(
        'main/search_results.html',
        query=query,
        products=products,
        batches=batches,
        shelf_locations=shelf_locations
    )