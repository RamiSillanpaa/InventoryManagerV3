# app/views/api.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from marshmallow import ValidationError
from ..models import Product, Batch, BatchLocation, ShelfLocation, InventoryMovement, db
from ..schemas import ProductSchema, BatchSchema, InventoryMovementSchema

bp = Blueprint('api', __name__)

@bp.route('/products', methods=['GET', 'POST'])
@login_required
def manage_products():
    product_schema = ProductSchema()
    
    if request.method == 'GET':
        products = Product.query.all()
        return jsonify(product_schema.dump(products, many=True))
    
    if request.method == 'POST':
        try:
            data = product_schema.load(request.json)
            product = Product(**data)
            product.created_by = current_user
            product.updated_by = current_user
            db.session.add(product)
            db.session.commit()
            return jsonify(product_schema.dump(product)), 201
        except ValidationError as err:
            return jsonify(err.messages), 400

@bp.route('/inventory/move', methods=['POST'])
@login_required
def move_inventory():
    movement_schema = InventoryMovementSchema()
    
    try:
        data = movement_schema.load(request.json)
        # Implement inventory movement logic here
        movement = InventoryMovement(**data)
        movement.created_by = current_user
        movement.updated_by = current_user
        db.session.add(movement)
        db.session.commit()
        return jsonify(movement_schema.dump(movement)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
