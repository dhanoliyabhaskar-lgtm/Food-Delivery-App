"""
FoodRush - Food Delivery Management System (Flask backend)

Folder structure:
    project/
    ├── app.py
    ├── dummy_data.py              (sirf testing ke liye, DB lagane ke baad delete)
    ├── .env                       (ADMIN_ID, PASSWORD, SECRET_KEY)
    └── templates/
        ├── layout.html            (sidebar + common CSS, baaki sab pages isse extend karte hain)
        ├── index.html             (single login panel)
        ├── user_register.html   user_menu.html   user_orders.html   user_reviews.html   user_profile.html
        ├── hotel_register.html  hotel_orders.html hotel_menu.html    hotel_history.html hotel_reviews.html hotel_profile.html
        ├── driver_register.html driver_deliveries.html driver_open.html driver_availability.html
        │                        driver_history.html  driver_reviews.html driver_profile.html
        └── admin.html

NOTE:
- Is file me KOI database code nahi hai. Jaha DB ka kaam hai waha `DB-TODO [..]` comment hai.
- Jaha dummy data use ho raha hai waha `# DUMMY-DATA` comment hai (search karke hata sakte ho).
- Login ke baad ID session me rehti hai (URL me nahi), isliye koi URL badal kar dusre ka dashboard nahi khol sakta.

DATABASE me ye columns chahiye:
    customer.password, hotel.password, driver.password  -> VARCHAR(255)  (hashed password save hota hai)
    Saari IDs (customer_id, hotel_id, driver_id) INT AUTO_INCREMENT.
"""

import hmac
import os
import secrets
import time
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

# .env se ADMIN_ID / PASSWORD / SECRET_KEY padhne ke liye:  pip install python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv install nahi hai, .env load nahi hogi (pip install python-dotenv)")

app = Flask(__name__)

# Session cookie isi key se sign hoti hai. .env me SECRET_KEY daal do.
# Na ho to har start par random key banegi (restart par sab logout ho jayenge).
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# ---------------------------------------------------------------------------
# DUMMY-DATA: Jab tak DB connect nahi hai, True rehne do. DB lagane ke baad False kar do,
# dummy_data.py delete karo aur niche ka import bhi hata do.
# Dummy login: U ID 1/2 | H ID 1/2/3 | D ID 1/2/3 | password: demo123 | coupon: SAVE10
# ---------------------------------------------------------------------------
USE_DUMMY_DATA = True
import dummy_data as dummy  # DUMMY-DATA: DB lagane ke baad ye import hata dena

# DB-TODO [0]: Yaha MySQL connection setup karo (connector / pool / helper functions).
#   Order place karte waqt transaction zaroor use karna.


# ===========================================================================
# Helper functions (sirf Python logic, DB nahi)
# ===========================================================================

def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def to_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clean(value):
    value = (value or "").strip()
    return value or None


def new_id(prefix):
    """Unique string id, jaise ORD-20261103-A1B2C3 (order_id / review_id / payment_id ke liye)."""
    return f"{prefix}-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"


def uid():
    """Logged-in user ki ID (session se)."""
    return session.get("user_id")


def password_error(password, confirm=None):
    """Password valid hai to None, warna error message."""
    if not password or len(password) < 6:
        return "Password kam se kam 6 characters ka hona chahiye."
    if confirm is not None and password != confirm:
        return "Password aur confirm password match nahi karte."
    return None


def login_user(role, user_id, name):
    session.clear()
    session["role"], session["user_id"], session["name"] = role, user_id, name


# ENUM values - apne MySQL ENUM se match karke badal lena
ORDER_STATUSES = ["PLACED", "CONFIRMED", "PREPARING", "READY", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"]
HOTEL_ALLOWED_STATUSES = ["CONFIRMED", "PREPARING", "READY", "CANCELLED"]
DRIVER_ALLOWED_STATUSES = ["OUT_FOR_DELIVERY", "DELIVERED"]
DRIVER_STATUSES = ["AVAILABLE", "BUSY", "OFFLINE"]
PAYMENT_MODES = ["CASH", "UPI", "CARD", "WALLET"]
REVIEW_TARGETS = ["HOTEL", "DRIVER"]
MENU_CATEGORIES = ["Starter", "Main Course", "Dessert", "Beverage", "Snack"]

ROLE_CODE = {"U": "customer", "H": "hotel", "D": "driver", "A": "admin"}
ROLE_HOME = {"customer": "/user/menu", "hotel": "/hotel/orders", "driver": "/driver/deliveries", "admin": "/admin"}

# Sidebar links: (label, url, bootstrap-icon)
NAV = {
    "customer": {"title": "Customer", "links": [
        ("Hotels & Menu", "/user/menu", "bi-shop"), ("My Orders", "/user/orders", "bi-bag-check"),
        ("Reviews", "/user/reviews", "bi-star"), ("Profile", "/user/profile", "bi-person")]},
    "hotel": {"title": "Hotel Partner", "links": [
        ("Orders", "/hotel/orders", "bi-receipt"), ("Menu", "/hotel/menu", "bi-journal-text"),
        ("History", "/hotel/history", "bi-clock-history"), ("Reviews", "/hotel/reviews", "bi-star"),
        ("Profile", "/hotel/profile", "bi-building")]},
    "driver": {"title": "Delivery Partner", "links": [
        ("Deliveries", "/driver/deliveries", "bi-bicycle"), ("Open Orders", "/driver/open", "bi-inbox"),
        ("Status & Location", "/driver/availability", "bi-geo-alt"), ("History", "/driver/history", "bi-clock-history"),
        ("Reviews", "/driver/reviews", "bi-star"), ("Profile", "/driver/profile", "bi-person")]},
}


@app.context_processor
def inject_layout_data():
    """layout.html ke liye: sidebar links, user ka naam, current path."""
    return {"nav": NAV.get(session.get("role")), "user_name": session.get("name"), "current_path": request.path}


# ---------------------------------------------------------------------------
# Access control: har prefix sirf apne role ke liye. Register pages public hain.
# ---------------------------------------------------------------------------
PROTECTED_PREFIXES = {"/user": "customer", "/hotel": "hotel", "/driver": "driver", "/admin": "admin"}
PUBLIC_PATHS = {"/user/register", "/hotel/register", "/driver/register"}


@app.before_request
def protect_pages():
    path = request.path
    if path in PUBLIC_PATHS:
        return None
    for prefix, role in PROTECTED_PREFIXES.items():
        if path == prefix or path.startswith(prefix + "/"):
            if session.get("role") != role:
                flash("Is page ke liye pehle sahi role se login karo.")
                return redirect("/")
    return None


# ===========================================================================
# LOGIN / LOGOUT  (index.html ka single login panel)
# ===========================================================================

@app.route("/")
def index():
    if session.get("role") in ROLE_HOME:       # pehle se login hai to seedha dashboard
        return redirect(ROLE_HOME[session["role"]])
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    role = ROLE_CODE.get(request.form.get("role"))
    login_id = clean(request.form.get("user_id"))
    password = request.form.get("password", "")

    if not (role and login_id and password):
        flash("Role, ID aur password teeno bharo.")
        return redirect("/")

    # ---- Admin: ID aur password .env se ----
    if role == "admin":
        expected_id, expected_pw = os.getenv("ADMIN_ID"), os.getenv("PASSWORD")
        if not (expected_id and expected_pw):
            flash("Server par ADMIN_ID / PASSWORD set nahi hai (.env file check karo).")
            return redirect("/")
        id_ok = hmac.compare_digest(login_id.encode(), expected_id.encode())
        pw_ok = hmac.compare_digest(password.encode(), expected_pw.encode())
        if not (id_ok and pw_ok):          # `and` nahi, dono compare ho chuke hain (timing safe)
            time.sleep(1)
            flash("Invalid ID ya password.")
            return redirect("/")
        login_user("admin", expected_id, "Administrator")
        return redirect("/admin")

    # ---- Customer / Hotel / Driver: ID integer hoti hai, password DB me hashed ----
    user_id = to_int(login_id)
    if user_id is None:
        flash("ID sirf number hoti hai.")
        return redirect("/")

    stored_hash, name = None, None
    # DB-TODO [A1]: role ke hisaab se table me user_id dhundo:
    #   customer -> `customer` (customer_id), hotel -> `hotel` (hotel_id), driver -> `driver` (driver_id)
    #   stored_hash = us row ka `password` column,  name = customer.name / hotel.hotel_name / driver.name
    #   Row na mile to dono None rehne do.
    if USE_DUMMY_DATA:  # DUMMY-DATA: dummy accounts ka password demo123
        stored_hash, name = dummy.get_login(role, user_id)

    if not stored_hash or not check_password_hash(stored_hash, password):
        time.sleep(1)
        flash("Invalid ID ya password.")
        return redirect("/")

    login_user(role, user_id, name)
    return redirect(ROLE_HOME[role])


@app.route("/logout")
def logout():
    session.clear()
    flash("Logout ho gaye.")
    return redirect("/")


# ===========================================================================
# CUSTOMER
# ===========================================================================

@app.route("/user/register", methods=["GET", "POST"])
def user_register():
    if request.method == "GET":
        return render_template("user_register.html")

    name = clean(request.form.get("name"))
    phone_number = to_int(request.form.get("phone_number"))
    password = request.form.get("password", "")
    error = password_error(password, request.form.get("confirm_password"))

    if not name or phone_number is None:
        error = "Name aur valid phone number zaroori hai."
    if error:
        flash(error)
        return redirect("/user/register")

    pw_hash = generate_password_hash(password)
    customer_id = None
    # DB-TODO [U0]: INSERT into customer (name, phone_number, password) VALUES (name, phone_number, pw_hash)
    #   customer_id AUTO_INCREMENT hai -> naya id (lastrowid) customer_id me daalo.
    if USE_DUMMY_DATA:  # DUMMY-DATA
        customer_id = dummy.save_customer(name, phone_number, pw_hash)

    login_user("customer", customer_id, name)   # registration ke turant baad login
    flash(f"Account ban gaya! Aapka Customer ID: {customer_id}. Login ke liye ise yaad rakho.")
    return redirect("/user/menu")


@app.route("/user")
def user_home():
    return redirect("/user/menu")


@app.route("/user/menu")
def user_menu():
    """Hotels & Menu page (4 sections: sidebar | hotels | menu | cart)."""
    customer_id = uid()
    hotel_id = to_int(request.args.get("hotel_id"))
    data = {"hotels": [], "selected_hotel": None, "menu_items": [], "addresses": []}
    # DB-TODO [U1]: data me ye keys bharo:
    #   hotels         : `hotel` ke saare hotels  [{hotel_id, hotel_name, city, street, opening_time, closing_time}]
    #   selected_hotel : hotel_id wala hotel {hotel_id, hotel_name}  (hotel_id nahi mila to pehla hotel le sakte ho)
    #   menu_items     : us hotel ke `menu_item` [{item_id, name, category, price, availability}]
    #   addresses      : `address` WHERE customer_id [{address_id, house, street, city}]
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.user_menu_page(customer_id, hotel_id)
    return render_template("user_menu.html", **data)


@app.route("/user/order", methods=["POST"])
def user_order():
    customer_id = uid()
    hotel_id = to_int(request.form.get("hotel_id"))
    address_id = to_int(request.form.get("address_id"))
    coupon = clean(request.form.get("coupon"))
    tip = max(to_float(request.form.get("tip"), 0.0), 0.0)
    payment_mode = request.form.get("payment_mode")

    # Cart lines: teeno lists same length (menu ki har row ek entry)
    item_ids = request.form.getlist("item_id")
    quantities = request.form.getlist("quantity")
    remarks_list = request.form.getlist("remarks")

    back = f"/user/menu?hotel_id={hotel_id or ''}"
    if not (hotel_id and address_id):
        flash("Hotel aur delivery address select karna zaroori hai.")
        return redirect(back)
    if payment_mode not in PAYMENT_MODES:
        flash("Valid payment mode select karo.")
        return redirect(back)

    lines = []
    for i, raw in enumerate(item_ids):
        item_id = to_int(raw)
        qty = to_int(quantities[i]) if i < len(quantities) else 0
        remarks = clean(remarks_list[i]) if i < len(remarks_list) else None
        if item_id and qty and qty > 0:           # quantity 0 wali rows skip
            lines.append({"item_id": item_id, "quantity": qty, "remarks": remarks})
    if not lines:
        flash("Cart khali hai. Kam se kam ek dish ki quantity daalo.")
        return redirect(back)

    if USE_DUMMY_DATA:  # DUMMY-DATA: price dummy menu se, coupon SAVE10 = 10%
        result = dummy.place_order(customer_id, hotel_id, address_id, coupon, tip, payment_mode, lines)
        flash(result["message"])
        return redirect("/user/orders" if result["ok"] else back)

    # DB-TODO [U2]: har line ke liye `menu_item` se (hotel_id, item_id) ki price + availability lo
    #   (unavailable ho to flash + redirect(back)); line["price_at_order"] = menu_item.price
    # DB-TODO [U3]: coupon diya ho to discount % nikalo (invalid ho to flash + redirect(back)); discount_pct
    # DB-TODO [U4]: total_price = sum(price_at_order * quantity) * (1 - discount_pct/100)
    # DB-TODO [U5]: TRANSACTION me: INSERT into food_order (order_id, customer_id, hotel_id, driver_id=NULL,
    #   address_id, status='PLACED', payment_id, payment_mode, payment_status, total_price, tip, discount_pct,
    #   coupon, time_of_order, delivery_time=NULL) + har line ke liye INSERT into order_item
    #   (order_id, hotel_id, item_id, quantity, price_at_order, remarks)
    order_id = new_id("ORD")
    payment_id = None if payment_mode == "CASH" else new_id("PAY")
    payment_status = "PENDING" if payment_mode == "CASH" else "PAID"
    time_of_order = datetime.now()
    flash(f"Order place ho gaya! Order ID: {order_id}")
    return redirect("/user/orders")


@app.route("/user/orders")
def user_orders():
    customer_id = uid()
    data = {"active_orders": [], "past_orders": []}
    # DB-TODO [U6]: customer_id ke saare orders (latest pehle). Join: food_order + hotel (hotel_name)
    #   + driver (LEFT JOIN: name, contact_no, vehicle_no) + order_item/menu_item.
    #   active_orders = status DELIVERED/CANCELLED ke ALAWA; past_orders = DELIVERED/CANCELLED
    #   Har row: {order_id, hotel_name, driver_name, contact_no, vehicle_no, status, total_price, tip,
    #             payment_mode, time_of_order, delivery_time,
    #             order_items = [{item_name, quantity, remarks}]}
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.user_orders_page(customer_id)
    return render_template("user_orders.html", **data)


@app.route("/user/reviews")
def user_reviews():
    customer_id = uid()
    data = {"delivered_orders": [], "my_reviews": []}
    # DB-TODO [U7]: delivered_orders = customer ke DELIVERED orders [{order_id, hotel_name, driver_name}]
    #   my_reviews = `review` jinke order customer ke hain
    #   [{review_id, order_id, hotel_name, target_type, rating, text_review}]
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.user_reviews_page(customer_id)
    return render_template("user_reviews.html", **data)


@app.route("/user/review", methods=["POST"])
def user_review():
    order_id = clean(request.form.get("order_id"))
    target_type = request.form.get("target_type")
    rating = to_int(request.form.get("rating"))
    text_review = clean(request.form.get("text_review"))

    if not order_id or target_type not in REVIEW_TARGETS or rating is None or not (1 <= rating <= 5):
        flash("Order, review type aur 1-5 rating select karo.")
        return redirect("/user/reviews")

    # DB-TODO [U8]: verify karo order_id isi customer (uid()) ka hai aur status 'DELIVERED' hai.
    #   Driver review ho aur order me driver_id NULL ho to error. (Optional: duplicate review check)
    if USE_DUMMY_DATA:  # DUMMY-DATA
        flash(dummy.add_review(order_id, target_type, rating, text_review))
        return redirect("/user/reviews")

    review_id = new_id("REV")
    # DB-TODO [U9]: INSERT into review (review_id, order_id, target_type, rating, text_review)
    flash("Review submit ho gaya. Shukriya!")
    return redirect("/user/reviews")


@app.route("/user/profile", methods=["GET", "POST"])
def user_profile():
    customer_id = uid()
    if request.method == "GET":
        data = {"customer": None, "addresses": []}
        # DB-TODO [U10]: customer = {customer_id, name, phone_number};
        #   addresses = `address` WHERE customer_id [{address_id, house, street, city, pin_code}]
        if USE_DUMMY_DATA:  # DUMMY-DATA
            data = dummy.user_profile_page(customer_id)
        return render_template("user_profile.html", **data)

    name = clean(request.form.get("name"))
    phone_number = to_int(request.form.get("phone_number"))
    new_password = request.form.get("new_password", "")
    if not name or phone_number is None:
        flash("Name aur valid phone number zaroori hai.")
        return redirect("/user/profile")
    new_hash = None
    if new_password:                      # khali chhodo to password nahi badlega
        error = password_error(new_password)
        if error:
            flash(error)
            return redirect("/user/profile")
        new_hash = generate_password_hash(new_password)

    # DB-TODO [U11]: UPDATE customer SET name, phone_number WHERE customer_id = uid()
    #   new_hash None nahi hai to `password` = new_hash bhi update karo.
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.update_customer(customer_id, name, phone_number, new_hash)
    session["name"] = name
    flash("Profile update ho gayi.")
    return redirect("/user/profile")


@app.route("/user/address", methods=["POST"])
def user_address():
    customer_id = uid()
    house, street, city = clean(request.form.get("house")), clean(request.form.get("street")), clean(request.form.get("city"))
    pin_code = to_int(request.form.get("pin_code"))
    geo_lat, geo_long = to_float(request.form.get("geo_lat")), to_float(request.form.get("geo_long"))

    if not (house and street and city and pin_code):
        flash("House, street, city aur PIN code bharna zaroori hai.")
        return redirect("/user/profile")

    # DB-TODO [U12]: INSERT into address (customer_id, address_id, house, street, city, geo_lat, geo_long, pin_code)
    #   address_id = us customer ke liye MAX(address_id)+1 (composite key)
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.add_address(customer_id, house, street, city, pin_code, geo_lat, geo_long)
    flash("Address save ho gaya.")
    return redirect("/user/profile")


# ===========================================================================
# HOTEL PARTNER
# ===========================================================================

@app.route("/hotel/register", methods=["GET", "POST"])
def hotel_register():
    if request.method == "GET":
        return render_template("hotel_register.html")

    f = request.form
    hotel_name, opening_time, closing_time = clean(f.get("hotel_name")), clean(f.get("opening_time")), clean(f.get("closing_time"))
    street, city, pin_code = clean(f.get("street")), clean(f.get("city")), to_int(f.get("pin_code"))
    geo_lat, geo_long = to_float(f.get("geo_lat")), to_float(f.get("geo_long"))
    password = f.get("password", "")
    error = password_error(password, f.get("confirm_password"))

    if not (hotel_name and opening_time and closing_time and street and city and pin_code):
        error = "Saari required hotel details bharo."
    if error:
        flash(error)
        return redirect("/hotel/register")

    pw_hash = generate_password_hash(password)
    hotel_id = None
    # DB-TODO [H0]: INSERT into hotel (hotel_name, opening_time, closing_time, city, street, geo_lat,
    #   geo_long, pin_code, password=pw_hash). hotel_id AUTO_INCREMENT -> lastrowid hotel_id me daalo.
    if USE_DUMMY_DATA:  # DUMMY-DATA
        hotel_id = dummy.save_hotel(hotel_name, opening_time, closing_time, street, city, pin_code,
                                    geo_lat, geo_long, pw_hash)

    login_user("hotel", hotel_id, hotel_name)
    flash(f"Hotel register ho gaya! Aapka Hotel ID: {hotel_id}. Login ke liye ise yaad rakho.")
    return redirect("/hotel/orders")


@app.route("/hotel")
def hotel_home():
    return redirect("/hotel/orders")


@app.route("/hotel/orders")
def hotel_orders():
    """Abhi chal rahe (active) orders + quick stats."""
    hotel_id = uid()
    data = {"orders": [], "stats": {}}
    # DB-TODO [H1]: orders = is hotel ke woh orders jinka status DELIVERED/CANCELLED NAHI hai (latest pehle).
    #   Join: food_order + customer (name) + driver (name, LEFT JOIN) + order_item/menu_item.
    #   [{order_id, customer_name, status, total_price, time_of_order, driver_name,
    #     order_items = [{item_name, quantity, remarks}]}]
    #   stats = {total_orders, pending_orders (status PLACED), avg_rating (HOTEL reviews), menu_count}
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.hotel_orders_page(hotel_id)
    return render_template("hotel_orders.html", **data)


@app.route("/hotel/order/status", methods=["POST"])
def hotel_order_status():
    order_id = clean(request.form.get("order_id"))
    status = request.form.get("status")
    if status not in HOTEL_ALLOWED_STATUSES:
        flash("Ye status hotel set nahi kar sakta.")
        return redirect("/hotel/orders")

    # DB-TODO [H2]: UPDATE food_order SET status WHERE order_id AND hotel_id = uid()
    #   (hotel_id check zaroori: hotel dusre hotel ka order na badal sake)
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.set_order_status(order_id, status, hotel_id=uid())
    flash(f"Order {order_id} ka status {status} ho gaya.")
    return redirect("/hotel/orders")


@app.route("/hotel/menu")
def hotel_menu():
    hotel_id = uid()
    data = {"menu_items": []}
    # DB-TODO [H3]: menu_items = `menu_item` WHERE hotel_id [{item_id, name, category, price, availability}]
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.hotel_menu_page(hotel_id)
    return render_template("hotel_menu.html", **data)


@app.route("/hotel/menu/add", methods=["POST"])
def hotel_menu_add():
    name, category = clean(request.form.get("name")), request.form.get("category")
    price = to_float(request.form.get("price"))
    availability = 1 if request.form.get("availability") == "1" else 0
    if not name or category not in MENU_CATEGORIES or price is None or price < 0:
        flash("Item name, category aur valid price daalo.")
        return redirect("/hotel/menu")

    # DB-TODO [H4]: INSERT into menu_item (hotel_id=uid(), item_id, name, category, price, availability)
    #   item_id = us hotel ke liye MAX(item_id)+1 (composite key)
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.add_menu_item(uid(), name, category, price, availability)
    flash("Menu me item add ho gaya.")
    return redirect("/hotel/menu")


@app.route("/hotel/menu/update", methods=["POST"])
def hotel_menu_update():
    item_id = to_int(request.form.get("item_id"))
    price = to_float(request.form.get("price"))
    availability = 1 if request.form.get("availability") == "1" else 0
    if not item_id or price is None or price < 0:
        flash("Valid price daalo.")
        return redirect("/hotel/menu")

    # DB-TODO [H5]: UPDATE menu_item SET price, availability WHERE hotel_id = uid() AND item_id
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.update_menu_item(uid(), item_id, price, availability)
    flash("Menu item update ho gaya.")
    return redirect("/hotel/menu")


@app.route("/hotel/menu/delete", methods=["POST"])
def hotel_menu_delete():
    item_id = to_int(request.form.get("item_id"))

    # DB-TODO [H6]: DELETE from menu_item WHERE hotel_id = uid() AND item_id
    #   order_item me use hua ho to FK error aayega -> delete ki jagah availability = 0 karo.
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.delete_menu_item(uid(), item_id)
    flash("Menu item hata diya.")
    return redirect("/hotel/menu")


@app.route("/hotel/history")
def hotel_history():
    """Pichhle 30 din ke poore ho chuke (DELIVERED / CANCELLED) orders."""
    hotel_id = uid()
    data = {"orders": [], "summary": {}}
    # DB-TODO [H7]: orders = is hotel ke DELIVERED/CANCELLED orders jinka time_of_order pichhle 30 din me ho
    #   (time_of_order >= NOW() - INTERVAL 30 DAY), latest pehle.
    #   [{order_id, customer_name, status, total_price, tip, time_of_order, delivery_time,
    #     order_items = [{item_name, quantity, remarks}]}]
    #   summary = {count, delivered, cancelled, revenue (SUM total_price of DELIVERED)}
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.hotel_history_page(hotel_id)
    return render_template("hotel_history.html", **data)


@app.route("/hotel/reviews")
def hotel_reviews():
    hotel_id = uid()
    data = {"reviews": [], "avg_rating": None}
    # DB-TODO [H8]: reviews = `review` WHERE target_type='HOTEL' aur order isi hotel ka
    #   [{review_id, order_id, rating, text_review}],  avg_rating = AVG(rating) (ya None)
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.hotel_reviews_page(hotel_id)
    return render_template("hotel_reviews.html", **data)


@app.route("/hotel/profile", methods=["GET", "POST"])
def hotel_profile():
    hotel_id = uid()
    if request.method == "GET":
        data = {"hotel": None, "phones": []}
        # DB-TODO [H9]: hotel = hotel row {hotel_id, hotel_name, opening_time, closing_time, city, street,
        #   geo_lat, geo_long, pin_code};  phones = `hotel_phone` WHERE hotel_id [{phone_no}]
        if USE_DUMMY_DATA:  # DUMMY-DATA
            data = dummy.hotel_profile_page(hotel_id)
        return render_template("hotel_profile.html", **data)

    f = request.form
    hotel_name, opening_time, closing_time = clean(f.get("hotel_name")), clean(f.get("opening_time")), clean(f.get("closing_time"))
    street, city, pin_code = clean(f.get("street")), clean(f.get("city")), to_int(f.get("pin_code"))
    geo_lat, geo_long = to_float(f.get("geo_lat")), to_float(f.get("geo_long"))
    new_password = f.get("new_password", "")
    if not (hotel_name and opening_time and closing_time and street and city and pin_code):
        flash("Saari required hotel details bharo.")
        return redirect("/hotel/profile")
    new_hash = None
    if new_password:
        error = password_error(new_password)
        if error:
            flash(error)
            return redirect("/hotel/profile")
        new_hash = generate_password_hash(new_password)

    # DB-TODO [H10]: UPDATE hotel SET hotel_name, opening_time, closing_time, city, street, geo_lat, geo_long,
    #   pin_code WHERE hotel_id = uid();  new_hash None nahi hai to `password` = new_hash bhi.
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.update_hotel(hotel_id, hotel_name, opening_time, closing_time, street, city, pin_code,
                           geo_lat, geo_long, new_hash)
    session["name"] = hotel_name
    flash("Hotel details update ho gayi.")
    return redirect("/hotel/profile")


@app.route("/hotel/phone", methods=["POST"])
def hotel_phone_add():
    phone_no = clean(request.form.get("phone_no"))
    if not phone_no:
        flash("Phone number daalo.")
        return redirect("/hotel/profile")

    # DB-TODO [H11]: INSERT into hotel_phone (hotel_id=uid(), phone_no); duplicate ho to flash me batao.
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.add_phone(uid(), phone_no)
    flash("Phone number add ho gaya.")
    return redirect("/hotel/profile")


@app.route("/hotel/phone/delete", methods=["POST"])
def hotel_phone_delete():
    phone_no = clean(request.form.get("phone_no"))

    # DB-TODO [H12]: DELETE from hotel_phone WHERE hotel_id = uid() AND phone_no
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.delete_phone(uid(), phone_no)
    flash("Phone number hata diya.")
    return redirect("/hotel/profile")


# ===========================================================================
# DELIVERY PARTNER
# ===========================================================================

@app.route("/driver/register", methods=["GET", "POST"])
def driver_register():
    if request.method == "GET":
        return render_template("driver_register.html")

    name, contact_no = clean(request.form.get("name")), clean(request.form.get("contact_no"))
    vehicle_no, current_city = clean(request.form.get("vehicle_no")), clean(request.form.get("current_city"))
    password = request.form.get("password", "")
    error = password_error(password, request.form.get("confirm_password"))

    if not (name and contact_no and vehicle_no and current_city):
        error = "Saari required details bharo."
    if error:
        flash(error)
        return redirect("/driver/register")

    pw_hash = generate_password_hash(password)
    driver_id = None
    # DB-TODO [D0]: INSERT into driver (name, contact_no, vehicle_no, status='OFFLINE', curr_lat=NULL,
    #   curr_long=NULL, current_city, password=pw_hash). driver_id AUTO_INCREMENT -> lastrowid driver_id me daalo.
    if USE_DUMMY_DATA:  # DUMMY-DATA
        driver_id = dummy.save_driver(name, contact_no, vehicle_no, current_city, pw_hash)

    login_user("driver", driver_id, name)
    flash(f"Driver register ho gaya! Aapka Driver ID: {driver_id}. Login ke liye ise yaad rakho.")
    return redirect("/driver/deliveries")


@app.route("/driver")
def driver_home():
    return redirect("/driver/deliveries")


@app.route("/driver/deliveries")
def driver_deliveries():
    driver_id = uid()
    data = {"driver": None, "my_orders": [], "stats": {}}
    # DB-TODO [D1]: driver = driver row {driver_id, name, status, current_city}
    #   my_orders = is driver ke ASSIGNED orders jo DELIVERED/CANCELLED NAHI hain. Har order ke liye:
    #     order_id, status, total_price, tip, payment_mode, payment_status
    #     pickup  : hotel_name, hotel_street (hotel.street), hotel_city (hotel.city), hotel_phone (hotel_phone ka koi ek),
    #               hotel_lat, hotel_long (hotel.geo_lat/geo_long)
    #     drop    : customer_name, customer_phone (customer.phone_number), house, street, city, pin_code,
    #               drop_lat, drop_long (address.geo_lat/geo_long; food_order.customer_id + address_id se)
    #     order_items = [{item_name, quantity, remarks}]
    #   stats = {completed (DELIVERED count), active, total_tips (SUM tip of delivered), avg_rating (DRIVER reviews)}
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.driver_deliveries_page(driver_id)
    return render_template("driver_deliveries.html", **data)


@app.route("/driver/open")
def driver_open():
    driver_id = uid()
    data = {"driver": None, "open_orders": []}
    # DB-TODO [D2]: driver row (status chahiye: accept sirf AVAILABLE driver kar sakta hai)
    #   open_orders = food_order WHERE status='READY' AND driver_id IS NULL
    #   [{order_id, hotel_name, hotel_street, hotel_city, city (drop city), total_price, tip,
    #     order_items = [{item_name, quantity, remarks}]}]
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.driver_open_page(driver_id)
    return render_template("driver_open.html", **data)


@app.route("/driver/accept", methods=["POST"])
def driver_accept():
    order_id = clean(request.form.get("order_id"))

    # DB-TODO [D3]: Transaction me: (a) driver ka status 'AVAILABLE' check
    #   (b) UPDATE food_order SET driver_id = uid() WHERE order_id AND driver_id IS NULL
    #       -> affected rows 0 = kisi aur ne pehle le liya (flash karke return)
    #   (c) UPDATE driver SET status='BUSY' WHERE driver_id = uid()
    if USE_DUMMY_DATA:  # DUMMY-DATA
        flash(dummy.accept_order(uid(), order_id))
        return redirect("/driver/deliveries")
    flash(f"Order {order_id} aapko assign ho gaya.")
    return redirect("/driver/deliveries")


@app.route("/driver/order/status", methods=["POST"])
def driver_order_status():
    order_id = clean(request.form.get("order_id"))
    status = request.form.get("status")
    if status not in DRIVER_ALLOWED_STATUSES:
        flash("Ye status driver set nahi kar sakta.")
        return redirect("/driver/deliveries")

    delivery_time = datetime.now() if status == "DELIVERED" else None
    # DB-TODO [D4]: UPDATE food_order SET status (DELIVERED ho to delivery_time bhi) WHERE order_id
    #   AND driver_id = uid().  DELIVERED ho to UPDATE driver SET status='AVAILABLE' bhi karo.
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.set_order_status(order_id, status, driver_id=uid())
    flash(f"Order {order_id} ka status {status} ho gaya.")
    return redirect("/driver/deliveries")


@app.route("/driver/availability")
def driver_availability():
    driver_id = uid()
    data = {"driver": None}
    # DB-TODO [D5]: driver = {driver_id, name, status, curr_lat, curr_long, current_city}
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.driver_availability_page(driver_id)
    return render_template("driver_availability.html", **data)


@app.route("/driver/status", methods=["POST"])
def driver_status():
    status = request.form.get("status")
    if status not in DRIVER_STATUSES:
        flash("Galat status.")
        return redirect("/driver/availability")

    # DB-TODO [D6]: UPDATE driver SET status WHERE driver_id = uid()
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.set_driver_status(uid(), status)
    flash(f"Status {status} set ho gaya.")
    return redirect("/driver/availability")


@app.route("/driver/location", methods=["POST"])
def driver_location():
    current_city = clean(request.form.get("current_city"))
    curr_lat, curr_long = to_float(request.form.get("curr_lat")), to_float(request.form.get("curr_long"))

    # DB-TODO [D7]: UPDATE driver SET current_city, curr_lat, curr_long WHERE driver_id = uid()
    #   (lat/long None ho sakte hain -> NULL)
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.set_driver_location(uid(), current_city, curr_lat, curr_long)
    flash("Location update ho gayi.")
    return redirect("/driver/availability")


@app.route("/driver/history")
def driver_history():
    driver_id = uid()
    data = {"history": [], "stats": {}}
    # DB-TODO [D8]: history = is driver ke DELIVERED orders (latest pehle)
    #   [{order_id, hotel_name, customer_name, total_price, tip, delivery_time}]
    #   stats = {completed, active, total_tips, avg_rating}  (D1 jaisa)
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.driver_history_page(driver_id)
    return render_template("driver_history.html", **data)


@app.route("/driver/reviews")
def driver_reviews():
    driver_id = uid()
    data = {"reviews": [], "avg_rating": None}
    # DB-TODO [D9]: reviews = `review` WHERE target_type='DRIVER' aur order ka driver_id = uid()
    #   [{review_id, order_id, rating, text_review}],  avg_rating = AVG(rating) (ya None)
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.driver_reviews_page(driver_id)
    return render_template("driver_reviews.html", **data)


@app.route("/driver/profile", methods=["GET", "POST"])
def driver_profile():
    driver_id = uid()
    if request.method == "GET":
        data = {"driver": None}
        # DB-TODO [D10]: driver = {driver_id, name, contact_no, vehicle_no}
        if USE_DUMMY_DATA:  # DUMMY-DATA
            data = dummy.driver_profile_page(driver_id)
        return render_template("driver_profile.html", **data)

    name, contact_no, vehicle_no = clean(request.form.get("name")), clean(request.form.get("contact_no")), clean(request.form.get("vehicle_no"))
    new_password = request.form.get("new_password", "")
    if not (name and contact_no and vehicle_no):
        flash("Saari required details bharo.")
        return redirect("/driver/profile")
    new_hash = None
    if new_password:
        error = password_error(new_password)
        if error:
            flash(error)
            return redirect("/driver/profile")
        new_hash = generate_password_hash(new_password)

    # DB-TODO [D11]: UPDATE driver SET name, contact_no, vehicle_no WHERE driver_id = uid()
    #   new_hash None nahi hai to `password` = new_hash bhi update karo.
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.update_driver(driver_id, name, contact_no, vehicle_no, new_hash)
    session["name"] = name
    flash("Driver profile update ho gayi.")
    return redirect("/driver/profile")


# ===========================================================================
# ADMIN  (login /login se hota hai, ADMIN_ID aur PASSWORD .env me)
# ===========================================================================

@app.route("/admin")
def admin_dashboard():
    data = {"stats": {}, "orders": [], "customers": [], "hotels": [], "drivers": [], "reviews": []}
    # DB-TODO [X1]: data ke keys bharo:
    #   stats     : {customers, hotels, drivers, orders (COUNTs), revenue (SUM total_price DELIVERED), avg_rating}
    #   orders    : saare orders latest pehle: {order_id, customer_id, customer_name, hotel_id, hotel_name,
    #               driver_id, driver_name (LEFT JOIN), status, payment_mode, payment_status, total_price, tip,
    #               discount_pct, coupon, time_of_order, delivery_time}
    #   customers : [{customer_id, name, phone_number}]   (password column mat bhejna)
    #   hotels    : [{hotel_id, hotel_name, city, opening_time, closing_time, pin_code}]
    #   drivers   : [{driver_id, name, contact_no, vehicle_no, status, current_city}]
    #   reviews   : [{review_id, order_id, target_type, rating, text_review}]
    if USE_DUMMY_DATA:  # DUMMY-DATA
        data = dummy.admin_dashboard()
    return render_template("admin.html", **data)


@app.route("/admin/order/update", methods=["POST"])
def admin_order_update():
    order_id = clean(request.form.get("order_id"))
    driver_id = to_int(request.form.get("driver_id"))   # None = koi driver nahi
    status = request.form.get("status")
    if status not in ORDER_STATUSES:
        flash("Galat status.")
        return redirect("/admin")

    delivery_time = datetime.now() if status == "DELIVERED" else None
    # DB-TODO [X2]: UPDATE food_order SET driver_id (NULL bhi), status (DELIVERED ho to delivery_time)
    #   WHERE order_id
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.admin_update_order(order_id, driver_id, status)
    flash(f"Order {order_id} update ho gaya.")
    return redirect("/admin")


@app.route("/admin/customer/delete", methods=["POST"])
def admin_customer_delete():
    customer_id = to_int(request.form.get("customer_id"))
    # DB-TODO [X3]: DELETE customer (aur uske address). Orders hain to FK error -> CASCADE ya error flash.
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.delete_customer(customer_id)
    flash("Customer delete ho gaya.")
    return redirect("/admin")


@app.route("/admin/hotel/delete", methods=["POST"])
def admin_hotel_delete():
    hotel_id = to_int(request.form.get("hotel_id"))
    # DB-TODO [X4]: DELETE hotel (hotel_phone, menu_item bhi). Orders ho to error handle karo.
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.delete_hotel(hotel_id)
    flash("Hotel delete ho gaya.")
    return redirect("/admin")


@app.route("/admin/driver/delete", methods=["POST"])
def admin_driver_delete():
    driver_id = to_int(request.form.get("driver_id"))
    # DB-TODO [X5]: DELETE driver (pehle orders me driver_id = NULL ya FK ON DELETE SET NULL)
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.delete_driver(driver_id)
    flash("Driver delete ho gaya.")
    return redirect("/admin")


@app.route("/admin/review/delete", methods=["POST"])
def admin_review_delete():
    review_id = clean(request.form.get("review_id"))
    # DB-TODO [X6]: DELETE from review WHERE review_id
    if USE_DUMMY_DATA:  # DUMMY-DATA
        dummy.delete_review(review_id)
    flash("Review delete ho gaya.")
    return redirect("/admin")


# ===========================================================================

if __name__ == "__main__":
    app.run(debug=True)