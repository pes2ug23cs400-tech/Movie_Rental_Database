from app import create_app, db
from app.models import Staff, Role

# Create an app context to interact with the database
app = create_app()
with app.app_context():
    # --- Define your first staff member ---
    STAFF_EMAIL = "manager@example.com"
    STAFF_PASSWORD = "securepassword123" # Change this password
    STAFF_ROLE = "Manager"

    # --- Check if the role exists, create if not ---
    role = Role.query.filter_by(name=STAFF_ROLE).first()
    if not role:
        print(f"Role '{STAFF_ROLE}' not found. Creating it...")
        role = Role(name=STAFF_ROLE, description="Full administrative access.")
        db.session.add(role)
        db.session.commit()
        print("Role created.")

    # --- Check if the staff member already exists ---
    if Staff.query.filter_by(email=STAFF_EMAIL).first():
        print(f"Staff member with email {STAFF_EMAIL} already exists.")
    else:
        # --- Create the new staff member ---
        print("Creating new manager staff member...")
        new_staff = Staff(
            first_name="Admin",
            last_name="User",
            email=STAFF_EMAIL,
            role_id=role.id
        )
        # Set the password (this will hash it)
        new_staff.set_password(STAFF_PASSWORD)
        
        # Add to database and commit
        db.session.add(new_staff)
        db.session.commit()
        print("Staff member created successfully!")
        print(f"Email: {STAFF_EMAIL}")
        print(f"Password: {STAFF_PASSWORD}")