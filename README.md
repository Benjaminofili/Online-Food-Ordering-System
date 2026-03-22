# 🍔 RegFood – Online Food Ordering System

A full-featured, production-ready web application for ordering food from local restaurants. Built with **Python + Flask** on the backend and a rich, responsive Bootstrap/HTML5 frontend.

[![Deploy Status](https://img.shields.io/badge/Deployed%20On-Render.com-blue?logo=render)](https://render.com)
[![Python](https://img.shields.io/badge/Python-3.14-yellow?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue?logo=postgresql)](https://postgresql.org)

---

## ✨ Features

### 🧑‍💼 Customer Portal
- **Restaurant Discovery** — Browse and search all restaurants with category & food-type filters.
- **Dish Details** — Full dish page with image gallery, size/option selectors, and real-time price calculation.
- **Add to Cart / Wishlist** — AJAX-powered cart with seamless UI updates (no page reload).
- **Checkout with Coupons** — Apply coupon codes for percent or fixed discounts at checkout.
- **Order Tracking** — View all orders with status updates and printable invoices.
- **Ratings & Reviews** — Leave a verified review only after a completed delivery.
- **Digital Menu** — Dedicated tab on the restaurant page to view, preview, and download the restaurant's uploaded menu PDF/image.
- **Customer Dashboard** — Manage profile, addresses, orders, wishlist, and change password from a single hub.

### 👨‍🍳 Restaurant Owner Portal
- **Dashboard Analytics** — Visual charts for revenue, daily orders, and top-selling items.
- **Dish Management** — Add, edit, and toggle dish availability with full image upload support (Cloudinary).
- **Menu Upload** — Upload a high-resolution digital copy of their physical menu for customers to download.
- **Order Management** — View incoming orders with delivery time countdown and update order statuses.
- **Coupon Management** — Create and manage time-limited promotional coupons.
- **Customer Reviews** — Dedicated reviews dashboard to read all customer feedback.
- **Profile Management** — Update restaurant info, logo, and owner contact details.

### 🔑 Admin Portal
- **System Dashboard** — Overview of total users, restaurants, orders, and revenue.
- **Restaurant Management** — Approve, review, and manage all registered restaurants.
- **Customer Management** — View all registered users with full profile details.
- **Category & Food-Type Management** — Add and delete food categories (e.g. Biryani, Burger) and food types (Veg/Non-Veg).
- **Order Reports** — Generate and export PDF reports for orders by restaurant or customer.
- **Food-Type Approval** — Review and approve custom food types suggested by restaurant owners.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask 3.1 |
| **Database (Production)** | PostgreSQL via Render |
| **Database (Development)** | SQLite |
| **ORM** | SQLAlchemy 2.0 + Flask-Migrate (Alembic) |
| **Auth** | Flask-Login, Werkzeug password hashing |
| **Forms** | Flask-WTF, WTForms |
| **Image Uploads** | Cloudinary |
| **Web Server** | Gunicorn |
| **Frontend** | Bootstrap 4, HTML5, Vanilla JS |
| **CSS Extras** | Font Awesome, WOW.js, DataTables.js, Chart.js |
| **Hosting** | Render.com (Web Service + PostgreSQL + Cron Job) |

---

## 🗄️ Database Schema

The application uses the following core models:

```
User          – All users (customer / owner / admin roles)
Restaurant    – Restaurant profiles linked to owner users
RestaurantMedia – Digital menus uploaded by owners
Category      – Food categories (e.g., Biryani, Burger)
FoodType      – Dietary types (e.g., Veg, Non-Veg)
Dish          – Menu items linked to a restaurant and category
Order         – Customer orders with delivery address & time
OrderItem     – Line items within each order
Coupon        – Promotional discount codes
Review        – Customer reviews (one per restaurant, per customer)
Wishlist      – Saved favourite dishes
```

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.10+
- Git
- A Cloudinary account (for image uploads)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/Online-Food-Ordering-System.git
cd Online-Food-Ordering-System
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root of the project:
```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=         # Leave blank to use SQLite locally
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

### 5. Initialise the Database
```bash
flask db upgrade
```

### 6. Run the Development Server
```bash
flask run
```
The app will be live at **http://127.0.0.1:5000**

---

## ☁️ Render.com Deployment

### Step 1: Create a PostgreSQL Database on Render
1. Go to [render.com](https://render.com) and click **New → Postgres**.
2. Choose a name (e.g., `regfood-db`) and select the **Free** tier.
3. After it is created, copy the **Internal Database URL**.

### Step 2: Create a Web Service
1. Click **New → Web Service** and connect your GitHub repository.
2. Set the following configuration:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
   - **Instance Type**: Free

### Step 3: Set Environment Variables
In your Web Service's **Environment** tab, add:
| Key | Value |
|---|---|
| `DATABASE_URL` | *(Internal Database URL from Step 1)* |
| `SECRET_KEY` | *(Any long random string)* |
| `CLOUDINARY_URL` | *(Your Cloudinary URL)* |

### Step 4: Keep-Alive Cron Job (Prevents Free Tier Sleeping)
1. Create a **New Cron Job** on Render.
2. Set the command to `curl https://YOUR_APP_URL.onrender.com/ping`
3. Set the schedule to `*/10 * * * *` (every 10 minutes).

---

## 📁 Project Structure

```
Online-Food-Ordering-System/
├── app/
│   ├── __init__.py         # App factory & blueprint registration
│   ├── models.py           # SQLAlchemy database models
│   ├── routes/
│   │   ├── auth.py         # Login, register, password reset
│   │   ├── customer.py     # Customer-facing routes
│   │   ├── owner.py        # Restaurant owner portal routes
│   │   └── admin.py        # Admin portal routes
│   ├── static/             # CSS, JS, images
│   └── templates/          # Jinja2 HTML templates
├── migrations/             # Alembic database migration files
├── config.py               # App configuration (DB, keys, Cloudinary)
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── .env                    # Local environment variables (NOT committed)
```

---

## 🔐 Default User Roles

| Role | Access |
|---|---|
| `customer` | Browse restaurants, order food, leave reviews |
| `owner` | Manage own restaurant, dishes, orders, coupons |
| `admin` | Full system access — users, all restaurants, reports |

> An admin user can be created by manually updating a user's `role` column in the database to `'admin'`.

---

## 📜 License

This project was built as an academic eProject for Semester 4. All rights reserved.
