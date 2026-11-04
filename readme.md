# FoodRush: Food Delivery Management System

A DBMS academic project. Customers order food from hotels, hotels manage their menu and orders, delivery partners pick up and deliver, and an admin oversees everything.

**Stack:** Python (Flask) · MySQL · Jinja2 templates · Bootstrap 5 (CDN)

> **Current status:** the app runs end-to-end on **built-in dummy data** (no database needed). The database layer is left as clearly marked `DB-TODO` comments in `app.py`, to be filled with MySQL queries.

---

## Features

| Role | What they can do |
|---|---|
| **Customer** | Browse hotels and menus, add dishes with remarks, apply a coupon, add a tip, pick a payment mode, place orders, track active orders, see past orders, review the hotel or driver, manage profile and delivery addresses |
| **Hotel partner** | See incoming orders (with items and remarks), update order status, add/edit/delete menu items and availability, view the last 30 days of order history, read reviews, manage profile and phone numbers |
| **Delivery partner** | See assigned deliveries with pickup address, drop address, customer/hotel phone, items and "Collect ₹..." info, accept open orders, mark picked up or delivered, set availability and location, view history and reviews |
| **Admin** | Dashboard with stats, view all orders, assign drivers and change order status, view and delete customers, hotels, drivers and reviews |

---

## Project structure

```
project/
├── app.py                  # Flask backend (routes, sessions, validation). No DB code, only DB-TODO comments
├── dummy_data.py           # In-memory demo data (delete after connecting the database)
├── requirements.txt
├── .env                    # Your secrets (create from .env.example, never commit)
├── .env.example
└── templates/
    ├── layout.html         # Shared CSS + sidebar; every dashboard page extends this
    ├── index.html          # Single login panel
    ├── user_register.html   user_menu.html   user_orders.html   user_reviews.html   user_profile.html
    ├── hotel_register.html  hotel_orders.html  hotel_menu.html   hotel_history.html  hotel_reviews.html  hotel_profile.html
    ├── driver_register.html driver_deliveries.html  driver_open.html  driver_availability.html
    │                        driver_history.html     driver_reviews.html  driver_profile.html
    └── admin.html
```

> All `.html` files must be inside the `templates/` folder, and the file names must match exactly (for example `user_menu.html`, not `user menu.html`).

---

## Quick start

```bash
# 1. (optional) create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 2. install dependencies
pip install -r requirements.txt

# 3. create your .env file
copy .env.example .env         # Windows   (cp .env.example .env on macOS / Linux)
# then open .env and set ADMIN_ID, PASSWORD and SECRET_KEY

# 4. run
python app.py
```

Open **http://127.0.0.1:5000**

### `.env` variables

| Variable | Purpose |
|---|---|
| `ADMIN_ID` | Admin login ID |
| `PASSWORD` | Admin login password |
| `SECRET_KEY` | Signs the session cookie. Use a long random string: `python -c "import secrets; print(secrets.token_hex(32))"` |

If `SECRET_KEY` is missing, a random key is generated on every start (everyone gets logged out when the server restarts). If `ADMIN_ID` or `PASSWORD` is missing, admin login is disabled.

---

## Logging in

The login page has one panel: **role selector + ID + password**.

| Letter | Role | ID type |
|---|---|---|
| `U` | User (customer) | number (auto-increment) |
| `H` | Hotel | number (auto-increment) |
| `D` | Driver | number (auto-increment) |
| `A` | Admin | `ADMIN_ID` from `.env` |

IDs are plain integers, so the role letter tells the system which table to check. New users register from the links under the login panel; the ID is generated automatically and shown right after registering, and the user is logged in immediately.

### Demo accounts (dummy mode)

| Role | IDs | Password |
|---|---|---|
| Customer (`U`) | `1`, `2` | `demo123` |
| Hotel (`H`) | `1`, `2`, `3` | `demo123` |
| Driver (`D`) | `1`, `2`, `3` | `demo123` |
| Admin (`A`) | `ADMIN_ID` from `.env` | `PASSWORD` from `.env` |

Dummy coupon: **`SAVE10`** (10% off).

**A good demo flow:**
1. Log in as customer `1`, open *Hotels & Menu*, choose a hotel, add dishes, place an order.
2. Log in as hotel `1`, open *Orders*, set the new order to **Ready for pickup**.
3. Log in as driver `1`, open *Open Orders*, accept it, then mark *Picked up* → *Delivered* in *Deliveries*.
4. Back as the customer, review the delivered order. Check *History* as the hotel, and everything as the admin.

---

## How it works

- **Sessions:** after login, the role and ID are stored in the signed session cookie, not in the URL. A user cannot open another user's dashboard by editing the URL.
- **Access control:** a `before_request` guard allows `/user/*` only for customers, `/hotel/*` only for hotels, `/driver/*` only for drivers and `/admin/*` only for the admin. Only the three register pages are public.
- **Passwords:** customer, hotel and driver passwords are stored **hashed** (Werkzeug), never as plain text. Admin credentials come from `.env`.
- **Server-side checks:** prices, totals and discounts are recalculated on the server, and a hotel or driver can only change their own orders.
- **Layout:** `layout.html` holds the sidebar and all common CSS. The *Hotels & Menu* page is split into four sections: sidebar, hotels list, menu, and cart/amount.

---

## Pages and routes

**Customer**: `/user/menu` · `/user/orders` · `/user/reviews` · `/user/profile` · `POST /user/order` · `POST /user/review` · `POST /user/address`

**Hotel**: `/hotel/orders` · `/hotel/menu` · `/hotel/history` · `/hotel/reviews` · `/hotel/profile` · `POST /hotel/order/status` · `POST /hotel/menu/{add,update,delete}` · `POST /hotel/phone[/delete]`

**Driver**: `/driver/deliveries` · `/driver/open` · `/driver/availability` · `/driver/history` · `/driver/reviews` · `/driver/profile` · `POST /driver/accept` · `POST /driver/order/status` · `POST /driver/status` · `POST /driver/location`

**Public**: `/` (login) · `POST /login` · `/logout` · `/user/register` · `/hotel/register` · `/driver/register`

**Admin**: `/admin` · `POST /admin/order/update` · `POST /admin/{customer,hotel,driver,review}/delete`

---

## Database

The app is designed for these 9 tables: `customer`, `address`, `hotel`, `hotel_phone`, `menu_item`, `driver`, `food_order`, `order_item`, `review`.

Changes the code expects from the original schema:

- Add a **`password VARCHAR(255)`** column to `customer`, `hotel` and `driver` (stores the hash).
- `customer_id`, `hotel_id` and `driver_id` are **`INT AUTO_INCREMENT`**. After each registration insert, use `lastrowid` as the new ID.
- `order_id`, `review_id` and `payment_id` stay as strings (`ORD-20261103-A1B2C3`, `REV-...`, `PAY-...`), generated in Python.
- ENUM values used in the code (change them in `app.py` and the templates if yours differ):
  - `food_order.status`: `PLACED, CONFIRMED, PREPARING, READY, OUT_FOR_DELIVERY, DELIVERED, CANCELLED`
  - `driver.status`: `AVAILABLE, BUSY, OFFLINE`
  - `payment_mode`: `CASH, UPI, CARD, WALLET`
  - `review.target_type`: `HOTEL, DRIVER`
  - `menu_item.category`: `Starter, Main Course, Dessert, Beverage, Snack`

### Connecting your database

1. Add your MySQL connection code at `DB-TODO [0]` in `app.py`.
2. Search `DB-TODO` and write a query at each marker. Every comment lists the inputs and the exact keys of the data the page expects.
3. Remove the demo layer:
   - delete `dummy_data.py`,
   - remove the line `import dummy_data as dummy`,
   - set `USE_DUMMY_DATA = False` (or delete every block marked `# DUMMY-DATA`).

| Marker | Area |
|---|---|
| `A1` | **Login lookup** (start here) |
| `U0`, `U1`–`U12` | Customer |
| `H0`–`H12` | Hotel |
| `D0`–`D11` | Driver |
| `X1`–`X6` | Admin |

Tips: place an order inside a **transaction** (`food_order` + all `order_item` rows). For accepting a delivery use `UPDATE ... WHERE driver_id IS NULL` and check the affected rows, so two drivers cannot take the same order. For hotel history, filter `time_of_order >= NOW() - INTERVAL 30 DAY`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `TemplateNotFound` | HTML files must be inside `templates/` with exact names (underscores, no spaces) |
| Admin login says "ADMIN_ID / PASSWORD set nahi hai" | Create `.env` next to `app.py` and set both variables; install `python-dotenv` |
| Logged out after every restart | Set a fixed `SECRET_KEY` in `.env` |
| Icons or fonts missing | The UI loads Bootstrap, Bootstrap Icons and Google Fonts from a CDN, so an internet connection is needed |
| Data resets on restart | Expected in dummy mode, data lives in memory until the DB is connected |

---

## Security notes

- Never commit `.env`.
- This is an academic project: there is no CSRF protection and no rate limiting beyond a short delay on failed logins. Add Flask-WTF and a limiter before any real deployment.
- Run with `debug=False` and a production server (for example gunicorn) outside of development.