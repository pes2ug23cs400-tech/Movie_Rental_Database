from datetime import datetime, timedelta
import logging
import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from . import db
from .models import Customer, Movie, Rental, RentalItem, Payment, MovieReview, Inventory

cust = Blueprint("cust", __name__, url_prefix="/api")

# ======================================
# 🧩 AUTH ROUTES
# ======================================

@cust.route("/customer/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    required_fields = ["first_name", "last_name", "email", "password"]
    if not all(k in data for k in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    if Customer.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    try:
        new_customer = Customer(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password_hash=generate_password_hash(data["password"])
        )
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({"message": "Signup successful!"}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Signup error: {e}")
        return jsonify({"error": "Signup failed", "details": str(e)}), 500


@cust.route("/customer/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
         return jsonify({"error": "Missing email or password"}), 400

    cust_obj = Customer.query.filter_by(email=email).first()

    if not cust_obj or not check_password_hash(cust_obj.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Token stores only string ID
    token = create_access_token(identity=str(cust_obj.id), expires_delta=timedelta(hours=6))

    return jsonify({
        "access_token": token,
        "first_name": cust_obj.first_name,
        "customer_id": cust_obj.id  # ✅ Add this
    }), 


# ======================================
# 🎬 MOVIE CATALOG & REVIEWS
# ======================================

@cust.route("/catalog", methods=["GET"])
def get_catalog():
    try:
        query = request.args.get("q", "").strip().lower()

        # If search query exists, filter by title
        if query:
            movies = Movie.query.filter(Movie.title.ilike(f"%{query}%")).all()
        else:
            movies = Movie.query.all()

        results = []
        for m in movies:
            ratings = [r.rating for r in m.reviews]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            review_count = len(ratings)

            results.append({
                "id": m.id,
                "title": m.title,
                "genre": m.genre.name if hasattr(m, "genre") and m.genre else None,
                "release_year": m.release_year,
                "description": m.description,
                "poster_url": getattr(m, "poster_url", None),
                "rating": round(avg_rating, 1),
                "review_count": review_count,
                "price": float(m.price) if hasattr(m, "price") and m.price is not None else 99.0

            })

        return jsonify(results), 200

    except Exception as e:
        logging.error(f"Catalog error: {e}")
        return jsonify({"error": "Failed to load catalog"}), 500


@cust.route('/movies/<int:movie_id>/reviews', methods=['GET'])
@jwt_required()
def get_movie_reviews(movie_id):
    try:
        reviews = (
            MovieReview.query
            .filter_by(movie_id=movie_id)
            .order_by(MovieReview.review_date.desc())
            .all()
        )

        data = []
        for r in reviews:
            # ✅ Identify reviewer if customer exists
            if r.customer:
                reviewer_name = f"{r.customer.first_name} {r.customer.last_name}".strip()
                reviewer_id = r.customer.id
            else:
                reviewer_name = "Anonymous"
                reviewer_id = None

            data.append({
                "id": r.id,
                "rating": r.rating,
                "comment": r.review_text,
                "date": r.review_date.strftime("%Y-%m-%d") if r.review_date else "Unknown Date",
                "reviewer": reviewer_name,
                "customer_id": reviewer_id  # ✅ Include reviewer’s ID
            })

        return jsonify(data), 200

    except Exception as e:
        logging.error(f"Get reviews error: {e}")
        return jsonify([]), 200


@cust.route("/customer/checkout", methods=["POST"])
@jwt_required()
def checkout():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            user_id = identity.get("customer_id")
        elif isinstance(identity, str) and identity.startswith("{"):
            user_id = json.loads(identity).get("customer_id")
        else:
            user_id = int(identity)

        data = request.get_json() or {}
        movie_ids = data.get("movie_ids", [])
        method = data.get("method", "Card")

        if not movie_ids:
            return jsonify({"error": "No movies selected"}), 400

        #  Check only rentals where items are *not returned*
        active_rentals = (
            db.session.query(RentalItem)
            .join(Rental)
            .filter(
                Rental.customer_id == user_id,
                Rental.return_date.is_(None),
                RentalItem.returned == '0',
                RentalItem.movie_id.in_(movie_ids)
            )
            .all()
        )

        if active_rentals:
            active_movie_ids = [item.movie_id for item in active_rentals]
            return jsonify({"error": f"You already have an active rental for movie ID(s) {active_movie_ids}"}), 409

        # Calculate total
        total = len(movie_ids) * 100.0
        due_date = datetime.utcnow() + timedelta(days=7)

        rental = Rental(
            customer_id=user_id,
            staff_id=1,
            rental_date=datetime.utcnow(),
            due_date=due_date
        )
        db.session.add(rental)
        db.session.flush()

        for mid in movie_ids:
            movie = Movie.query.get(mid)
            if not movie:
                db.session.rollback()
                return jsonify({"error": f"Movie with ID {mid} not found"}), 404

            # Decrease inventory
            inv = Inventory.query.filter_by(movie_id=mid).first()
            if inv and inv.available_copies > 0:
                inv.available_copies -= 1

            db.session.add(RentalItem(rental_id=rental.id, movie_id=mid, returned=False))

        # Create Payment
        payment = Payment(
            customer_id=user_id,
            rental_id=rental.id,
            amount=total,
            method=method,
            status="Completed"
        )
        db.session.add(payment)
        db.session.commit()

        return jsonify({
            "message": f"Rented {len(movie_ids)} movie(s) successfully!",
            "rental_id": rental.id,
            "amount": total
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        logging.error(f"Checkout IntegrityError: {e.orig}")
        return jsonify({"error": "Checkout failed due to data conflict.", "details": str(e.orig)}), 409
    except Exception as e:
        db.session.rollback()
        logging.error(f"Checkout error: {e}")
        return jsonify({"error": "Checkout failed", "details": str(e)}), 500


# @cust.route("/customer/return", methods=["POST"])
# @jwt_required()
# def return_movie():
#     """
#     Return a specific rental item. Closes rental if all items returned.
#     """
#     try:
#         identity = get_jwt_identity()
#         if isinstance(identity, dict):
#             user_id = identity.get("customer_id")
#         elif isinstance(identity, str) and identity.startswith("{"):
#             user_id = json.loads(identity).get("customer_id")
#         else:
#             user_id = int(identity)

#         data = request.get_json() or {}
#         rental_item_id = data.get("rental_item_id")

#         if not rental_item_id:
#             return jsonify({"error": "Missing rental_item_id"}), 400

#         rental_item = RentalItem.query.get(rental_item_id)
#         if not rental_item:
#             return jsonify({"error": "Rental item not found"}), 404
#         if rental_item.returned:
#             return jsonify({"error": "This item has already been returned"}), 400

#         parent_rental = Rental.query.get(rental_item.rental_id)
#         if not parent_rental or parent_rental.customer_id != user_id:
#             return jsonify({"error": "Unauthorized or invalid rental"}), 403

#         # --- Mark item returned ---
#         now = datetime.utcnow()
#         rental_item.returned = True
#         rental_item.returned_at = now

#         # --- Restore inventory ---
#         inv = Inventory.query.filter_by(movie_id=rental_item.movie_id).first()
#         if inv:
#             inv.available_copies = (inv.available_copies or 0) + 1

#         # --- Late Fee Calculation ---
#         late_fee_per_day = float(data.get("late_fee_per_day", 2.0))
#         late_fee = 0.0
#         if parent_rental.due_date and now > parent_rental.due_date:
#             days_late = (now - parent_rental.due_date).days
#             late_fee = max(0, days_late * late_fee_per_day)
#             rental_item.late_fee = late_fee
#             parent_rental.late_fee = (parent_rental.late_fee or 0.0) + late_fee

#         # ✅ --- Close rental if all items returned ---
#         all_returned = all(it.returned for it in parent_rental.items)
#         if all_returned:
#             parent_rental.return_date = now

#         db.session.commit()

#         return jsonify({
#             "message": "Movie returned successfully!",
#             "late_fee_charged": late_fee
#         }), 200

#     except Exception as e:
#         db.session.rollback()
#         logging.error(f"Return error: {e}")
#         return jsonify({"error": "Failed to return movie", "details": str(e)}), 500

@cust.route("/customer/return", methods=["POST"])
@jwt_required()
def return_movie():
    """
    Return a specific rental item. Closes rental if all items returned.
    Late fee is calculated using MySQL fn_calculate_late_fee() if available,
    otherwise fallback to manual (Python) calculation.
    """
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            user_id = identity.get("customer_id")
        elif isinstance(identity, str) and identity.startswith("{"):
            user_id = json.loads(identity).get("customer_id")
        else:
            user_id = int(identity)

        data = request.get_json() or {}
        rental_item_id = data.get("rental_item_id")

        if not rental_item_id:
            return jsonify({"error": "Missing rental_item_id"}), 400

        rental_item = RentalItem.query.get(rental_item_id)
        if not rental_item:
            return jsonify({"error": "Rental item not found"}), 404
        if rental_item.returned:
            return jsonify({"error": "This item has already been returned"}), 400

        parent_rental = Rental.query.get(rental_item.rental_id)
        if not parent_rental or parent_rental.customer_id != user_id:
            return jsonify({"error": "Unauthorized or invalid rental"}), 403

        # --- Mark item returned ---
        now = datetime.utcnow()
        rental_item.returned = True
        rental_item.returned_at = now

        # --- Restore inventory ---
        inv = Inventory.query.filter_by(movie_id=rental_item.movie_id).first()
        if inv:
            inv.available_copies = (inv.available_copies or 0) + 1

        # --- Late Fee Calculation (Function + Fallback) ---
        late_fee = 0.0
        late_fee_per_day = float(data.get("late_fee_per_day", 2.0))

        try:
            # Try database function first
            sql = f"SELECT fn_calculate_late_fee({parent_rental.id}) AS fee;"
            result = db.session.execute(sql).fetchone()
            if result and result[0] is not None:
                late_fee = float(result[0])
            else:
                # fallback if function returned NULL
                raise ValueError("Function returned NULL")

        except Exception as db_err:
            logging.warning(f"MySQL function fn_calculate_late_fee() failed or missing: {db_err}")

            # --- Fallback: Manual Python method ---
            if parent_rental.due_date and now > parent_rental.due_date:
                days_late = (now - parent_rental.due_date).days
                late_fee = max(0, days_late * late_fee_per_day)

        # --- Apply calculated fee ---
        rental_item.late_fee = late_fee
        parent_rental.late_fee = (parent_rental.late_fee or 0.0) + late_fee

        # ✅ --- Close rental if all items returned ---
        all_returned = all(it.returned for it in parent_rental.items)
        if all_returned:
            parent_rental.return_date = now

        db.session.commit()

        return jsonify({
            "message": "Movie returned successfully!",
            "late_fee_charged": late_fee
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Return error: {e}")
        return jsonify({"error": "Failed to return movie", "details": str(e)}), 500



@cust.route("/customer/rentals", methods=["GET"])
@jwt_required()
def my_rentals():
    """
    Return all rentals for the logged-in customer, 
    including movies and rental_item_id (needed for returns).
    """
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            user_id = identity.get("customer_id")
        elif isinstance(identity, str) and identity.startswith("{"):
            user_id = json.loads(identity).get("customer_id")
        else:
            user_id = int(identity)

        rentals = (
            Rental.query.filter_by(customer_id=user_id)
            .order_by(Rental.rental_date.desc())
            .all()
        )

        data = []
        for r in rentals:
            rental_movies = []

            for item in r.items:  # Each RentalItem linked to a Movie
                movie = Movie.query.get(item.movie_id)
                if movie:
                    rental_movies.append({
                        "id": movie.id,
                        "title": movie.title,
                        "poster_url": getattr(movie, "poster_url", None),
                        "genre": movie.genre.name if hasattr(movie, "genre") and movie.genre else "Unknown Genre",
                        "price": float(getattr(movie, "price", 0.0)),
                        "description": getattr(movie, "description", ""),
                        "rental_item_id": item.id,  # ✅ critical for return endpoint
                        "returned": item.returned,
                        "returned_at": item.returned_at.strftime("%Y-%m-%d") if item.returned_at else None,
                    })
                else:
                    rental_movies.append({
                        "title": "Unknown Movie (Deleted)",
                        "poster_url": "https://via.placeholder.com/150?text=Deleted",
                        "rental_item_id": item.id,  # still include to keep backend linkage
                        "returned": item.returned,
                        "returned_at": item.returned_at.strftime("%Y-%m-%d") if item.returned_at else None,
                    })

            # Build rental entry
            data.append({
                "id": r.id,
                "rental_date": r.rental_date.strftime("%Y-%m-%d") if r.rental_date else "N/A",
                "return_date": r.return_date.strftime("%Y-%m-%d") if r.return_date else None,
                "due_date": r.due_date.strftime("%Y-%m-%d") if r.due_date else None,
                "late_fee": float(getattr(r, "late_fee", 0.0)),
                "movies": rental_movies,
            })

        return jsonify(data), 200

    except Exception as e:
        logging.error(f"Rental history error: {e}")
        # Return safe fallback
        return jsonify([]), 200


@cust.route("/customer/payments", methods=["GET"])
@jwt_required()
def payments():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
             user_id = identity.get("customer_id")
        elif isinstance(identity, str) and identity.startswith("{"):
             user_id = json.loads(identity).get("customer_id")
        else:
             user_id = int(identity)

        pays = Payment.query.filter_by(customer_id=user_id).order_by(Payment.payment_date.desc()).all()
        data = [{
            "id": p.id,
            "amount": float(p.amount),
            "method": p.method,
            "status": p.status,
            "payment_date": p.payment_date.strftime("%Y-%m-%d %H:%M") if p.payment_date else None,
            "rental_id": p.rental_id
        } for p in pays]

        return jsonify(data), 200

    except Exception as e:
        logging.error(f"Payment history error: {e}")
        return jsonify({"error": "Failed to load payments"}), 500


# ======================================
# ⭐ POST REVIEW
# ======================================

@cust.route("/customer/review", methods=["POST"])
@jwt_required()
def add_review():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
             user_id = identity.get("customer_id")
        elif isinstance(identity, str) and identity.startswith("{"):
             user_id = json.loads(identity).get("customer_id")
        else:
             user_id = int(identity)

        data = request.get_json() or {}
        movie_id = data.get("movie_id")
        rating = data.get("rating")
        comment = data.get("comment", "")

        if not (movie_id and rating):
            return jsonify({"error": "Movie ID and rating required"}), 400
        
        if not Movie.query.get(movie_id):
             return jsonify({"error": "Movie not found"}), 404

        review = MovieReview(
            customer_id=user_id,
            movie_id=movie_id,
            rating=rating,
            review_text=comment
        )
        db.session.add(review)
        db.session.commit()

        return jsonify({"message": "Review added successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Add review error: {e}")
        return jsonify({"error": "Failed to post review", "details": str(e)}), 500
    


@cust.route("/customer/review/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review(review_id):
    """Allow a customer to delete their own review."""
    try:
        # --- Identify the logged-in user ---
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            user_id = identity.get("customer_id")
        elif isinstance(identity, str) and identity.startswith("{"):
            user_id = json.loads(identity).get("customer_id")
        else:
            user_id = int(identity)

        # --- Fetch the review ---
        review = MovieReview.query.get(review_id)
        if not review:
            return jsonify({"error": "Review not found"}), 404

        # --- Check ownership ---
        if review.customer_id != user_id:
            return jsonify({"error": "You can only delete your own reviews"}), 403

        # --- Delete the review ---
        db.session.delete(review)
        db.session.commit()

        return jsonify({"message": "Review deleted successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete review error: {e}")
        return jsonify({"error": "Failed to delete review", "details": str(e)}), 500

# ======================================
# 🧠 DEBUG ROUTE
# ======================================

@cust.route("/customer/debug_identity", methods=["GET"])
@jwt_required()
def debug_identity():
    identity = get_jwt_identity()
    return jsonify({
        "identity_raw": identity,
        "identity_type": type(identity).__name__
    }), 200


from sqlalchemy import text

@cust.route("/customer/late_fee/<int:rental_id>", methods=["GET"])
@jwt_required()
def get_late_fee(rental_id):
    """
    Safely calls fn_calculate_late_fee(rental_id) from MySQL.
    Returns 0.00 if rental has no return date or calculation fails.
    """
    try:
        sql = text("SELECT fn_calculate_late_fee(:rental_id) AS fee;")
        result = db.session.execute(sql, {"rental_id": rental_id}).fetchone()

        if not result or result[0] is None:
            logging.warning(f"fn_calculate_late_fee({rental_id}) returned NULL or no data.")
            return jsonify({
                "rental_id": rental_id,
                "late_fee": 0.00,
                "note": "No return date or not yet due."
            }), 200

        fee = float(result[0])
        return jsonify({"rental_id": rental_id, "late_fee": fee}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Late fee fetch error: {e}")
        return jsonify({
            "error": "Failed to calculate late fee",
            "details": str(e)
        }), 500
