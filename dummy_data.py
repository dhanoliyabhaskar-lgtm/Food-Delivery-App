"""
dummy_data.py  -  DEMO ONLY (database ke bina app chalane ke liye)

Ye poori file sirf testing ke liye hai. Data memory me rehta hai, server restart par reset ho jata hai.

DB connect karne ke baad:
  1. Ye file delete kar do.
  2. app.py me `import dummy_data as dummy` hata do aur `USE_DUMMY_DATA = False` kar do
     (ya search "DUMMY-DATA" karke har `if USE_DUMMY_DATA:` block hata do).

------------------------------------------------------------------
DUMMY LOGIN (role dropdown + ID + password)
    U (Customer) : ID 1 (Aarav Sharma)   ID 2 (Priya Verma)
    H (Hotel)    : ID 1 (Spice Garden)   ID 2 (Pizza Corner)   ID 3 (Chai Point)
    D (Driver)   : ID 1 (Ramesh, AVAILABLE)  ID 2 (Suresh, BUSY)  ID 3 (Imran, OFFLINE)
    A (Admin)    : .env wala ADMIN_ID aur PASSWORD
    Sab dummy accounts ka password : demo123
    Dummy coupon : SAVE10 (10% off)
------------------------------------------------------------------
"""
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

NOW = datetime.now()
DEMO_PASSWORD = "demo123"
_DEMO_HASH = generate_password_hash(DEMO_PASSWORD)


def _fmt(dt):
    return dt.strftime("%d %b %Y, %I:%M %p") if dt else None


# ===========================================================================
# DUMMY TABLES (in-memory).  Saare IDs integer / auto-increment style
# ===========================================================================

# `password` column (hashed) - role -> {id: hash}
PASSWORDS = {
    "customer": {1: _DEMO_HASH, 2: _DEMO_HASH},
    "hotel": {1: _DEMO_HASH, 2: _DEMO_HASH, 3: _DEMO_HASH},
    "driver": {1: _DEMO_HASH, 2: _DEMO_HASH, 3: _DEMO_HASH},
}

CUSTOMERS = {
    1: {"customer_id": 1, "name": "Aarav Sharma", "phone_number": 9876543210},
    2: {"customer_id": 2, "name": "Priya Verma", "phone_number": 9123456780},
}

ADDRESSES = {
    1: [
        {"address_id": 1, "house": "12-A", "street": "Sector 1 Main Road", "city": "Pithampur",
         "geo_lat": 22.6120, "geo_long": 75.6850, "pin_code": 454775},
        {"address_id": 2, "house": "Plot 45", "street": "Industrial Area", "city": "Pithampur",
         "geo_lat": 22.6250, "geo_long": 75.6900, "pin_code": 454774},
    ],
    2: [
        {"address_id": 1, "house": "B-7", "street": "Shanti Nagar", "city": "Indore",
         "geo_lat": 22.7196, "geo_long": 75.8577, "pin_code": 452001},
    ],
}

HOTELS = {
    1: {"hotel_id": 1, "hotel_name": "Spice Garden", "opening_time": "09:00", "closing_time": "23:00",
        "city": "Pithampur", "street": "Main Market", "geo_lat": 22.6103, "geo_long": 75.6836, "pin_code": 454775},
    2: {"hotel_id": 2, "hotel_name": "Pizza Corner", "opening_time": "11:00", "closing_time": "23:30",
        "city": "Pithampur", "street": "Bus Stand Road", "geo_lat": 22.6150, "geo_long": 75.6800, "pin_code": 454775},
    3: {"hotel_id": 3, "hotel_name": "Chai Point", "opening_time": "07:00", "closing_time": "21:00",
        "city": "Indore", "street": "Vijay Nagar", "geo_lat": 22.7533, "geo_long": 75.8937, "pin_code": 452010},
}

HOTEL_PHONES = {1: ["9876500001", "07292-400001"], 2: ["9876500002"], 3: ["9876500003"]}

MENU = {
    1: [
        {"item_id": 1, "name": "Paneer Tikka", "category": "Starter", "price": 220.0, "availability": 1},
        {"item_id": 2, "name": "Dal Makhani", "category": "Main Course", "price": 260.0, "availability": 1},
        {"item_id": 3, "name": "Butter Naan", "category": "Main Course", "price": 45.0, "availability": 1},
        {"item_id": 4, "name": "Gulab Jamun", "category": "Dessert", "price": 80.0, "availability": 1},
        {"item_id": 5, "name": "Masala Chaas", "category": "Beverage", "price": 40.0, "availability": 0},
    ],
    2: [
        {"item_id": 1, "name": "Margherita Pizza", "category": "Main Course", "price": 299.0, "availability": 1},
        {"item_id": 2, "name": "Garlic Bread", "category": "Snack", "price": 129.0, "availability": 1},
        {"item_id": 3, "name": "Cold Coffee", "category": "Beverage", "price": 99.0, "availability": 1},
    ],
    3: [
        {"item_id": 1, "name": "Masala Chai", "category": "Beverage", "price": 30.0, "availability": 1},
        {"item_id": 2, "name": "Samosa", "category": "Snack", "price": 25.0, "availability": 1},
        {"item_id": 3, "name": "Veg Sandwich", "category": "Snack", "price": 70.0, "availability": 1},
    ],
}

DRIVERS = {
    1: {"driver_id": 1, "name": "Ramesh Kumar", "contact_no": "9811111111", "vehicle_no": "MP09 AB 1234",
        "status": "AVAILABLE", "curr_lat": 22.6110, "curr_long": 75.6840, "current_city": "Pithampur"},
    2: {"driver_id": 2, "name": "Suresh Patil", "contact_no": "9822222222", "vehicle_no": "MP09 CD 5678",
        "status": "BUSY", "curr_lat": 22.6200, "curr_long": 75.6880, "current_city": "Pithampur"},
    3: {"driver_id": 3, "name": "Imran Khan", "contact_no": "9833333333", "vehicle_no": "MP10 EF 9012",
        "status": "OFFLINE", "curr_lat": None, "curr_long": None, "current_city": "Indore"},
}


def _line(item_id, qty, price, remarks=None):
    return {"item_id": item_id, "quantity": qty, "price_at_order": price, "remarks": remarks}


def _order(oid, cust, hotel, driver, addr, status, mode, pstatus, total, tip, placed, delivered, lines):
    return {"order_id": oid, "customer_id": cust, "hotel_id": hotel, "driver_id": driver, "address_id": addr,
            "status": status, "payment_id": None if mode == "CASH" else f"PAY-{oid}", "payment_mode": mode,
            "payment_status": pstatus, "total_price": total, "tip": tip, "discount_pct": 0.0, "coupon": None,
            "time_of_order": placed, "delivery_time": delivered, "lines": lines}


ORDERS = [
    _order("ORD-DEMO-001", 1, 1, 1, 1, "OUT_FOR_DELIVERY", "UPI", "PAID", 620.0, 30.0,
           NOW - timedelta(minutes=40), None, [_line(1, 2, 220.0, "Less spicy"), _line(3, 4, 45.0)]),
    _order("ORD-DEMO-002", 1, 2, None, 2, "PLACED", "CASH", "PENDING", 428.0, 20.0,
           NOW - timedelta(minutes=5), None, [_line(1, 1, 299.0, "Extra cheese"), _line(2, 1, 129.0)]),
    _order("ORD-DEMO-003", 1, 1, 1, 1, "DELIVERED", "CARD", "PAID", 260.0, 10.0,
           NOW - timedelta(days=1, hours=2), NOW - timedelta(days=1, hours=1), [_line(2, 1, 260.0)]),
    _order("ORD-DEMO-004", 2, 1, None, 1, "READY", "CASH", "PENDING", 300.0, 15.0,
           NOW - timedelta(minutes=25), None, [_line(1, 1, 220.0), _line(4, 1, 80.0, "Serve warm")]),
    _order("ORD-DEMO-005", 2, 3, 2, 1, "OUT_FOR_DELIVERY", "UPI", "PAID", 125.0, 5.0,
           NOW - timedelta(minutes=30), None, [_line(1, 1, 30.0), _line(2, 1, 25.0), _line(3, 1, 70.0)]),
    # --- purane orders (hotel History page ke liye) ---
    _order("ORD-DEMO-006", 2, 1, 1, 1, "DELIVERED", "UPI", "PAID", 305.0, 20.0,
           NOW - timedelta(days=7), NOW - timedelta(days=7) + timedelta(minutes=45),
           [_line(1, 1, 220.0), _line(3, 1, 45.0), _line(5, 1, 40.0)]),
    _order("ORD-DEMO-007", 1, 1, None, 1, "CANCELLED", "CASH", "PENDING", 80.0, 0.0,
           NOW - timedelta(days=12), None, [_line(4, 1, 80.0)]),
    _order("ORD-DEMO-008", 1, 1, 1, 1, "DELIVERED", "CARD", "PAID", 260.0, 10.0,
           NOW - timedelta(days=45), NOW - timedelta(days=45) + timedelta(minutes=50),
           [_line(2, 1, 260.0)]),  # 30 din se purana -> History me nahi dikhega
]

REVIEWS = [
    {"review_id": "REV-DEMO-001", "order_id": "ORD-DEMO-003", "target_type": "HOTEL", "rating": 5,
     "text_review": "Dal Makhani was fantastic, will order again."},
    {"review_id": "REV-DEMO-002", "order_id": "ORD-DEMO-003", "target_type": "DRIVER", "rating": 4,
     "text_review": "Delivered on time, polite driver."},
]

# ===========================================================================
# Helpers
# ===========================================================================

FINISHED = ("DELIVERED", "CANCELLED")


def _find_order(order_id):
    return next((o for o in ORDERS if o["order_id"] == order_id), None)


def _item_name(hotel_id, item_id):
    for m in MENU.get(hotel_id, []):
        if m["item_id"] == item_id:
            return m["name"]
    return f"Item {item_id}"


def _order_items(o):
    return [{"item_name": _item_name(o["hotel_id"], l["item_id"]), "quantity": l["quantity"],
             "remarks": l["remarks"]} for l in o["lines"]]


def _hotel_name(hotel_id):
    return HOTELS.get(hotel_id, {}).get("hotel_name", "(deleted hotel)")


def _customer_name(customer_id):
    return CUSTOMERS.get(customer_id, {}).get("name", "(deleted customer)")


def _driver_name(driver_id):
    d = DRIVERS.get(driver_id)
    return d["name"] if d else None


def _address(customer_id, address_id):
    return next((a for a in ADDRESSES.get(customer_id, []) if a["address_id"] == address_id), {})


def _avg(values):
    return round(sum(values) / len(values), 1) if values else None


def _next_id(table):
    return max(table, default=0) + 1


# ===========================================================================
# LOGIN
# ===========================================================================

def get_login(role, user_id):
    """(password_hash, display_name) ya (None, None) agar account nahi mila."""
    h = PASSWORDS.get(role, {}).get(user_id)
    if not h:
        return None, None
    if role == "customer":
        return h, CUSTOMERS[user_id]["name"]
    if role == "hotel":
        return h, HOTELS[user_id]["hotel_name"]
    return h, DRIVERS[user_id]["name"]


# ===========================================================================
# CUSTOMER
# ===========================================================================

def save_customer(name, phone_number, password_hash):
    cid = _next_id(CUSTOMERS)
    CUSTOMERS[cid] = {"customer_id": cid, "name": name, "phone_number": phone_number}
    ADDRESSES[cid] = []
    PASSWORDS["customer"][cid] = password_hash
    return cid


def update_customer(customer_id, name, phone_number, new_hash):
    if customer_id in CUSTOMERS:
        CUSTOMERS[customer_id].update({"name": name, "phone_number": phone_number})
        if new_hash:
            PASSWORDS["customer"][customer_id] = new_hash


def user_menu_page(customer_id, hotel_id):
    if hotel_id not in HOTELS:
        hotel_id = next(iter(HOTELS), None)  # pehla hotel default select
    selected = HOTELS.get(hotel_id)
    return {"hotels": list(HOTELS.values()), "selected_hotel": selected,
            "menu_items": list(MENU.get(hotel_id, [])) if selected else [],
            "addresses": list(ADDRESSES.get(customer_id, []))}


def user_orders_page(customer_id):
    active, past = [], []
    for o in reversed(ORDERS):
        if o["customer_id"] != customer_id:
            continue
        d = DRIVERS.get(o["driver_id"]) or {}
        row = {"order_id": o["order_id"], "hotel_name": _hotel_name(o["hotel_id"]), "driver_name": d.get("name"),
               "contact_no": d.get("contact_no"), "vehicle_no": d.get("vehicle_no"), "status": o["status"],
               "total_price": o["total_price"], "tip": o["tip"], "payment_mode": o["payment_mode"],
               "time_of_order": _fmt(o["time_of_order"]), "delivery_time": _fmt(o["delivery_time"]),
               "order_items": _order_items(o)}
        (past if o["status"] in FINISHED else active).append(row)
    return {"active_orders": active, "past_orders": past}


def user_reviews_page(customer_id):
    mine = {o["order_id"]: o for o in ORDERS if o["customer_id"] == customer_id}
    delivered = [{"order_id": o["order_id"], "hotel_name": _hotel_name(o["hotel_id"]),
                  "driver_name": _driver_name(o["driver_id"])}
                 for o in reversed(list(mine.values())) if o["status"] == "DELIVERED"]
    my_reviews = [{"review_id": r["review_id"], "order_id": r["order_id"], "target_type": r["target_type"],
                   "hotel_name": _hotel_name(mine[r["order_id"]]["hotel_id"]), "rating": r["rating"],
                   "text_review": r["text_review"]} for r in REVIEWS if r["order_id"] in mine]
    return {"delivered_orders": delivered, "my_reviews": my_reviews}


def user_profile_page(customer_id):
    return {"customer": CUSTOMERS.get(customer_id), "addresses": list(ADDRESSES.get(customer_id, []))}


def add_address(customer_id, house, street, city, pin_code, geo_lat, geo_long):
    lst = ADDRESSES.setdefault(customer_id, [])
    lst.append({"address_id": max((a["address_id"] for a in lst), default=0) + 1, "house": house,
                "street": street, "city": city, "geo_lat": geo_lat, "geo_long": geo_long, "pin_code": pin_code})


def place_order(customer_id, hotel_id, address_id, coupon, tip, payment_mode, lines):
    if hotel_id not in HOTELS:
        return {"ok": False, "message": "Hotel nahi mila."}
    subtotal, saved = 0.0, []
    for l in lines:
        item = next((m for m in MENU.get(hotel_id, []) if m["item_id"] == l["item_id"]), None)
        if not item or not item["availability"]:
            return {"ok": False, "message": "Koi item available nahi hai. Cart check karo."}
        subtotal += item["price"] * l["quantity"]
        saved.append({**l, "price_at_order": item["price"]})
    discount = 10.0 if (coupon or "").upper() == "SAVE10" else 0.0
    if coupon and not discount:
        return {"ok": False, "message": "Coupon invalid hai. (Dummy coupon: SAVE10)"}
    order_id = f"ORD-DEMO-{len(ORDERS) + 1:03d}"
    o = _order(order_id, customer_id, hotel_id, None, address_id, "PLACED", payment_mode,
               "PENDING" if payment_mode == "CASH" else "PAID", round(subtotal * (1 - discount / 100), 2),
               tip, datetime.now(), None, saved)
    o["discount_pct"], o["coupon"] = discount, (coupon or None)
    ORDERS.append(o)
    return {"ok": True, "message": f"Order place ho gaya! Order ID: {order_id}"}


def add_review(order_id, target_type, rating, text_review):
    REVIEWS.append({"review_id": f"REV-DEMO-{len(REVIEWS) + 1:03d}", "order_id": order_id,
                    "target_type": target_type, "rating": rating, "text_review": text_review})
    return "Review submit ho gaya. Shukriya!"


# ===========================================================================
# HOTEL
# ===========================================================================

def save_hotel(hotel_name, opening_time, closing_time, street, city, pin_code, geo_lat, geo_long, password_hash):
    hid = _next_id(HOTELS)
    HOTELS[hid] = {"hotel_id": hid, "hotel_name": hotel_name, "opening_time": opening_time,
                   "closing_time": closing_time, "city": city, "street": street,
                   "geo_lat": geo_lat, "geo_long": geo_long, "pin_code": pin_code}
    HOTEL_PHONES[hid], MENU[hid] = [], []
    PASSWORDS["hotel"][hid] = password_hash
    return hid


def update_hotel(hotel_id, hotel_name, opening_time, closing_time, street, city, pin_code, geo_lat, geo_long, new_hash):
    if hotel_id in HOTELS:
        HOTELS[hotel_id].update({"hotel_name": hotel_name, "opening_time": opening_time,
                                 "closing_time": closing_time, "street": street, "city": city,
                                 "pin_code": pin_code, "geo_lat": geo_lat, "geo_long": geo_long})
        if new_hash:
            PASSWORDS["hotel"][hotel_id] = new_hash


def hotel_orders_page(hotel_id):
    mine = [o for o in ORDERS if o["hotel_id"] == hotel_id]
    active = [{"order_id": o["order_id"], "customer_name": _customer_name(o["customer_id"]),
               "status": o["status"], "total_price": o["total_price"], "time_of_order": _fmt(o["time_of_order"]),
               "driver_name": _driver_name(o["driver_id"]), "order_items": _order_items(o)}
              for o in reversed(mine) if o["status"] not in FINISHED]
    ids = {o["order_id"] for o in mine}
    ratings = [r["rating"] for r in REVIEWS if r["target_type"] == "HOTEL" and r["order_id"] in ids]
    stats = {"total_orders": len(mine), "pending_orders": sum(1 for o in mine if o["status"] == "PLACED"),
             "avg_rating": _avg(ratings), "menu_count": len(MENU.get(hotel_id, []))}
    return {"orders": active, "stats": stats}


def hotel_menu_page(hotel_id):
    return {"menu_items": list(MENU.get(hotel_id, []))}


def hotel_history_page(hotel_id):
    cutoff = datetime.now() - timedelta(days=30)
    rows = [o for o in reversed(ORDERS) if o["hotel_id"] == hotel_id and o["status"] in FINISHED
            and o["time_of_order"] >= cutoff]
    orders = [{"order_id": o["order_id"], "customer_name": _customer_name(o["customer_id"]),
               "status": o["status"], "total_price": o["total_price"], "tip": o["tip"],
               "time_of_order": _fmt(o["time_of_order"]), "delivery_time": _fmt(o["delivery_time"]),
               "order_items": _order_items(o)} for o in rows]
    done = [o for o in rows if o["status"] == "DELIVERED"]
    summary = {"count": len(rows), "delivered": len(done), "cancelled": len(rows) - len(done),
               "revenue": round(sum(o["total_price"] for o in done), 2)}
    return {"orders": orders, "summary": summary}


def hotel_reviews_page(hotel_id):
    ids = {o["order_id"] for o in ORDERS if o["hotel_id"] == hotel_id}
    reviews = [r for r in REVIEWS if r["target_type"] == "HOTEL" and r["order_id"] in ids]
    return {"reviews": reviews, "avg_rating": _avg([r["rating"] for r in reviews])}


def hotel_profile_page(hotel_id):
    return {"hotel": HOTELS.get(hotel_id), "phones": [{"phone_no": p} for p in HOTEL_PHONES.get(hotel_id, [])]}


def add_phone(hotel_id, phone_no):
    lst = HOTEL_PHONES.setdefault(hotel_id, [])
    if phone_no not in lst:
        lst.append(phone_no)


def delete_phone(hotel_id, phone_no):
    if phone_no in HOTEL_PHONES.get(hotel_id, []):
        HOTEL_PHONES[hotel_id].remove(phone_no)


def add_menu_item(hotel_id, name, category, price, availability):
    lst = MENU.setdefault(hotel_id, [])
    lst.append({"item_id": max((m["item_id"] for m in lst), default=0) + 1, "name": name,
                "category": category, "price": price, "availability": availability})


def update_menu_item(hotel_id, item_id, price, availability):
    for m in MENU.get(hotel_id, []):
        if m["item_id"] == item_id:
            m["price"], m["availability"] = price, availability


def delete_menu_item(hotel_id, item_id):
    MENU[hotel_id] = [m for m in MENU.get(hotel_id, []) if m["item_id"] != item_id]


def set_order_status(order_id, status, hotel_id=None, driver_id=None):
    """Hotel / driver / admin teeno isi se order ka status badalte hain."""
    o = _find_order(order_id)
    if not o:
        return
    if hotel_id is not None and o["hotel_id"] != hotel_id:
        return  # hotel sirf apna order badal sakta hai
    if driver_id is not None and o["driver_id"] != driver_id:
        return  # driver sirf apna order badal sakta hai
    o["status"] = status
    if status == "DELIVERED":
        o["delivery_time"] = datetime.now()
        if o["payment_mode"] == "CASH":
            o["payment_status"] = "PAID"
        if o["driver_id"] in DRIVERS:
            DRIVERS[o["driver_id"]]["status"] = "AVAILABLE"


# ===========================================================================
# DRIVER
# ===========================================================================

def save_driver(name, contact_no, vehicle_no, current_city, password_hash):
    did = _next_id(DRIVERS)
    DRIVERS[did] = {"driver_id": did, "name": name, "contact_no": contact_no, "vehicle_no": vehicle_no,
                    "status": "OFFLINE", "curr_lat": None, "curr_long": None, "current_city": current_city}
    PASSWORDS["driver"][did] = password_hash
    return did


def update_driver(driver_id, name, contact_no, vehicle_no, new_hash):
    if driver_id in DRIVERS:
        DRIVERS[driver_id].update({"name": name, "contact_no": contact_no, "vehicle_no": vehicle_no})
        if new_hash:
            PASSWORDS["driver"][driver_id] = new_hash


def _driver_stats(driver_id):
    mine = [o for o in ORDERS if o["driver_id"] == driver_id]
    done = [o for o in mine if o["status"] == "DELIVERED"]
    ids = {o["order_id"] for o in mine}
    ratings = [r["rating"] for r in REVIEWS if r["target_type"] == "DRIVER" and r["order_id"] in ids]
    return {"completed": len(done), "active": sum(1 for o in mine if o["status"] not in FINISHED),
            "total_tips": sum(o["tip"] for o in done), "avg_rating": _avg(ratings)}


def driver_deliveries_page(driver_id):
    my_orders = []
    for o in reversed(ORDERS):
        if o["driver_id"] != driver_id or o["status"] in FINISHED:
            continue
        h = HOTELS.get(o["hotel_id"], {})
        a = _address(o["customer_id"], o["address_id"])
        phones = HOTEL_PHONES.get(o["hotel_id"], [])
        my_orders.append({
            "order_id": o["order_id"], "status": o["status"], "total_price": o["total_price"], "tip": o["tip"],
            "payment_mode": o["payment_mode"], "payment_status": o["payment_status"],
            "hotel_name": h.get("hotel_name"), "hotel_street": h.get("street"), "hotel_city": h.get("city"),
            "hotel_phone": phones[0] if phones else None, "hotel_lat": h.get("geo_lat"), "hotel_long": h.get("geo_long"),
            "customer_name": _customer_name(o["customer_id"]),
            "customer_phone": CUSTOMERS.get(o["customer_id"], {}).get("phone_number"),
            "house": a.get("house"), "street": a.get("street"), "city": a.get("city"), "pin_code": a.get("pin_code"),
            "drop_lat": a.get("geo_lat"), "drop_long": a.get("geo_long"), "order_items": _order_items(o)})
    return {"driver": DRIVERS.get(driver_id), "my_orders": my_orders, "stats": _driver_stats(driver_id)}


def driver_open_page(driver_id):
    open_orders = []
    for o in reversed(ORDERS):
        if o["status"] == "READY" and o["driver_id"] is None:
            h = HOTELS.get(o["hotel_id"], {})
            a = _address(o["customer_id"], o["address_id"])
            open_orders.append({"order_id": o["order_id"], "hotel_name": h.get("hotel_name"),
                                "hotel_street": h.get("street"), "hotel_city": h.get("city"),
                                "city": a.get("city"), "total_price": o["total_price"], "tip": o["tip"],
                                "order_items": _order_items(o)})
    return {"driver": DRIVERS.get(driver_id), "open_orders": open_orders}


def driver_availability_page(driver_id):
    return {"driver": DRIVERS.get(driver_id)}


def driver_history_page(driver_id):
    done = [o for o in reversed(ORDERS) if o["driver_id"] == driver_id and o["status"] == "DELIVERED"]
    history = [{"order_id": o["order_id"], "hotel_name": _hotel_name(o["hotel_id"]),
                "customer_name": _customer_name(o["customer_id"]), "total_price": o["total_price"],
                "tip": o["tip"], "delivery_time": _fmt(o["delivery_time"])} for o in done]
    return {"history": history, "stats": _driver_stats(driver_id)}


def driver_reviews_page(driver_id):
    ids = {o["order_id"] for o in ORDERS if o["driver_id"] == driver_id}
    reviews = [r for r in REVIEWS if r["target_type"] == "DRIVER" and r["order_id"] in ids]
    return {"reviews": reviews, "avg_rating": _avg([r["rating"] for r in reviews])}


def driver_profile_page(driver_id):
    return {"driver": DRIVERS.get(driver_id)}


def set_driver_status(driver_id, status):
    if driver_id in DRIVERS:
        DRIVERS[driver_id]["status"] = status


def set_driver_location(driver_id, current_city, curr_lat, curr_long):
    if driver_id in DRIVERS:
        DRIVERS[driver_id].update({"current_city": current_city, "curr_lat": curr_lat, "curr_long": curr_long})


def accept_order(driver_id, order_id):
    o, d = _find_order(order_id), DRIVERS.get(driver_id)
    if not o or not d:
        return "Order ya driver nahi mila."
    if d["status"] != "AVAILABLE":
        return "Pehle apna status Available karo."
    if o["driver_id"] is not None:
        return "Ye order kisi aur driver ne le liya."
    o["driver_id"], d["status"] = driver_id, "BUSY"
    return f"Order {order_id} aapko assign ho gaya."


# ===========================================================================
# ADMIN
# ===========================================================================

def admin_dashboard():
    orders = [{
        "order_id": o["order_id"], "customer_id": o["customer_id"], "customer_name": _customer_name(o["customer_id"]),
        "hotel_id": o["hotel_id"], "hotel_name": _hotel_name(o["hotel_id"]), "driver_id": o["driver_id"],
        "driver_name": _driver_name(o["driver_id"]), "status": o["status"], "payment_mode": o["payment_mode"],
        "payment_status": o["payment_status"], "total_price": o["total_price"], "tip": o["tip"],
        "discount_pct": o["discount_pct"], "coupon": o["coupon"], "time_of_order": _fmt(o["time_of_order"]),
        "delivery_time": _fmt(o["delivery_time"]),
    } for o in reversed(ORDERS)]
    stats = {"customers": len(CUSTOMERS), "hotels": len(HOTELS), "drivers": len(DRIVERS), "orders": len(ORDERS),
             "revenue": round(sum(o["total_price"] for o in ORDERS if o["status"] == "DELIVERED"), 2),
             "avg_rating": _avg([r["rating"] for r in REVIEWS])}
    return {"stats": stats, "orders": orders, "customers": list(CUSTOMERS.values()),
            "hotels": list(HOTELS.values()), "drivers": list(DRIVERS.values()), "reviews": list(REVIEWS)}


def admin_update_order(order_id, driver_id, status):
    o = _find_order(order_id)
    if o:
        o["driver_id"] = driver_id if driver_id in DRIVERS else None
        set_order_status(order_id, status)


def delete_customer(customer_id):
    CUSTOMERS.pop(customer_id, None)
    ADDRESSES.pop(customer_id, None)
    PASSWORDS["customer"].pop(customer_id, None)


def delete_hotel(hotel_id):
    for table in (HOTELS, HOTEL_PHONES, MENU, PASSWORDS["hotel"]):
        table.pop(hotel_id, None)


def delete_driver(driver_id):
    DRIVERS.pop(driver_id, None)
    PASSWORDS["driver"].pop(driver_id, None)
    for o in ORDERS:
        if o["driver_id"] == driver_id:
            o["driver_id"] = None


def delete_review(review_id):
    REVIEWS[:] = [r for r in REVIEWS if r["review_id"] != review_id]