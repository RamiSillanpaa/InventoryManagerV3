# app/schemas.py
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from .models import Product, Batch, InventoryMovement

class ProductSchema(SQLAlchemySchema):
    class Meta:
        model = Product
        load_instance = True
    
    id = auto_field()
    name = auto_field()
    description = auto_field()
    manufacturer_code = auto_field()
    internal_code = auto_field()
    category_id = auto_field()

class BatchSchema(SQLAlchemySchema):
    class Meta:
        model = Batch
        load_instance = True
    
    id = auto_field()
    product_id = auto_field()
    batch_number = auto_field()
    received_date = auto_field()
    notes = auto_field()

class InventoryMovementSchema(SQLAlchemySchema):
    class Meta:
        model = InventoryMovement
        load_instance = True
    
    id = auto_field()
    batch_location_id = auto_field()
    movement_type = auto_field()
    quantity = auto_field()
    reference = auto_field()
    notes = auto_field()