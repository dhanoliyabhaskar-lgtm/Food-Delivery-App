"""
FoodRush - Food Delivery Management System (Flask backend)

Folder structure:
    project/
    ├── app.py
    └── templates/
        ├── index.html
        ├── user.html
        ├── hotel.html
        ├── driver.html
        └── admin.html

NOTE:
- Is file me KOI database code nahi hai (no mysql import, no connection, no query).
- Jaha bhi DB ka kaam karna hai waha `DB-TODO` comment hai. Search karo: "DB-TODO".
- Har DB-TODO me likha hai: kya karna hai, input kya milega, aur kya return/pass karna hai.
- Abhi placeholders (None / [] / {}) hain, isliye bina DB ke bhi saare pages khul jayenge.
"""

import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # flash() ke liye zaroori

# ---------------------------------------------------------------------------
# DB-TODO [0]: Yaha MySQL connection setup karo (connector / pool / helper functions).
#   Suggestion: ek helper bana lena jaise get_db() jo connection de, aur har route me
#   use karke commit/close karna. Order place karte waqt transaction zaroor use karna.
# ---------------------------------------------------------------------------


# ===========================================================================
# Helper functions (sirf Python logic, DB nahi)
# ===========================================================================

def to_int(value):
    """'' ya galat value ko None bana deta hai, warna int."""
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
    """Form text ko strip karta hai; khali ho to None."""
    value = (value or "").strip()
    return value or None


def new_id(prefix):
    """Unique string id, jaise ORD-20261103-A1B2C3. order_id / review_id / payment_id ke liye."""
    return f"{prefix}-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"


# ENUM values - apne MySQL ENUM se match karke badal lena
ORDER_STATUSES = ["PLACED", "CONFIRMED", "PREPARING", "READY",
                  "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"]
HOTEL_ALLOWED_STATUSES = ["CONFIRMED", "PREPARING", "READY", "CANCELLED"]
DRIVER_ALLOWED_STATUSES = ["OUT_FOR_DELIVERY", "DELIVERED"]
DRIVER_STATUSES = ["AVAILABLE", "BUSY", "OFFLINE"]
PAYMENT_MODES = ["CASH", "UPI", "CARD", "WALLET"]
REVIEW_TARGETS = ["HOTEL", "DRIVER"]
MENU_CATEGORIES = ["Starter", "Main Course", "Dessert", "Beverage", "Snack"]


# ===========================================================================
# 1. LANDING PAGE
# ===========================================================================

@app.route("/")
def index():
    return render_template("index.html")


# ===========================================================================
# 2. CUSTOMER  (user.html)
# ===========================================================================

def redirect_user(customer_id, hotel_id=None):
    url = f"/user?customer_id={customer_id or ''}"
    if hotel_id:
        url += f"&hotel_id={hotel_id}"
    return redirect(url)


@app.route("/user")
def user_dashboard():
    customer_id = to_int(request.args.get("customer_id"))
    hotel_id = clean(request.args.get("hotel_id"))

    customer = None          # dict: customer_id, name, phone_number
    addresses = []           # list of dict: address_id, house, street, city, geo_lat, geo_long, pin_code
    hotels = []              # list of dict: hotel_id, hotel_name, city, street, opening_time, closing_time
    selected_hotel = None    # dict: hotel_id, hotel_name
    menu_items = []          # list of dict: item_id, name, category, price, availability
    active_orders = []       # list of dict: order_id, hotel_name, driver_name, contact_no, vehicle_no,
                             #               status, total_price, time_of_order
    delivered_orders = []    # list of dict: order_id, hotel_name, driver_name

    # DB-TODO [1]: customer_id mila ho to `customer` table se us customer ki row lo
    #   -> customer = {customer_id, name, phone_number}. Na mile to customer None rehne do.

    # DB-TODO [2]: customer_id ho to `address` table se uske saare addresses lo
    #   -> addresses = [{address_id, house, street, city, geo_lat, geo_long, pin_code}, ...]

    # DB-TODO [3]: `hotel` table se saare hotels lo (jo available/open ho sakte hain)
    #   -> hotels = [{hotel_id, hotel_name, city, street, opening_time, closing_time}, ...]

    # DB-TODO [4]: hotel_id mila ho to us hotel ki row lo -> selected_hotel = {hotel_id, hotel_name}
    #   aur `menu_item` se us hotel_id ke saare items lo
    #   -> menu_items = [{item_id, name, category, price, availability}, ...]
    #   (availability: 1 = available, 0 = nahi)

    # DB-TODO [5]: Active orders: `food_order` me customer_id ke woh orders jinka status
    #   DELIVERED ya CANCELLED NAHI hai. Join chahiye:
    #     food_order + hotel (hotel_name) + driver (name, contact_no, vehicle_no; driver NULL bhi ho sakta hai - LEFT JOIN)
    #   -> active_orders = [{order_id, hotel_name, driver_name, contact_no, vehicle_no,
    #                        status, total_price, time_of_order}, ...]   (latest pehle)

    # DB-TODO [6]: Review ke liye: customer ke woh orders jinka status = 'DELIVERED' hai
    #   (aur jinka review abhi nahi diya gaya, ye optional hai). Join hotel + driver (LEFT JOIN).
    #   -> delivered_orders = [{order_id, hotel_name, driver_name}, ...]

    return render_template(
        "user.html",
        customer=customer,
        addresses=addresses,
        hotels=hotels,
        selected_hotel=selected_hotel,
        menu_items=menu_items,
        active_orders=active_orders,
        delivered_orders=delivered_orders,
    )


@app.route("/user/profile", methods=["POST"])
def user_profile():
    customer_id = to_int(request.form.get("customer_id"))
    name = clean(request.form.get("name"))
    phone_number = to_int(request.form.get("phone_number"))

    if not name or phone_number is None:
        flash("Name aur valid phone number zaroori hai.")
        return redirect_user(customer_id)

    if customer_id:
        # DB-TODO [7]: UPDATE customer SET name, phone_number WHERE customer_id
        #   inputs: customer_id, name, phone_number
        flash("Profile update ho gayi.")
    else:
        # DB-TODO [8]: INSERT into customer (name, phone_number).
        #   customer_id AUTO_INCREMENT hai to naya id (lastrowid) customer_id variable me daalo,
        #   warna khud generate karo.
        #   inputs: name, phone_number
        flash("Profile ban gayi.")

    return redirect_user(customer_id)


@app.route("/user/address", methods=["POST"])
def user_address():
    customer_id = to_int(request.form.get("customer_id"))
    house = clean(request.form.get("house"))
    street = clean(request.form.get("street"))
    city = clean(request.form.get("city"))
    pin_code = to_int(request.form.get("pin_code"))
    geo_lat = to_float(request.form.get("geo_lat"))      # optional, None ho sakta hai
    geo_long = to_float(request.form.get("geo_long"))    # optional, None ho sakta hai

    if not customer_id:
        flash("Pehle profile banao, phir address add karo.")
        return redirect_user(None)
    if not (house and street and city and pin_code):
        flash("House, street, city aur PIN code bharna zaroori hai.")
        return redirect_user(customer_id)

    # DB-TODO [9]: INSERT into address (customer_id, address_id, house, street, city, geo_lat, geo_long, pin_code)
    #   address_id composite key ka hissa hai -> us customer ke liye next id = MAX(address_id)+1 (ya 1)
    #   inputs: customer_id, house, street, city, pin_code, geo_lat, geo_long

    flash("Address save ho gaya.")
    return redirect_user(customer_id)


@app.route("/user/order", methods=["POST"])
def user_order():
    customer_id = to_int(request.form.get("customer_id"))
    hotel_id = clean(request.form.get("hotel_id"))
    address_id = to_int(request.form.get("address_id"))
    coupon = clean(request.form.get("coupon"))
    tip = max(to_float(request.form.get("tip"), 0.0), 0.0)
    payment_mode = request.form.get("payment_mode")

    # Cart lines: teeno lists same length ki hoti hain (menu ki har row ek entry)
    item_ids = request.form.getlist("item_id")
    quantities = request.form.getlist("quantity")
    remarks_list = request.form.getlist("remarks")

    # --- Basic validation (Python only) ---
    if not (customer_id and hotel_id and address_id):
        flash("Customer, hotel aur delivery address select karna zaroori hai.")
        return redirect_user(customer_id, hotel_id)
    if payment_mode not in PAYMENT_MODES:
        flash("Valid payment mode select karo.")
        return redirect_user(customer_id, hotel_id)

    # --- Cart lines banao: quantity 0 wali rows skip ---
    lines = []
    for i, raw_item_id in enumerate(item_ids):
        item_id = to_int(raw_item_id)
        qty = to_int(quantities[i]) if i < len(quantities) else 0
        remarks = clean(remarks_list[i]) if i < len(remarks_list) else None
        if item_id and qty and qty > 0:
            lines.append({"item_id": item_id, "quantity": qty, "remarks": remarks})

    if not lines:
        flash("Cart khali hai. Kam se kam ek dish ki quantity daalo.")
        return redirect_user(customer_id, hotel_id)

    # DB-TODO [10]: Har line ke liye `menu_item` se (hotel_id, item_id) ki price aur availability lo.
    #   - Agar item available nahi hai ya exist nahi karta -> flash error + redirect_user(...) return karo.
    #   - Line me "price_at_order" set karo (menu_item.price) -> line["price_at_order"] = ...
    #   Neeche ka loop us price ko use karke subtotal banata hai.
    for line in lines:
        line["price_at_order"] = 0.0  # TODO: DB se actual price yaha daalo

    subtotal = sum(l["price_at_order"] * l["quantity"] for l in lines)

    # DB-TODO [11]: Coupon check (agar coupon diya hai): coupon table / rule se discount % nikalo.
    #   Invalid coupon ho to flash + redirect. Valid ho to discount_pct = <value>.
    discount_pct = 0.0

    total_price = round(subtotal * (1 - discount_pct / 100), 2)

    # DB-TODO [12] (optional): Hotel ka opening_time/closing_time check karo, closed ho to order mat lo.

    order_id = new_id("ORD")
    payment_id = None if payment_mode == "CASH" else new_id("PAY")
    payment_status = "PENDING" if payment_mode == "CASH" else "PAID"
    time_of_order = datetime.now()

    # DB-TODO [13]: TRANSACTION me ye dono kaam karo (fail ho to rollback):
    #   (a) INSERT into food_order (order_id, customer_id, hotel_id, driver_id=NULL, address_id,
    #                               status='PLACED', payment_id, payment_mode, payment_status,
    #                               total_price, tip, discount_pct, coupon, time_of_order, delivery_time=NULL)
    #   (b) har line ke liye INSERT into order_item (order_id, hotel_id, item_id, quantity,
    #                                                price_at_order, remarks)
    #   Variables ready: order_id, customer_id, hotel_id, address_id, payment_id, payment_mode,
    #                    payment_status, total_price, tip, discount_pct, coupon, time_of_order, lines

    flash(f"Order place ho gaya! Order ID: {order_id}")
    return redirect_user(customer_id)


@app.route("/user/review", methods=["POST"])
def user_review():
    customer_id = to_int(request.form.get("customer_id"))  # hidden field se aata hai
    order_id = clean(request.form.get("order_id"))
    target_type = request.form.get("target_type")
    rating = to_int(request.form.get("rating"))
    text_review = clean(request.form.get("text_review"))

    if not order_id or target_type not in REVIEW_TARGETS or rating is None or not (1 <= rating <= 5):
        flash("Order, review type aur 1-5 rating select karo.")
        return redirect_user(customer_id)

    # DB-TODO [14]: Verify karo ki order_id ka status 'DELIVERED' hai (aur customer_id wahi hai).
        #   Driver review ho aur order me driver_id NULL ho to error do.

    # DB-TODO [15] (optional): Check karo ki is order + target_type ka review pehle se to nahi hai.

    review_id = new_id("REV")

    # DB-TODO [16]: INSERT into review (review_id, order_id, target_type, rating, text_review)
    #   Variables ready: review_id, order_id, target_type, rating, text_review

    flash("Review submit ho gaya. Shukriya!")
    return redirect_user(customer_id)


# ===========================================================================
# 3. HOTEL PARTNER  (hotel.html)
# ===========================================================================

def redirect_hotel(hotel_id):
    return redirect(f"/hotel?hotel_id={hotel_id or ''}")


@app.route("/hotel")
def hotel_dashboard():
    hotel_id = clean(request.args.get("hotel_id"))

    hotel = None        # dict: hotel_id, hotel_name, opening_time, closing_time, city, street, geo_lat, geo_long, pin_code
    phones = []         # list of dict: phone_no
    menu_items = []     # list of dict: item_id, name, category, price, availability
    orders = []         # list of dict: order_id, customer_name, items, status, total_price, time_of_order, driver_name
    reviews = []        # list of dict: review_id, order_id, rating, text_review
    stats = {}          # dict: total_orders, pending_orders, avg_rating, menu_count

    if hotel_id:
        # DB-TODO [17]: `hotel` table se hotel_id ki row lo -> hotel dict (upar ke keys)
        #   Na mile to hotel None rehne do (page registration form dikhayega).

        # DB-TODO [18]: `hotel_phone` se hotel_id ke saare phone_no -> phones = [{phone_no}, ...]

        # DB-TODO [19]: `menu_item` se hotel_id ke saare items
        #   -> menu_items = [{item_id, name, category, price, availability}, ...]

        # DB-TODO [20]: Is hotel ke orders (latest pehle). Join chahiye:
        #   food_order + customer (name as customer_name) + driver (name as driver_name, LEFT JOIN)
        #   + order_item/menu_item se items ki summary string, jaise "2 x Paneer Tikka, 1 x Naan"
        #   -> orders = [{order_id, customer_name, items, status, total_price, time_of_order, driver_name}, ...]

        # DB-TODO [21]: `review` se woh reviews jinka target_type='HOTEL' aur order isi hotel ka ho
        #   -> reviews = [{review_id, order_id, rating, text_review}, ...]

        # DB-TODO [22]: Stats calculate karo (COUNT / AVG queries):
        #   stats = {"total_orders": ..., "pending_orders": (status PLACED), "avg_rating": ..., "menu_count": ...}
        pass

    return render_template(
        "hotel.html",
        hotel=hotel, phones=phones, menu_items=menu_items,
        orders=orders, reviews=reviews, stats=stats,
    )


@app.route("/hotel/profile", methods=["POST"])
def hotel_profile():
    hotel_id = clean(request.form.get("hotel_id"))
    hotel_name = clean(request.form.get("hotel_name"))
    opening_time = clean(request.form.get("opening_time"))   # "HH:MM"
    closing_time = clean(request.form.get("closing_time"))   # "HH:MM"
    street = clean(request.form.get("street"))
    city = clean(request.form.get("city"))
    pin_code = to_int(request.form.get("pin_code"))
    geo_lat = to_float(request.form.get("geo_lat"))
    geo_long = to_float(request.form.get("geo_long"))

    if not (hotel_id and hotel_name and opening_time and closing_time and street and city and pin_code):
        flash("Saari required hotel details bharo.")
        return redirect_hotel(hotel_id)

    # DB-TODO [23]: Check karo ki hotel_id pehle se exist karta hai ya nahi.
    #   - Exist karta hai -> UPDATE hotel SET hotel_name, opening_time, closing_time, city, street,
    #                        geo_lat, geo_long, pin_code WHERE hotel_id
    #   - Nahi karta      -> INSERT into hotel (hotel_id, hotel_name, opening_time, closing_time,
    #                        city, street, geo_lat, geo_long, pin_code)
    #   Variables ready: hotel_id, hotel_name, opening_time, closing_time, street, city, pin_code, geo_lat, geo_long

    flash("Hotel details save ho gayi.")
    return redirect_hotel(hotel_id)


@app.route("/hotel/phone", methods=["POST"])
def hotel_phone_add():
    hotel_id = clean(request.form.get("hotel_id"))
    phone_no = clean(request.form.get("phone_no"))

    if not (hotel_id and phone_no):
        flash("Phone number daalo.")
        return redirect_hotel(hotel_id)

    # DB-TODO [24]: INSERT into hotel_phone (hotel_id, phone_no). Duplicate (same hotel + number) ho to
    #   error handle karo aur flash me batao.

    flash("Phone number add ho gaya.")
    return redirect_hotel(hotel_id)


@app.route("/hotel/phone/delete", methods=["POST"])
def hotel_phone_delete():
    hotel_id = clean(request.form.get("hotel_id"))
    phone_no = clean(request.form.get("phone_no"))

    # DB-TODO [25]: DELETE from hotel_phone WHERE hotel_id AND phone_no

    flash("Phone number hata diya.")
    return redirect_hotel(hotel_id)


@app.route("/hotel/menu/add", methods=["POST"])
def hotel_menu_add():
    hotel_id = clean(request.form.get("hotel_id"))
    name = clean(request.form.get("name"))
    category = request.form.get("category")
    price = to_float(request.form.get("price"))
    availability = 1 if request.form.get("availability") == "1" else 0

    if not (hotel_id and name) or category not in MENU_CATEGORIES or price is None or price < 0:
        flash("Item name, category aur valid price daalo.")
        return redirect_hotel(hotel_id)

    # DB-TODO [26]: INSERT into menu_item (hotel_id, item_id, name, category, price, availability)
    #   item_id composite key ka hissa hai -> us hotel ke liye next id = MAX(item_id)+1 (ya 1)
    #   Variables ready: hotel_id, name, category, price, availability

    flash("Menu me item add ho gaya.")
    return redirect_hotel(hotel_id)


@app.route("/hotel/menu/update", methods=["POST"])
def hotel_menu_update():
    hotel_id = clean(request.form.get("hotel_id"))
    item_id = to_int(request.form.get("item_id"))
    price = to_float(request.form.get("price"))
    availability = 1 if request.form.get("availability") == "1" else 0

    if not (hotel_id and item_id) or price is None or price < 0:
        flash("Valid price daalo.")
        return redirect_hotel(hotel_id)

    # DB-TODO [27]: UPDATE menu_item SET price, availability WHERE hotel_id AND item_id
    #   Variables ready: hotel_id, item_id, price, availability

    flash("Menu item update ho gaya.")
    return redirect_hotel(hotel_id)


@app.route("/hotel/menu/delete", methods=["POST"])
def hotel_menu_delete():
    hotel_id = clean(request.form.get("hotel_id"))
    item_id = to_int(request.form.get("item_id"))

    # DB-TODO [28]: DELETE from menu_item WHERE hotel_id AND item_id
    #   Dhyan: order_item me ye item use hua ho to foreign key error aayega.
    #   Aisa ho to delete ki jagah availability = 0 kar do aur flash me batao.

    flash("Menu item hata diya.")
    return redirect_hotel(hotel_id)


@app.route("/hotel/order/status", methods=["POST"])
def hotel_order_status():
    hotel_id = clean(request.form.get("hotel_id"))
    order_id = clean(request.form.get("order_id"))
    status = request.form.get("status")

    if status not in HOTEL_ALLOWED_STATUSES:
        flash("Ye status hotel set nahi kar sakta.")
        return redirect_hotel(hotel_id)

    # DB-TODO [29]: UPDATE food_order SET status WHERE order_id AND hotel_id
    #   (hotel_id check zaroori hai taaki hotel dusre hotel ka order na badal sake)
    #   Optional: DELIVERED / CANCELLED ho chuke order ko dobara change na hone do.

    flash(f"Order {order_id} ka status {status} ho gaya.")
    return redirect_hotel(hotel_id)


# ===========================================================================
# 4. DELIVERY PARTNER  (driver.html)
# ===========================================================================

def redirect_driver(driver_id):
    return redirect(f"/driver?driver_id={driver_id or ''}")


@app.route("/driver")
def driver_dashboard():
    driver_id = clean(request.args.get("driver_id"))

    driver = None        # dict: driver_id, name, contact_no, vehicle_no, status, curr_lat, curr_long, current_city
    my_orders = []       # list of dict: order_id, hotel_name, hotel_street, hotel_city, customer_name,
                         #               house, street, city, status, total_price, tip, payment_mode
    open_orders = []     # list of dict: order_id, hotel_name, hotel_street, hotel_city, city, total_price, tip
    history = []         # list of dict: order_id, hotel_name, delivery_time, tip
    reviews = []         # list of dict: review_id, order_id, rating, text_review
    stats = {}           # dict: completed, active, total_tips, avg_rating

    if driver_id:
        # DB-TODO [30]: `driver` table se driver_id ki row lo -> driver dict. Na mile to None.

        # DB-TODO [31]: Is driver ko assigned orders (food_order.driver_id = driver_id)
        #   Join: hotel (hotel_name, street -> hotel_street, city -> hotel_city),
        #         customer (name -> customer_name), address (house, street, city via customer_id + address_id)
        #   -> my_orders = [...]  (DELIVERED/CANCELLED bhi aa sakte hain; template unhe 'Closed' dikhata hai)

        # DB-TODO [32]: Open orders jo koi bhi driver accept kar sakta hai:
        #   food_order WHERE status='READY' AND driver_id IS NULL
        #   Join hotel + address (drop city). Optional: driver.current_city se match karke filter karo.
        #   -> open_orders = [{order_id, hotel_name, hotel_street, hotel_city, city, total_price, tip}, ...]

        # DB-TODO [33]: Delivery history: is driver ke DELIVERED orders
        #   -> history = [{order_id, hotel_name, delivery_time, tip}, ...]

        # DB-TODO [34]: `review` WHERE target_type='DRIVER' aur order ka driver_id = driver_id
        #   -> reviews = [{review_id, order_id, rating, text_review}, ...]

        # DB-TODO [35]: Stats: stats = {"completed": (DELIVERED count), "active": (OUT_FOR_DELIVERY/assigned count),
        #   "total_tips": SUM(tip) of delivered, "avg_rating": AVG(driver reviews)}
        pass

    return render_template(
        "driver.html",
        driver=driver, my_orders=my_orders, open_orders=open_orders,
        history=history, reviews=reviews, stats=stats,
    )


@app.route("/driver/profile", methods=["POST"])
def driver_profile():
    driver_id = clean(request.form.get("driver_id"))
    name = clean(request.form.get("name"))
    contact_no = clean(request.form.get("contact_no"))
    vehicle_no = clean(request.form.get("vehicle_no"))
    current_city = clean(request.form.get("current_city"))  # sirf new registration form me aata hai

    if not (driver_id and name and contact_no and vehicle_no):
        flash("Saari required details bharo.")
        return redirect_driver(driver_id)

    # DB-TODO [36]: Check karo driver_id exist karta hai ya nahi.
    #   - Exist karta hai -> UPDATE driver SET name, contact_no, vehicle_no WHERE driver_id
    #   - Nahi karta      -> INSERT into driver (driver_id, name, contact_no, vehicle_no,
    #                        status='OFFLINE', curr_lat=NULL, curr_long=NULL, current_city)
    #   Variables ready: driver_id, name, contact_no, vehicle_no, current_city

    flash("Driver profile save ho gayi.")
    return redirect_driver(driver_id)


@app.route("/driver/status", methods=["POST"])
def driver_status():
    driver_id = clean(request.form.get("driver_id"))
    status = request.form.get("status")

    if status not in DRIVER_STATUSES:
        flash("Galat status.")
        return redirect_driver(driver_id)

    # DB-TODO [37]: UPDATE driver SET status WHERE driver_id

    flash(f"Status {status} set ho gaya.")
    return redirect_driver(driver_id)


@app.route("/driver/location", methods=["POST"])
def driver_location():
    driver_id = clean(request.form.get("driver_id"))
    current_city = clean(request.form.get("current_city"))
    curr_lat = to_float(request.form.get("curr_lat"))
    curr_long = to_float(request.form.get("curr_long"))

    # DB-TODO [38]: UPDATE driver SET current_city, curr_lat, curr_long WHERE driver_id
    #   (curr_lat / curr_long None ho sakte hain -> NULL store karo)

    flash("Location update ho gayi.")
    return redirect_driver(driver_id)


@app.route("/driver/accept", methods=["POST"])
def driver_accept():
    driver_id = clean(request.form.get("driver_id"))
    order_id = clean(request.form.get("order_id"))

    # DB-TODO [39]: Transaction me:
    #   (a) Check: driver ka status 'AVAILABLE' hai.
    #   (b) UPDATE food_order SET driver_id = driver_id WHERE order_id AND driver_id IS NULL
    #       -> affected rows 0 ho to matlab kisi aur ne pehle accept kar liya; flash karke return karo.
    #   (c) UPDATE driver SET status = 'BUSY' WHERE driver_id
    #   Variables ready: driver_id, order_id

    flash(f"Order {order_id} aapko assign ho gaya.")
    return redirect_driver(driver_id)


@app.route("/driver/order/status", methods=["POST"])
def driver_order_status():
    driver_id = clean(request.form.get("driver_id"))
    order_id = clean(request.form.get("order_id"))
    status = request.form.get("status")

    if status not in DRIVER_ALLOWED_STATUSES:
        flash("Ye status driver set nahi kar sakta.")
        return redirect_driver(driver_id)

    delivery_time = datetime.now() if status == "DELIVERED" else None

    # DB-TODO [40]: UPDATE food_order SET status (aur DELIVERED ho to delivery_time = delivery_time)
    #   WHERE order_id AND driver_id = driver_id   (driver apna hi order badal sake)
    #   DELIVERED ho to: driver ka status wapas 'AVAILABLE' kar do (UPDATE driver ...).
    #   Variables ready: order_id, driver_id, status, delivery_time

    flash(f"Order {order_id} ka status {status} ho gaya.")
    return redirect_driver(driver_id)


# ===========================================================================
# 5. ADMIN  (admin.html)
# ===========================================================================
# DB-TODO [41]: Admin ke liye login/password ya session check yaha laga sakte ho
#   (abhi koi protection nahi hai). Ek @app.before_request hook me /admin ke liye check kar sakte ho.

@app.route("/admin")
def admin_dashboard():
    stats = {}        # dict: customers, hotels, drivers, orders, revenue, avg_rating
    orders = []       # list of dict: order_id, customer_id, customer_name, hotel_id, hotel_name, driver_id,
                      #   driver_name, status, payment_mode, payment_status, total_price, tip,
                      #   discount_pct, coupon, time_of_order, delivery_time
    customers = []    # list of dict: customer_id, name, phone_number
    hotels = []       # list of dict: hotel_id, hotel_name, city, opening_time, closing_time, pin_code
    drivers = []      # list of dict: driver_id, name, contact_no, vehicle_no, status, current_city
    reviews = []      # list of dict: review_id, order_id, target_type, rating, text_review

    # DB-TODO [42]: Stats: COUNT(customer), COUNT(hotel), COUNT(driver), COUNT(food_order),
    #   revenue = SUM(total_price) (DELIVERED orders), avg_rating = AVG(review.rating)
    #   -> stats = {"customers":..., "hotels":..., "drivers":..., "orders":..., "revenue":..., "avg_rating":...}

    # DB-TODO [43]: Saare orders (latest pehle): food_order + customer (name) + hotel (hotel_name)
    #   + driver (name, LEFT JOIN)  -> orders = [...] (upar ke keys)

    # DB-TODO [44]: `customer` table ki saari rows -> customers
    # DB-TODO [45]: `hotel` table ki saari rows -> hotels
    # DB-TODO [46]: `driver` table ki saari rows -> drivers  (orders ke dropdown me bhi yahi use hota hai)
    # DB-TODO [47]: `review` table ki saari rows -> reviews

    return render_template(
        "admin.html",
        stats=stats, orders=orders, customers=customers,
        hotels=hotels, drivers=drivers, reviews=reviews,
    )


@app.route("/admin/order/update", methods=["POST"])
def admin_order_update():
    order_id = clean(request.form.get("order_id"))
    driver_id = clean(request.form.get("driver_id"))   # None = koi driver nahi
    status = request.form.get("status")

    if status not in ORDER_STATUSES:
        flash("Galat status.")
        return redirect("/admin")

    delivery_time = datetime.now() if status == "DELIVERED" else None

    # DB-TODO [48]: UPDATE food_order SET driver_id (NULL bhi ho sakta hai), status
    #   WHERE order_id. Status DELIVERED ho to delivery_time = delivery_time bhi set karo.
    #   Variables ready: order_id, driver_id, status, delivery_time

    flash(f"Order {order_id} update ho gaya.")
    return redirect("/admin")


@app.route("/admin/customer/delete", methods=["POST"])
def admin_customer_delete():
    customer_id = to_int(request.form.get("customer_id"))

    # DB-TODO [49]: DELETE customer (aur uske address). Orders hain to FK error aa sakta hai ->
    #   ON DELETE CASCADE use karo ya error pakad ke flash karo.

    flash("Customer delete ho gaya.")
    return redirect("/admin")


@app.route("/admin/hotel/delete", methods=["POST"])
def admin_hotel_delete():
    hotel_id = clean(request.form.get("hotel_id"))

    # DB-TODO [50]: DELETE hotel (hotel_phone, menu_item bhi hatao ya cascade). Orders ho to error handle karo.

    flash("Hotel delete ho gaya.")
    return redirect("/admin")


@app.route("/admin/driver/delete", methods=["POST"])
def admin_driver_delete():
    driver_id = clean(request.form.get("driver_id"))

    # DB-TODO [51]: DELETE driver. Purane orders me driver_id ho to pehle un orders me driver_id = NULL
    #   karo (ya FK ON DELETE SET NULL use karo).

    flash("Driver delete ho gaya.")
    return redirect("/admin")


@app.route("/admin/review/delete", methods=["POST"])
def admin_review_delete():
    review_id = clean(request.form.get("review_id"))

    # DB-TODO [52]: DELETE from review WHERE review_id

    flash("Review delete ho gaya.")
    return redirect("/admin")


# ===========================================================================

if __name__ == "__main__":
    app.run(debug=True)