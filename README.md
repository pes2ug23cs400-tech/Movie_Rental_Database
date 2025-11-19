
# 🎬 Movie Rental Database

This project is a complete Movie Rental Management System that includes both a **backend system** and a **frontend interface** to manage movie rentals, customers, and staff using a database-driven architecture.

---

## **Project Structure**

```
Movie_Rental_Database/
│── customer_frontend.py        # Customer CLI frontend
│── frontend.py                 # Staff/admin CLI frontend
│── Movie Rental Database.sql   # SQL schema for database
│── movie_rental_backend/       # Flask backend server
│   │── run.py                  # Backend entry point
│   │── create_staff.py         # Script to create staff users
│   │── app/
│   │   │── models.py           # DB models
│   │   │── routes.py           # Staff routes
│   │   │── routes_customer.py  # Customer routes
│   │   │── __init__.py
│   │── migrations/             # DB migration files
│   │── .env.example
```

---

## 🚀 **How to Run**

### **1️⃣ Setup Database**
Import the SQL file into your RDBMS:

```bash
mysql -u root -p < "Movie Rental Database.sql"
```

OR use any GUI tool (MySQL Workbench, phpMyAdmin, etc.)

---

### **2️⃣ Setup Backend**

Install dependencies:

```bash
cd movie_rental_backend
pip install -r requirements.txt
```

Copy environment file:

```bash
cp .env.example .env
```

Run the server:

```bash
cd .\movie_rental_backend\      
.\venv\Scripts\python.exe run.py  
```

---

### **3️⃣ Run Frontend (CLI)**

#### **For Staff/Admin:**
```bash
streamlit run frontend.py
```

#### **For Customers:**
```bash
streamlit run customer_frontend.py
```

---

## 🛠 **Tech Stack Used**

| Component | Technology |
|----------|------------|
| Backend API | Flask (Python) |
| Database | MySQL |
| Auth & Users | Custom scripts & SQL tables |
| Interface | Python CLI & Flask endpoints |

---

## 📂 **Features**

✔ Add & manage movies  
✔ Register customers  
✔ Staff authentication  
✔ Rent and return movies  
✔ View rental history  

---

## 🧑‍💻 Contributors

This project was created for learning purposes and can be extended further with web UI, JWT auth, or admin dashboards.

---

## 📜 License

This project is open-source and free to modify.

