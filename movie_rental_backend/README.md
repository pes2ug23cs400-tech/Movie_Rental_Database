Movie Rental Backend API
Description
This project is a complete backend API for a movie rental service, built with Python, Flask, and MySQL. It supports core functionalities like managing customers, movies, inventory, and processing rental transactions.

Technologies Used
Python 3

Flask & Flask-SQLAlchemy

Flask-JWT-Extended & Flask-Bcrypt

MySQL

Postman for testing

Setup and Installation
Clone the repository.

Create and activate a virtual environment:
python -m venv venv
.\venv\Scripts\Activate


Install the required packages (you will need to create a requirements.txt file first by running pip freeze > requirements.txt).
pip install -r requirements.txt

Set up your .env file with your DATABASE_URL.

Run the application:
python run.py

API Endpoints
Authentication
POST /api/login - Logs in a staff member and returns a JWT token.

Customers
POST /api/customers - Creates a new customer.

GET /api/customers - Retrieves a list of all customers.

GET /api/customers/<id> - Retrieves a single customer.

PUT /api/customers/<id> - Updates a customer.

DELETE /api/customers/<id> - Deletes a customer.

Movies
POST /api/movies - Creates a new movie.

GET /api/movies - Retrieves a list of all movies.

GET /api/movies/<id> - Retrieves a single movie.

PUT /api/movies/<id> - Updates a movie.

DELETE /api/movies/<id> - Deletes a movie.

Inventory
POST /api/inventory - Adds a quantity of a specific movie to the inventory.

GET /api/inventory - Retrieves a list of all inventory items.

Rentals & Returns
POST /api/rentals - Creates a new rental transaction for a customer.

GET /api/rentals - Retrieves a list of all rentals.

GET /api/rentals/<id> - Retrieves a single rental with its line items.

POST /api/returns - Processes the return of a single rental item.

Payments
POST /api/payments - Records a new payment for a customer.

GET /api/payments - Retrieves all payment records.

GET /api/payments/customer/<id> - Retrieves all payments for a specific customer.

Administrative Management (Manager Role Required)
Staff: GET, POST, PUT, DELETE at /api/staff and /api/staff/<id>.

Genres: POST, PUT, DELETE at /api/genres and /api/genres/<id>. (GET is public).

Formats: POST, PUT, DELETE at /api/formats and /api/formats/<id>. (GET is public).

Roles: GET, POST, PUT, DELETE at /api/roles and /api/roles/<id>.

Membership Tiers: POST, PUT, DELETE at /api/membership-tiers and /api/membership-tiers/<id>. (GET is public).