from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

# Single Bcrypt instance for the app
bcrypt = Bcrypt()

# ==============================
#  Core Entities
# ==============================

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    # Relationships
    staff_members = db.relationship('Staff', backref='role', lazy=True)


class MembershipTier(db.Model):
    __tablename__ = 'membership_tiers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    rental_limit = db.Column(db.Integer)
    rental_period_days = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    # Relationships
    customers = db.relationship('Customer', backref='membership_tier', lazy=True)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    membership_tier_id = db.Column(db.Integer, db.ForeignKey('membership_tiers.id'))
    rental_limit = db.Column(db.Integer, default=5)

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    # Auth
    password_hash = db.Column(db.String(255), nullable=True)

    # Relationships
    rentals = db.relationship('Rental', backref='customer', lazy=True)
    reviews = db.relationship('MovieReview', backref='customer', lazy=True)
    payments = db.relationship('Payment', backref='customer', lazy=True)

    # Helpers
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(50))

    # Auth
    password_hash = db.Column(db.String(128), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    # Foreign Keys
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # Relationships
    rentals_processed = db.relationship('Rental', backref='staff', lazy=True)
    inventory_changes = db.relationship('InventoryHistory', backref='staff', lazy=True)

    # Helpers
    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)


class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    # Relationships
    movies = db.relationship('Movie', backref='genre', lazy=True)


class Format(db.Model):
    __tablename__ = 'formats'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    # Relationships
    movies = db.relationship('Movie', backref='format', lazy=True)


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    poster_url = db.Column(db.String(255))
    release_year = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False, default=99.0) 

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    # Foreign Keys
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'))

    # Relationships
    inventory_items = db.relationship('Inventory', backref='movie', lazy=True)
    reviews = db.relationship('MovieReview', backref='movie', lazy=True)
    rental_items = db.relationship('RentalItem', backref='movie', lazy=True)


# ==============================
#  Inventory & History
# ==============================

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    available_copies = db.Column(db.Integer, nullable=False, default=0)
    total_copies = db.Column(db.Integer, nullable=False, default=0)
    last_inventory_change = db.Column(db.DateTime)

    # Foreign Keys
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))

    # Relationships
    history_logs = db.relationship('InventoryHistory', backref='inventory', lazy=True)
    rental_items = db.relationship('RentalItem', backref='inventory', lazy=True)


class InventoryHistory(db.Model):
    __tablename__ = 'inventory_history'
    id = db.Column(db.Integer, primary_key=True)
    change_type = db.Column(db.String(50))
    change_amount = db.Column(db.Integer)
    note = db.Column(db.Text)
    change_date = db.Column(db.DateTime, server_default=func.now())

    # Foreign Keys
    changed_by_staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))


# ==============================
#  Rentals & Payments
# ==============================

class Rental(db.Model):
    __tablename__ = 'rentals'
    id = db.Column(db.Integer, primary_key=True)
    rental_date = db.Column(db.DateTime, nullable=False, server_default=func.now())
    return_date = db.Column(db.DateTime)

    # ✅ FIX APPLIED HERE: Removed conflicting 'default=' parameter.
    due_date = db.Column(db.DateTime, nullable=False)

    late_fee = db.Column(db.Numeric(5, 2), default=0.00)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

    items = db.relationship('RentalItem', backref='rental', lazy=True)
    payments = db.relationship('Payment', backref='rental', lazy=True)


class RentalItem(db.Model):
    __tablename__ = 'rental_items'
    id = db.Column(db.Integer, primary_key=True)
    rental_start = db.Column(db.DateTime, server_default=func.now())
    returned = db.Column(db.Boolean, default=False)
    returned_at = db.Column(db.DateTime, nullable=True)
    late_fee = db.Column(db.Numeric(5, 2))

    # Foreign Keys
    rental_id = db.Column(db.Integer, db.ForeignKey('rentals.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=True)


class PaymentGateway(db.Model):
    __tablename__ = 'payment_gateways'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(100))
    api_key = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, server_default=func.now())
    method = db.Column(db.String(50))
    status = db.Column(db.String(50))

    # Foreign Keys
    rental_id = db.Column(db.Integer, db.ForeignKey('rentals.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    payment_gateway_id = db.Column(db.Integer, db.ForeignKey('payment_gateways.id'))


# ==============================
#  Reviews & External
# ==============================

class MovieReview(db.Model):
    __tablename__ = 'movie_reviews'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)
    review_date = db.Column(db.DateTime, server_default=func.now())

    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))


class ExternalMovieDb(db.Model):
    __tablename__ = 'external_movie_db'
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(255))
    external_db_id = db.Column(db.String(255))
    source = db.Column(db.String(100))
    fetched_at = db.Column(db.DateTime, nullable=True)

    # Foreign Keys
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))