from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from typing import List, Optional

db = SQLAlchemy()

class AuditMixin:
    """
    Mixin class for audit logging. Automatically tracks creation and modification times
    and users for any model that inherits from it.
    """
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

class User(UserMixin, db.Model):
    """User model for authentication and audit logging."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(AuditMixin, db.Model):
    """Product category classification."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Relationships
    products = db.relationship('Product', back_populates='category')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(AuditMixin, db.Model):
    """Product master data."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    manufacturer_code = db.Column(db.String(100))
    internal_code = db.Column(db.String(100), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    minimum_stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    category = db.relationship('Category', back_populates='products')
    batches = db.relationship('Batch', back_populates='product')
    
    __table_args__ = (
        db.Index('idx_product_search', 'name', 'manufacturer_code', 'internal_code'),
    )
    
    def __repr__(self):
        return f'<Product {self.internal_code}: {self.name}>'

class WarehouseArea(AuditMixin, db.Model):
    """Defines different warehouse areas (outside, inside, yard)."""
    __tablename__ = 'warehouse_areas'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Relationships
    shelf_locations = db.relationship('ShelfLocation', back_populates='area')
    
    def __repr__(self):
        return f'<WarehouseArea {self.name}>'

class ShelfLocation(AuditMixin, db.Model):
    """Individual shelf locations within warehouse areas."""
    __tablename__ = 'shelf_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    location_code = db.Column(db.String(50), nullable=False, unique=True)
    area_id = db.Column(db.Integer, db.ForeignKey('warehouse_areas.id'), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    area = db.relationship('WarehouseArea', back_populates='shelf_locations')
    batch_locations = db.relationship('BatchLocation', back_populates='shelf_location')
    
    __table_args__ = (
        db.Index('idx_shelf_location_search', 'location_code'),
    )
    
    def __repr__(self):
        return f'<ShelfLocation {self.location_code}>'

class Batch(AuditMixin, db.Model):
    """Represents a batch of products received."""
    __tablename__ = 'batches'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    batch_number = db.Column(db.String(100), nullable=False)
    received_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    product = db.relationship('Product', back_populates='batches')
    locations = db.relationship('BatchLocation', back_populates='batch')
    
    __table_args__ = (
        db.UniqueConstraint('batch_number', 'product_id', name='uq_batch_number_product'),
    )
    
    def __repr__(self):
        return f'<Batch {self.batch_number}>'

class BatchLocation(AuditMixin, db.Model):
    """Tracks quantity of specific batch at specific shelf location."""
    __tablename__ = 'batch_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    shelf_location_id = db.Column(db.Integer, db.ForeignKey('shelf_locations.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    
    # Relationships
    batch = db.relationship('Batch', back_populates='locations')
    shelf_location = db.relationship('ShelfLocation', back_populates='batch_locations')
    movements = db.relationship('InventoryMovement', back_populates='batch_location')
    
    __table_args__ = (
        db.UniqueConstraint('batch_id', 'shelf_location_id', name='uq_batch_location'),
        db.Index('idx_batch_location_search', 'batch_id', 'shelf_location_id'),
    )
    
    def __repr__(self):
        return f'<BatchLocation {self.batch.batch_number} at {self.shelf_location.location_code}>'

class InventoryMovement(AuditMixin, db.Model):
    """Logs all inventory movements (additions, removals, transfers)."""
    __tablename__ = 'inventory_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_location_id = db.Column(db.Integer, db.ForeignKey('batch_locations.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # 'IN', 'OUT', 'TRANSFER'
    quantity = db.Column(db.Integer, nullable=False)
    reference = db.Column(db.String(100))  # e.g., order number, transfer reference
    notes = db.Column(db.Text)
    
    # For transfers, track the destination
    destination_location_id = db.Column(db.Integer, db.ForeignKey('shelf_locations.id'))
    
    # Relationships
    batch_location = db.relationship('BatchLocation', back_populates='movements')
    destination_location = db.relationship('ShelfLocation', foreign_keys=[destination_location_id])
    
    __table_args__ = (
        db.Index('idx_movement_search', 'movement_type', 'reference'),
    )
    
    def __repr__(self):
        return f'<InventoryMovement {self.movement_type} {self.quantity}>'