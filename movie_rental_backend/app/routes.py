# # app/routes.py
# from flask import jsonify
# from . import db
# from .models import Movie
# from flask import current_app as app # Import the 'app' instance

# @app.route('/')
# def index():
#     return "Welcome to the Movie Rental API! 🍿"

# # Endpoint to get all movies
# @app.route('/api/movies', methods=['GET'])
# def get_movies():
#     try:
#         movies = Movie.query.all()
#         movie_list = [
#             {
#                 'id': movie.id,
#                 'title': movie.title,
#                 'description': movie.description
#             } for movie in movies
#         ]
#         return jsonify(movie_list), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    
#     # In app/routes.py

# # ... other imports ...
# from .models import Movie, Customer # Make sure Customer is imported

# # ... other routes like get_movie_by_id ...


# # Endpoint to get all customers
# @app.route('/api/customers', methods=['GET'])
# def get_customers():
#     customers = Customer.query.all()
#     customer_list = []
#     for customer in customers:
#         customer_data = {
#             'id': customer.id,
#             'first_name': customer.first_name,
#             'last_name': customer.last_name,
#             'email': customer.email,
#             'phone': customer.phone
#         }
#         customer_list.append(customer_data)
        
#     return jsonify(customer_list)





# # app/routes.py

# # Add 'request' to your imports from flask

# from .models import Movie, Customer # Make sure to import the Customer model

# # ... your existing routes like index() and get_movies() are here ...


# # Endpoint to create a new customer
# @app.route('/api/customers', methods=['POST'])
# def create_customer():
#     # Get the JSON data from the incoming request
#     data = request.get_json()

#     # Basic validation to ensure data was sent and required fields are present
#     if not data or not 'email' in data or not 'first_name' in data:
#         return jsonify({'error': 'Missing required fields: first_name and email'}), 400

#     # Check if a customer with this email already exists
#     if Customer.query.filter_by(email=data['email']).first():
#         return jsonify({'error': 'Customer with this email already exists'}), 409 # 409 Conflict

#     # Create a new Customer object from the data
#     # .get() is used for optional fields like 'last_name' to avoid errors if they are not provided
#     new_customer = Customer(
#         first_name=data['first_name'],
#         last_name=data.get('last_name'),
#         email=data['email'],
#         phone=data.get('phone'),
#         address=data.get('address')
#     )

#     # Add the new customer to the database session
#     db.session.add(new_customer)
#     # Commit the session to permanently save the record
#     db.session.commit()

#     # Return a success message and the ID of the new customer
#     # The HTTP status code 201 means "Created"
#     return jsonify({
#         'message': 'Customer created successfully!',
#         'customer_id': new_customer.id
#     }), 201


# # In app/routes.py

# from flask import jsonify, request
# from . import db
# from .models import Customer, Movie, Genre, Format # Make sure to import all needed models

# # --- CUSTOMER ENDPOINTS ---

# # CREATE a new customer
# @app.route('/api/customers', methods=['POST'])
# def create_customer():
#     data = request.get_json()
#     if not data or not 'email' in data or not 'first_name' in data:
#         return jsonify({'error': 'Missing required fields: first_name and email'}), 400

#     if Customer.query.filter_by(email=data['email']).first():
#         return jsonify({'error': 'Customer with this email already exists'}), 409

#     new_customer = Customer(
#         first_name=data['first_name'],
#         last_name=data.get('last_name'),
#         email=data['email'],
#         phone=data.get('phone'),
#         address=data.get('address')
#     )
#     db.session.add(new_customer)
#     db.session.commit()
#     return jsonify({'message': 'Customer created successfully!', 'customer_id': new_customer.id}), 201

# # READ all customers
# @app.route('/api/customers', methods=['GET'])
# def get_customers():
#     customers = Customer.query.all()
#     return jsonify([{
#         'id': c.id, 'first_name': c.first_name, 'last_name': c.last_name, 'email': c.email
#     } for c in customers])

# # READ a single customer by ID
# @app.route('/api/customers/<int:id>', methods=['GET'])
# def get_customer(id):
#     customer = Customer.query.get_or_404(id)
#     return jsonify({
#         'id': customer.id, 'first_name': customer.first_name, 'last_name': customer.last_name, 
#         'email': customer.email, 'phone': customer.phone, 'address': customer.address
#     })

# # UPDATE a customer by ID
# @app.route('/api/customers/<int:id>', methods=['PUT'])
# def update_customer(id):
#     customer = Customer.query.get_or_404(id)
#     data = request.get_json()

#     customer.first_name = data.get('first_name', customer.first_name)
#     customer.last_name = data.get('last_name', customer.last_name)
#     customer.email = data.get('email', customer.email)
#     customer.phone = data.get('phone', customer.phone)
#     customer.address = data.get('address', customer.address)

#     db.session.commit()
#     return jsonify({'message': 'Customer updated successfully!'})

# # DELETE a customer by ID
# @app.route('/api/customers/<int:id>', methods=['DELETE'])
# def delete_customer(id):
#     customer = Customer.query.get_or_404(id)
#     db.session.delete(customer)
#     db.session.commit()
#     return jsonify({'message': 'Customer deleted successfully!'})



# # In app/routes.py, continued...

# # --- MOVIE ENDPOINTS ---

# # CREATE a new movie
# @app.route('/api/movies', methods=['POST'])
# def create_movie():
#     data = request.get_json()
#     if not data or not 'title' in data or not 'genre_id' in data:
#         return jsonify({'error': 'Missing required fields: title and genre_id'}), 400

#     # Optional: Check if genre and format exist
#     if not Genre.query.get(data['genre_id']):
#         return jsonify({'error': 'Genre not found'}), 404
#     if 'format_id' in data and not Format.query.get(data['format_id']):
#         return jsonify({'error': 'Format not found'}), 404
        
#     new_movie = Movie(
#         title=data['title'],
#         description=data.get('description'),
#         release_year=data.get('release_year'),
#         genre_id=data['genre_id'],
#         format_id=data.get('format_id')
#     )
#     db.session.add(new_movie)
#     db.session.commit()
#     return jsonify({'message': 'Movie created successfully!', 'movie_id': new_movie.id}), 201

# # READ all movies
# @app.route('/api/movies', methods=['GET'])
# def get_movies():
#     movies = Movie.query.all()
#     return jsonify([{
#         'id': m.id, 'title': m.title, 'release_year': m.release_year, 'genre_id': m.genre_id
#     } for m in movies])

# # READ a single movie by ID
# @app.route('/api/movies/<int:id>', methods=['GET'])
# def get_movie(id):
#     movie = Movie.query.get_or_404(id)
#     return jsonify({
#         'id': movie.id, 'title': movie.title, 'description': movie.description,
#         'release_year': movie.release_year, 'genre_id': movie.genre_id, 'format_id': movie.format_id
#     })

# # UPDATE a movie by ID
# @app.route('/api/movies/<int:id>', methods=['PUT'])
# def update_movie(id):
#     movie = Movie.query.get_or_404(id)
#     data = request.get_json()

#     movie.title = data.get('title', movie.title)
#     movie.description = data.get('description', movie.description)
#     movie.release_year = data.get('release_year', movie.release_year)
#     movie.genre_id = data.get('genre_id', movie.genre_id)
#     movie.format_id = data.get('format_id', movie.format_id)

#     db.session.commit()
#     return jsonify({'message': 'Movie updated successfully!'})

# # DELETE a movie by ID
# @app.route('/api/movies/<int:id>', methods=['DELETE'])
# def delete_movie(id):
#     movie = Movie.query.get_or_404(id)
#     db.session.delete(movie)
#     db.session.commit()
#     return jsonify({'message': 'Movie deleted successfully!'})


# app/routes.py

from datetime import datetime, timedelta
from functools import wraps
import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import (
    Movie, Customer, Genre, Format, Inventory,
    Rental, RentalItem, Payment, Staff
)

main = Blueprint('main', __name__)

# -------------------------
# Helper: role extractor and password check
# -------------------------
def _get_role_from_staff(staff):
    """Return a string role from a Staff row whether role is a string or a relationship."""
    if not staff:
        return None
    # if staff.role is a relationship object with .name
    role = getattr(staff, 'role', None)
    if role is None:
        return None
    # if role is object with .name (e.g., Role model)
    role_name = getattr(role, 'name', None)
    if role_name:
        return role_name
    # otherwise assume role is a string
    if isinstance(role, str):
        return role
    # fallback: convert to string
    return str(role)


def _verify_staff_password(staff, plain_password):
    """
    Try staff.check_password if available, otherwise fallback to werkzeug check_password_hash
    assuming staff.password stores a hashed password.
    """
    if staff is None:
        return False
    # Prefer a model-provided check_password method
    if hasattr(staff, 'check_password') and callable(getattr(staff, 'check_password')):
        try:
            return staff.check_password(plain_password)
        except Exception:
            pass
    # Fallback to comparing hashed password (common pattern)
    if hasattr(staff, 'password') and staff.password:
        try:
            return check_password_hash(staff.password, plain_password)
        except Exception:
            pass
    return False

# -------------------------
# Role-check decorator (manager-only)
# -------------------------
def manager_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        import json

        # Ensure there's a valid JWT
        verify_jwt_in_request()

        # Get and decode the identity (JSON string -> dict)
        identity_raw = get_jwt_identity()
        try:
            identity = json.loads(identity_raw) if isinstance(identity_raw, str) else identity_raw
        except Exception:
            return jsonify({'msg': 'Invalid token identity format'}), 400

        # Check if token contains identity
        if not identity:
            return jsonify({'msg': 'Missing identity in token'}), 401

        # Extract role and enforce manager access
        role = identity.get('role')
        if not role or str(role).lower() != 'manager':
            return jsonify({'msg': 'Managers only! Access denied.'}), 403

        # Proceed to the protected route
        return fn(*args, **kwargs)

    return wrapper


# ===========================
# General route
# ===========================
@main.route('/')
def index():
    return "Welcome to the Movie Rental API! 🍿"


# ===========================
# AUTHENTICATION
# ===========================
@main.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    staff_member = Staff.query.filter_by(email=email).first()
    if not staff_member or not _verify_staff_password(staff_member, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # build identity payload
    role = _get_role_from_staff(staff_member) or 'staff'
    identity = {'staff_id': staff_member.id, 'role': role}

    # Create token (expiration optional)
  
    access_token = create_access_token(identity=json.dumps(identity), expires_delta=timedelta(hours=4))
    return jsonify({'access_token': access_token, 'staff_id': staff_member.id, 'role': role})

# # ===========================
# # CUSTOMER AUTHENTICATION
# # ===========================
# @main.route('/api/customer/signup', methods=['POST'])
# def customer_signup():
#     data = request.get_json() or {}
#     first_name = data.get('first_name')
#     last_name = data.get('last_name')
#     email = data.get('email')
#     password = data.get('password')

#     if not all([first_name, last_name, email, password]):
#         return jsonify({'error': 'Missing required fields'}), 400

#     # Check if email already exists
#     if Customer.query.filter_by(email=email).first():
#         return jsonify({'error': 'Email already registered'}), 409

#     # Hash password
#     password_hash = generate_password_hash(password)

#     # Create new customer
#     new_customer = Customer(
#         first_name=first_name,
#         last_name=last_name,
#         email=email
#     )

#     # Assign password hash if model has such column
#     if hasattr(new_customer, 'password_hash'):
#         new_customer.password_hash = password_hash
#     elif hasattr(new_customer, 'password'):
#         new_customer.password = password_hash

#     db.session.add(new_customer)
#     db.session.commit()

#     return jsonify({'message': 'Signup successful! Please log in.'}), 201

# # app/routes.py
# from sqlalchemy.exc import IntegrityError
# from werkzeug.exceptions import BadRequest

# @main.route('/api/customer/signup', methods=['POST'])
# def customer_signup():
#     data = request.get_json() or {}

#     # Validate input early
#     required = ['first_name', 'last_name', 'email', 'password']
#     missing = [f for f in required if not data.get(f)]
#     if missing:
#         return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

#     # Duplicate check (prevents 500 on unique constraint)
#     if Customer.query.filter_by(email=data['email']).first():
#         return jsonify({'error': 'Email already registered'}), 409

#     try:
#         new_customer = Customer(
#             first_name=data['first_name'],
#             last_name=data['last_name'],
#             email=data['email'],
#             phone=data.get('phone'),
#             address=data.get('address'),
#         )

#         # Use model method (avoids AttributeError if method missing)
#         if hasattr(new_customer, 'set_password') and callable(new_customer.set_password):
#             new_customer.set_password(data['password'])
#         else:
#             # fallback if you didn’t add the method yet
#             new_customer.password_hash = generate_password_hash(data['password'])

#         db.session.add(new_customer)
#         db.session.commit()
#         return jsonify({'message': 'Signup successful! Please log in.'}), 201

#     except IntegrityError as ie:
#         db.session.rollback()
#         # Most likely: duplicate email or NOT NULL violation
#         return jsonify({'error': 'Signup failed due to data constraint.', 'details': str(ie.orig)}), 409
#     except BadRequest as br:
#         return jsonify({'error': 'Invalid request payload', 'details': str(br)}), 400
#     except Exception as e:
#         db.session.rollback()
#         # In development, exposing details helps; in prod, log it instead.
#         return jsonify({'error': 'Internal error during signup', 'details': str(e)}), 500

from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

@main.route('/api/customer/signup', methods=['POST'])
def customer_signup():
    data = request.get_json() or {}
    required = ['first_name','last_name','email','password']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    try:
        cust = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address'),
        )
        if hasattr(cust, 'set_password'):
            cust.set_password(data['password'])
        else:
            cust.password_hash = generate_password_hash(data['password'])

        db.session.add(cust)
        db.session.commit()
        return jsonify({'message': 'Signup successful! Please log in.'}), 201

    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({'error': 'Signup failed due to data constraint.', 'details': str(ie.orig)}), 409
    except Exception as e:
        db.session.rollback()
        import traceback
        print("[SIGNUP ERROR]", traceback.format_exc())
        return jsonify({'error': 'Internal error during signup', 'details': str(e)}), 500


# @main.route('/api/customer/login', methods=['POST'])
# def customer_login():
#     data = request.get_json() or {}
#     email = data.get('email')
#     password = data.get('password')

#     if not email or not password:
#         return jsonify({'error': 'Missing email or password'}), 400

#     customer = Customer.query.filter_by(email=email).first()
#     if not customer:
#         return jsonify({'error': 'Customer not found'}), 404

#     # Validate password
#     stored_password = getattr(customer, 'password_hash', None) or getattr(customer, 'password', None)
#     if not stored_password or not check_password_hash(stored_password, password):
#         return jsonify({'error': 'Invalid password'}), 401

#     # Create token (identity can be just the customer ID)
#     access_token = create_access_token(identity=str(customer.id), expires_delta=timedelta(hours=6))

#     return jsonify({
#         'access_token': access_token,
#         'first_name': customer.first_name,
#         'email': customer.email
#     }), 200

@main.route('/api/customer/login', methods=['POST'])
def customer_login():

    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    customer = Customer.query.filter_by(email=email).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    # ✅ Use model method instead of manual hash check
    if not customer.check_password(password):
        return jsonify({'error': 'Invalid password'}), 401

    # ✅ Use structured identity (easy to extend later)
    identity = {'customer_id': customer.id, 'email': customer.email}
    access_token = create_access_token(identity=json.dumps(identity), expires_delta=timedelta(hours=6))

    return jsonify({
        'access_token': access_token,
        'first_name': customer.first_name,
        'email': customer.email
    }), 200



# ===========================
# CUSTOMER CRUD
# ===========================
@main.route('/api/customers', methods=['POST'])
@jwt_required()
def create_customer():
    data = request.get_json() or {}
    if not data or 'email' not in data or 'first_name' not in data:
        return jsonify({'error': 'Missing required fields: first_name and email'}), 400

    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Customer with this email already exists'}), 409

    new_customer = Customer(
        first_name=data['first_name'],
        last_name=data.get('last_name'),
        email=data['email'],
        phone=data.get('phone'),
        address=data.get('address')
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'Customer created successfully!', 'customer_id': new_customer.id}), 201


@main.route('/api/customers', methods=['GET'])
@jwt_required()
def get_customers():
    customers = Customer.query.all()
    return jsonify([{
        'id': c.id,
        'first_name': getattr(c, 'first_name', None) or getattr(c, 'full_name', None),
        'last_name': getattr(c, 'last_name', None),
        'email': c.email,
        'phone': getattr(c, 'phone', None)
    } for c in customers])


@main.route('/api/customers/<int:id>', methods=['GET'])
@jwt_required()
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify({
        'id': customer.id,
        'first_name': getattr(customer, 'first_name', None) or getattr(customer, 'full_name', None),
        'last_name': getattr(customer, 'last_name', None),
        'email': customer.email,
        'phone': getattr(customer, 'phone', None),
        'address': getattr(customer, 'address', None)
    })


@main.route('/api/customers/<int:id>', methods=['PUT'])
@jwt_required()
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json() or {}
    # Support both first_name/full_name patterns
    if 'first_name' in data:
        customer.first_name = data.get('first_name', getattr(customer, 'first_name', None))
    elif 'full_name' in data:
        # map full_name -> first_name if model uses full_name
        if hasattr(customer, 'full_name'):
            customer.full_name = data.get('full_name', customer.full_name)

    # update remaining fields
    if hasattr(customer, 'last_name'):
        customer.last_name = data.get('last_name', getattr(customer, 'last_name', None))
    if 'email' in data:
        customer.email = data.get('email', customer.email)
    if hasattr(customer, 'phone'):
        customer.phone = data.get('phone', getattr(customer, 'phone', None))
    if hasattr(customer, 'address'):
        customer.address = data.get('address', getattr(customer, 'address', None))

    db.session.commit()
    return jsonify({'message': 'Customer updated successfully!'})


@main.route('/api/customers/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully!'})


# ===========================
# GENRES & FORMATS simple endpoints (optional convenience)
# ===========================
@main.route('/api/genres', methods=['GET'])
def list_genres():
    if not hasattr(Genre, 'query'):
        return jsonify([])  # no-op if model not present
    genres = Genre.query.all()
    return jsonify([{'id': g.id, 'name': getattr(g, 'name', None)} for g in genres])


@main.route('/api/formats', methods=['GET'])
def list_formats():
    if not hasattr(Format, 'query'):
        return jsonify([])
    formats = Format.query.all()
    return jsonify([{'id': f.id, 'name': getattr(f, 'name', None)} for f in formats])


# ===========================
# MOVIE CRUD (uses Movie model)
# ===========================
@main.route('/api/movies', methods=['POST'])
@jwt_required()
def create_movie():
    data = request.get_json() or {}
    if not data or 'title' not in data or 'genre_id' not in data:
        return jsonify({'error': 'Missing required fields: title and genre_id'}), 400

    if not Genre.query.get(data['genre_id']):
        return jsonify({'error': 'Genre not found'}), 404

    if 'format_id' in data and data['format_id'] is not None and not Format.query.get(data['format_id']):
        return jsonify({'error': 'Format not found'}), 404

    new_movie = Movie(
        title=data['title'],
        description=data.get('description'),
        release_year=data.get('release_year'),
        genre_id=data['genre_id'],
        format_id=data.get('format_id')
    )
    db.session.add(new_movie)
    db.session.commit()
    return jsonify({'message': 'Movie created successfully!', 'movie_id': new_movie.id}), 201


@main.route('/api/movies', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    return jsonify([{
        'id': m.id,
        'title': m.title,
        'description': m.description,
        'release_year': m.release_year,
        'genre_id': m.genre_id,
        'format_id': getattr(m, 'format_id', None)
    } for m in movies])


@main.route('/api/movies/<int:id>', methods=['GET'])
def get_movie(id):
    movie = Movie.query.get_or_404(id)
    return jsonify({
        'id': movie.id,
        'title': movie.title,
        'description': movie.description,
        'release_year': movie.release_year,
        'genre_id': movie.genre_id,
        'format_id': getattr(movie, 'format_id', None)
    })


@main.route('/api/movies/<int:id>', methods=['PUT'])
@jwt_required()
def update_movie(id):
    movie = Movie.query.get_or_404(id)
    data = request.get_json() or {}
    movie.title = data.get('title', movie.title)
    movie.description = data.get('description', movie.description)
    movie.release_year = data.get('release_year', movie.release_year)
    movie.genre_id = data.get('genre_id', movie.genre_id)
    movie.format_id = data.get('format_id', getattr(movie, 'format_id', None))
    db.session.commit()
    return jsonify({'message': 'Movie updated successfully!'})


@main.route('/api/movies/<int:id>', methods=['DELETE'])
@manager_required
def delete_movie(id):
    """Only managers can delete movies."""
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    return jsonify({'message': 'Movie deleted successfully!'})


# ===========================
# INVENTORY (copies) endpoints
# ===========================
@main.route('/api/inventory', methods=['POST'])
@jwt_required()
def add_to_inventory():
    data = request.get_json() or {}
    if 'movie_id' not in data or 'quantity' not in data:
        return jsonify({'error': 'Missing required fields: movie_id and quantity'}), 400

    movie_id = data['movie_id']
    try:
        quantity = int(data['quantity'])
    except Exception:
        return jsonify({'error': 'Quantity must be an integer'}), 400

    if not Movie.query.get(movie_id):
        return jsonify({'error': 'Movie not found'}), 404

    inventory_item = Inventory.query.filter_by(movie_id=movie_id).first()
    if inventory_item:
        inventory_item.total_copies = (inventory_item.total_copies or 0) + quantity
        inventory_item.available_copies = (inventory_item.available_copies or 0) + quantity
    else:
        inventory_item = Inventory(
            movie_id=movie_id,
            total_copies=quantity,
            available_copies=quantity
        )
        db.session.add(inventory_item)

    db.session.commit()
    return jsonify({
        'message': f'Added {quantity} copies for movie ID {movie_id}. Total available: {inventory_item.available_copies}'
    }), 200


@main.route('/api/inventory', methods=['GET'])
def get_inventory():
    items = Inventory.query.all()
    inventory_list = [{
        'id': item.id,
        'movie_id': item.movie_id,
        'total_copies': item.total_copies,
        'available_copies': item.available_copies
    } for item in items]
    return jsonify(inventory_list)


# ===========================
# RENTALS (create, list, detail)
# ===========================
@main.route('/api/rentals', methods=['POST'])
@jwt_required()
def create_rental():
    data = request.get_json() or {}
    if 'customer_id' not in data or 'inventory_ids' not in data:
        return jsonify({'error': 'Missing required fields: customer_id and inventory_ids'}), 400

    customer_id = data['customer_id']
    inventory_ids = data['inventory_ids']
    if not isinstance(inventory_ids, (list, tuple)) or len(inventory_ids) == 0:
        return jsonify({'error': 'inventory_ids must be a non-empty list'}), 400

    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    # check availability
    for inv_id in inventory_ids:
        inv = Inventory.query.get(inv_id)
        if not inv or (inv.available_copies is None) or inv.available_copies < 1:
            return jsonify({'error': f'Inventory item ID {inv_id} is not available'}), 400

    try:
        identity = get_jwt_identity() or {}
        staff_id = identity.get('staff_id') or 1  # fallback to 1 if authentication is misconfigured

        due_days = int(data.get('rental_days', 7))
        due_date = datetime.utcnow() + timedelta(days=due_days)

        new_rental = Rental(
            customer_id=customer_id,
            rental_date=datetime.utcnow(),
            due_date=due_date,
            staff_id=staff_id
        )
        db.session.add(new_rental)
        db.session.flush()  # get new_rental.id

        # create rental items and reduce available_copies
        for inv_id in inventory_ids:
            rental_item = RentalItem(rental_id=new_rental.id, inventory_id=inv_id)
            db.session.add(rental_item)

            inv = Inventory.query.get(inv_id)
            inv.available_copies = (inv.available_copies or 0) - 1

        db.session.commit()
        return jsonify({'message': 'Rental created successfully!', 'rental_id': new_rental.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create rental.', 'details': str(e)}), 500


@main.route('/api/rentals', methods=['GET'])
@jwt_required()
def get_rentals():
    rentals = Rental.query.all()
    rental_list = [{
        'id': r.id,
        'customer_id': r.customer_id,
        'staff_id': r.staff_id,
        'rental_date': r.rental_date.isoformat() if r.rental_date else None,
        'due_date': r.due_date.isoformat() if r.due_date else None,
        'return_date': r.return_date.isoformat() if r.return_date else None,
        'late_fee': float(r.late_fee) if getattr(r, 'late_fee', None) is not None else 0.0
    } for r in rentals]
    return jsonify(rental_list)


@main.route('/api/rentals/<int:id>', methods=['GET'])
@jwt_required()
def get_rental(id):
    rental = Rental.query.get_or_404(id)
    items_list = [{
        'rental_item_id': it.id,
        'inventory_id': it.inventory_id,
        'returned': bool(it.returned),
        'returned_at': it.returned_at.isoformat() if it.returned_at else None,
        'late_fee': float(it.late_fee) if getattr(it, 'late_fee', None) is not None else 0.0
    } for it in rental.rental_items]
    rental_details = {
        'id': rental.id,
        'customer_id': rental.customer_id,
        'staff_id': rental.staff_id,
        'rental_date': rental.rental_date.isoformat() if rental.rental_date else None,
        'due_date': rental.due_date.isoformat() if rental.due_date else None,
        'return_date': rental.return_date.isoformat() if rental.return_date else None,
        'items': items_list,
        'late_fee': float(rental.late_fee) if getattr(rental, 'late_fee', None) is not None else 0.0
    }
    return jsonify(rental_details)


# ===========================
# RETURNS
# ===========================
@main.route('/api/returns', methods=['POST'])
@jwt_required()
def process_return():
    data = request.get_json() or {}
    if 'rental_item_id' not in data:
        return jsonify({'error': 'Missing required field: rental_item_id'}), 400

    rental_item_id = data['rental_item_id']
    try:
        rental_item = RentalItem.query.get(rental_item_id)
        if not rental_item:
            return jsonify({'error': 'Rental item not found'}), 404
        if rental_item.returned:
            return jsonify({'error': 'This item has already been returned'}), 400

        rental_item.returned = True
        rental_item.returned_at = datetime.utcnow()

        inventory_item = Inventory.query.get(rental_item.inventory_id)
        if inventory_item:
            inventory_item.available_copies = (inventory_item.available_copies or 0) + 1

        # calculate late fee
        parent_rental = Rental.query.get(rental_item.rental_id)
        late_fee = 0.0
        if parent_rental and parent_rental.due_date and rental_item.returned_at > parent_rental.due_date:
            days_late = (rental_item.returned_at - parent_rental.due_date).days
            late_fee = max(0, days_late) * float(request.json.get('late_fee_per_day', 2.0))
            rental_item.late_fee = late_fee
            parent_rental.late_fee = (parent_rental.late_fee or 0.0) + late_fee

        db.session.commit()
        return jsonify({'message': 'Item returned successfully.', 'late_fee_charged': late_fee}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to process return.', 'details': str(e)}), 500


# ===========================
# PAYMENTS
# ===========================
@main.route('/api/payments', methods=['POST'])
@jwt_required()
def create_payment():
    data = request.get_json() or {}
    if 'customer_id' not in data or 'amount' not in data:
        return jsonify({'error': 'Missing required fields: customer_id and amount'}), 400

    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    rental = None
    if 'rental_id' in data and data['rental_id'] is not None:
        rental = Rental.query.get(data['rental_id'])
        if not rental:
            return jsonify({'error': 'Rental not found'}), 404

    try:
        # Accept either 'payment_method' or 'method' naming
        method = data.get('payment_method') or data.get('method') or 'Card'
        # Accept either 'status' or default to 'Completed'
        status = data.get('status', 'Completed')

        new_payment = Payment(
            rental_id=rental.id if rental else None,
            amount=float(data['amount']),
            payment_date=datetime.utcnow(),
            # if model has fields named differently, map to common ones:
            **({'method': method} if 'method' in Payment.__table__.columns else {}),
            **({'payment_method': method} if 'payment_method' in Payment.__table__.columns else {}),
            **({'status': status} if 'status' in Payment.__table__.columns else {})
        )

        # if Payment model doesn't accept extra kwargs, do minimal set
    except Exception:
        # Fallback construction if model columns differ
        try:
            new_payment = Payment(
                rental_id=rental.id if rental else None,
                amount=float(data['amount'])
            )
            # set attributes manually if available
            if hasattr(new_payment, 'payment_date'):
                new_payment.payment_date = datetime.utcnow()
            if hasattr(new_payment, 'method'):
                new_payment.method = data.get('method') or data.get('payment_method') or 'Card'
            if hasattr(new_payment, 'payment_method'):
                new_payment.payment_method = data.get('payment_method') or data.get('method') or 'Card'
            if hasattr(new_payment, 'status'):
                new_payment.status = data.get('status', 'Completed')
        except Exception as e2:
            return jsonify({'error': 'Failed to construct Payment object', 'details': str(e2)}), 500

    try:
        db.session.add(new_payment)
        db.session.commit()
        return jsonify({'message': 'Payment recorded successfully!', 'payment_id': new_payment.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to record payment.', 'details': str(e)}), 500


@main.route('/api/payments', methods=['GET'])
@jwt_required()
def get_payments():
    payments = Payment.query.all()
    result = []
    for p in payments:
        result.append({
            'id': p.id,
            'rental_id': getattr(p, 'rental_id', None),
            'amount': float(getattr(p, 'amount', 0)),
            'payment_date': getattr(p, 'payment_date', None).isoformat() if getattr(p, 'payment_date', None) else None,
            'status': getattr(p, 'status', None) or getattr(p, 'payment_method', None) or getattr(p, 'method', None)
        })
    return jsonify(result)


@main.route('/api/payments/customer/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer_payments(customer_id):
    if not Customer.query.get(customer_id):
        return jsonify({'error': 'Customer not found'}), 404

    # Payment model may or may not have customer_id - if not, find payments via rentals
    if 'customer_id' in Payment.__table__.columns:
        payments = Payment.query.filter_by(customer_id=customer_id).all()
    else:
        rentals = Rental.query.filter_by(customer_id=customer_id).all()
        rental_ids = [r.id for r in rentals]
        payments = Payment.query.filter(Payment.rental_id.in_(rental_ids)).all() if rental_ids else []

    if not payments:
        return jsonify([])

    return jsonify([{
        'id': p.id,
        'rental_id': getattr(p, 'rental_id', None),
        'amount': float(getattr(p, 'amount', 0)),
        'payment_date': getattr(p, 'payment_date', None).isoformat() if getattr(p, 'payment_date', None) else None,
        'status': getattr(p, 'status', None) or getattr(p, 'payment_method', None) or getattr(p, 'method', None)
    } for p in payments])


# In app/routes.py
# Make sure to import the MovieReview model at the top
from .models import MovieReview # ... and your other models

# ... your other routes ...

# ===================================================================
# MOVIE REVIEW ENDPOINTS
# ===================================================================

# CREATE a new review for a specific movie
@main.route('/api/movies/<int:movie_id>/reviews', methods=['POST'])
@jwt_required() # A user must be logged in to post a review
def create_review(movie_id):
    # Check if the movie exists
    if not Movie.query.get(movie_id):
        return jsonify({'error': 'Movie not found'}), 404

    data = request.get_json()
    if not data or 'rating' not in data or 'review_text' not in data:
        return jsonify({'error': 'Missing required fields: rating and review_text'}), 400

    # Get the customer's ID from their token
    # NOTE: For this to work, you would need to create a customer login system
    # similar to your staff login. For now, we can hardcode the customer_id.
    # In a real app: identity = get_jwt_identity(); customer_id = identity['customer_id']
    customer_id = 1 # Hardcoded for demonstration

    new_review = MovieReview(
        movie_id=movie_id,
        customer_id=customer_id, 
        rating=data['rating'],
        review_text=data['review_text']
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({'message': 'Review submitted successfully!', 'review_id': new_review.id}), 201

# READ all reviews for a specific movie
@main.route('/api/movies/<int:movie_id>/reviews', methods=['GET'])
def get_reviews_for_movie(movie_id):
    if not Movie.query.get(movie_id):
        return jsonify({'error': 'Movie not found'}), 404

    reviews = MovieReview.query.filter_by(movie_id=movie_id).all()
    
    return jsonify([{
        'id': review.id,
        'customer_id': review.customer_id,
        'rating': review.rating,
        'review_text': review.review_text,
        'review_date': review.review_date.isoformat()
    } for review in reviews])


# In app/routes.py
# Make sure these models are imported at the top of your file
from .models import Staff, Role, Genre, Format, MembershipTier # ... and your other models

# ... your other existing routes ...

# ===================================================================
# ADMINISTRATIVE MANAGEMENT ENDPOINTS (Manager Access Only)
# ===================================================================

# -------------------------
# Staff Management
# -------------------------

@main.route('/api/staff', methods=['POST'])
@manager_required
def create_staff():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data or 'role_id' not in data:
        return jsonify({'error': 'Missing required fields: email, password, role_id'}), 400
    if Staff.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Staff member with this email already exists'}), 409
    new_staff = Staff(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data['email'],
        phone=data.get('phone'),
        role_id=data['role_id']
    )
    new_staff.set_password(data['password'])
    db.session.add(new_staff)
    db.session.commit()
    return jsonify({'message': 'Staff member created successfully', 'staff_id': new_staff.id}), 201

@main.route('/api/staff', methods=['GET'])
@manager_required
def get_staff():
    staff_list = Staff.query.all()
    return jsonify([{'id': s.id, 'first_name': s.first_name, 'last_name': s.last_name, 'email': s.email, 'role_id': s.role_id} for s in staff_list])

@main.route('/api/staff/<int:id>', methods=['GET'])
@manager_required
def get_single_staff(id):
    staff = Staff.query.get_or_404(id)
    return jsonify({'id': staff.id, 'first_name': staff.first_name, 'last_name': staff.last_name, 'email': staff.email, 'phone': staff.phone, 'role_id': staff.role_id})

@main.route('/api/staff/<int:id>', methods=['PUT'])
@manager_required
def update_staff(id):
    staff = Staff.query.get_or_404(id)
    data = request.get_json()
    staff.first_name = data.get('first_name', staff.first_name)
    staff.last_name = data.get('last_name', staff.last_name)
    staff.email = data.get('email', staff.email)
    staff.phone = data.get('phone', staff.phone)
    staff.role_id = data.get('role_id', staff.role_id)
    if 'password' in data:
        staff.set_password(data['password'])
    db.session.commit()
    return jsonify({'message': 'Staff member updated successfully'})

@main.route('/api/staff/<int:id>', methods=['DELETE'])
@manager_required
def delete_staff(id):
    staff = Staff.query.get_or_404(id)
    db.session.delete(staff)
    db.session.commit()
    return jsonify({'message': 'Staff member deleted successfully'})

# -------------------------
# Genre Management
# -------------------------

@main.route('/api/genres', methods=['POST'])
@manager_required
def create_genre():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Missing required field: name'}), 400
    new_genre = Genre(name=data['name'], description=data.get('description'))
    db.session.add(new_genre)
    db.session.commit()
    return jsonify({'message': 'Genre created successfully', 'id': new_genre.id}), 201

@main.route('/api/genres/<int:id>', methods=['PUT'])
@manager_required
def update_genre(id):
    genre = Genre.query.get_or_404(id)
    data = request.get_json()
    genre.name = data.get('name', genre.name)
    genre.description = data.get('description', genre.description)
    db.session.commit()
    return jsonify({'message': 'Genre updated successfully'})

@main.route('/api/genres/<int:id>', methods=['DELETE'])
@manager_required
def delete_genre(id):
    genre = Genre.query.get_or_404(id)
    db.session.delete(genre)
    db.session.commit()
    return jsonify({'message': 'Genre deleted successfully'})

# -------------------------
# Format Management
# -------------------------

@main.route('/api/formats', methods=['POST'])
@manager_required
def create_format():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Missing required field: name'}), 400
    new_format = Format(name=data['name'], description=data.get('description'))
    db.session.add(new_format)
    db.session.commit()
    return jsonify({'message': 'Format created successfully', 'id': new_format.id}), 201

@main.route('/api/formats/<int:id>', methods=['PUT'])
@manager_required
def update_format(id):
    format_item = Format.query.get_or_404(id)
    data = request.get_json()
    format_item.name = data.get('name', format_item.name)
    format_item.description = data.get('description', format_item.description)
    db.session.commit()
    return jsonify({'message': 'Format updated successfully'})

@main.route('/api/formats/<int:id>', methods=['DELETE'])
@manager_required
def delete_format(id):
    format_item = Format.query.get_or_404(id)
    db.session.delete(format_item)
    db.session.commit()
    return jsonify({'message': 'Format deleted successfully'})

# -------------------------
# Role Management
# -------------------------

@main.route('/api/roles', methods=['POST'])
@manager_required
def create_role():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Missing required field: name'}), 400
    new_role = Role(name=data['name'], description=data.get('description'))
    db.session.add(new_role)
    db.session.commit()
    return jsonify({'message': 'Role created successfully', 'id': new_role.id}), 201
    
@main.route('/api/roles', methods=['GET'])
@manager_required
def get_roles():
    roles = Role.query.all()
    return jsonify([{'id': r.id, 'name': r.name} for r in roles])

@main.route('/api/roles/<int:id>', methods=['PUT'])
@manager_required
def update_role(id):
    role = Role.query.get_or_404(id)
    data = request.get_json()
    role.name = data.get('name', role.name)
    role.description = data.get('description', role.description)
    db.session.commit()
    return jsonify({'message': 'Role updated successfully'})

@main.route('/api/roles/<int:id>', methods=['DELETE'])
@manager_required
def delete_role(id):
    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    return jsonify({'message': 'Role deleted successfully'})

# -------------------------
# Membership Tier Management
# -------------------------

@main.route('/api/membership-tiers', methods=['POST'])
@manager_required
def create_membership_tier():
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({'error': 'Missing required fields: name and price'}), 400
    new_tier = MembershipTier(
        name=data['name'],
        description=data.get('description'),
        rental_limit=data.get('rental_limit'),
        rental_period_days=data.get('rental_period_days'),
        price=data['price']
    )
    db.session.add(new_tier)
    db.session.commit()
    return jsonify({'message': 'Membership tier created successfully', 'id': new_tier.id}), 201
    
@main.route('/api/membership-tiers', methods=['GET'])
@jwt_required()
def get_membership_tiers():
    tiers = MembershipTier.query.all()
    return jsonify([{'id': t.id, 'name': t.name, 'price': float(t.price)} for t in tiers])

@main.route('/api/membership-tiers/<int:id>', methods=['PUT'])
@manager_required
def update_membership_tier(id):
    tier = MembershipTier.query.get_or_404(id)
    data = request.get_json()
    tier.name = data.get('name', tier.name)
    tier.description = data.get('description', tier.description)
    tier.rental_limit = data.get('rental_limit', tier.rental_limit)
    tier.rental_period_days = data.get('rental_period_days', tier.rental_period_days)
    tier.price = data.get('price', tier.price)
    db.session.commit()
    return jsonify({'message': 'Membership tier updated successfully'})

@main.route('/api/membership-tiers/<int:id>', methods=['DELETE'])
@manager_required
def delete_membership_tier(id):
    tier = MembershipTier.query.get_or_404(id)
    db.session.delete(tier)
    db.session.commit()
    return jsonify({'message': 'Membership tier deleted successfully'})
