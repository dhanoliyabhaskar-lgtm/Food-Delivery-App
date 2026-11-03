"""
dummy_data.py  -  DEMO ONLY (database ke bina app chalane ke liye)

Ye poori file sirf testing ke liye hai. Data memory me rehta hai, server restart par reset ho jata hai.

DB connect karne ke baad:
  1. Is file ko delete kar do (dummy_data.py).
  2. app.py me `USE_DUMMY_DATA = True` ko False karo (ya "DUMMY-DATA" comment wale saare blocks hata do).
     Search karo: "DUMMY-DATA"  -> har jagah jaha dummy data use hua hai wahan ye comment hai.

------------------------------------------------------------------
DUMMY LOGIN IDs
    Customer : 1   (Aarav Sharma, 2 addresses, 3 orders)
               2   (Priya Verma, 1 address, 2 orders)
    Hotel    : H001 (Spice Garden)   H002 (Pizza Corner)   H003 (Chai Point)
    Driver   : D001 (Ramesh Kumar, AVAILABLE)  D002 (Suresh Patil, BUSY)  D003 (Imran Khan, OFFLINE)
    Admin    : koi ID nahi, seedha "Open admin dashboard"
    Coupon   : SAVE10  (10% discount, dummy)
------------------------------------------------------------------
"""
from datetime import datetime, timedelta

NOW = datetime.now()


def _fmt(dt):
    return dt.strftime("%d %b %Y, %I:%M %p") if dt else None


# ===========================================================================
# DUMMY TABLES (in-memory)
# ===========================================================================

# customer table
CUSTOMERS = {
    1: {"customer_id": 1, "name": "Aarav Sharma", "phone_number": 9876543210},
    2: {"customer_id": 2, "name": "Priya Verma", "phone_number": 9123456780},
}

# address table  (customer_id -> list of addresses)
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

# hotel table
HOTELS = {
    "H001": {"hotel_id": "H001", "hotel_name": "Spice Garden", "opening_time": "09:00", "closing_time": "23:00",
             "city": "Pithampur", "street": "Main Market", "geo_lat": 22.6103, "geo_long": 75.6836, "pin_code": 454775},
    "H002": {"hotel_id": "H002", "hotel_name": "Pizza Corner", "opening_time": "11:00", "closing_time": "23:30",
             "city": "Pithampur", "street": "Bus Stand Road", "geo_lat": 22.6150, "geo_long": 75.6800, "pin_code": 454775},
    "H003": {"hotel_id": "H003", "hotel_name": "Chai Point", "opening_time": "07:00", "closing_time": "21:00",
             "city": "Indore", "street": "Vijay Nagar", "geo_lat": 22.7533, "geo_long": 75.8937, "pin_code": 452010},
}

# hotel_phone table
HOTEL_PHONES = {
    "H001": ["9876500001", "07292-400001"],
    "H002": ["9876500002"],
    "H003": ["9876500003"],
}

# menu_item table
MENU = {
    "H001": [
        {"item_id": 1, "name": "Paneer Tikka", "category": "Starter", "price": 220.0, "availability": 1},
        {"item_id": 2, "name": "Dal Makhani", "category": "Main Course", "price": 260.0, "availability": 1},
        {"item_id": 3, "name": "Butter Naan", "category": "Main Course", "price": 45.0, "availability": 1},
        {"item_id": 4, "name": "Gulab Jamun", "category": "Dessert", "price": 80.0, "availability": 1},
        {"item_id": 5, "name": "Masala Chaas", "category": "Beverage", "price": 40.0, "availability": 0},
    ],
    "H002": [
        {"item_id": 1, "name": "Margherita Pizza", "category": "Main Course", "price": 299.0, "availability": 1},
        {"item_id": 2, "name": "Garlic Bread", "category": "Snack", "price": 129.0, "availability": 1},
        {"item_id": 3, "name": "Cold Coffee", "category": "Beverage", "price": 99.0, "availability": 1},
    ],
    "H003": [
        {"item_id": 1, "name": "Masala Chai", "category": "Beverage", "price": 30.0, "availability": 1},
        {"item_id": 2, "name": "Samosa", "category": "Snack", "price": 25.0, "availability": 1},
        {"item_id": 3, "name": "Veg Sandwich", "category": "Snack", "price": 70.0, "availability": 1},
    ],
}

# driver table
DRIVERS = {
    "D001": {"driver_id": "D001", "name": "Ramesh Kumar", "contact_no": "9811111111", "vehicle_no": "MP09 AB 1234",
             "status": "AVAILABLE", "curr_lat": 22.6110, "curr_long": 75.6840, "current_city": "Pithampur"},
    "D002": {"driver_id": "D002", "name": "Suresh Patil", "contact_no": "9822222222", "vehicle_no": "MP09 CD 5678",
             "status": "BUSY", "curr_lat": 22.6200, "curr_long": 75.6880, "current_city": "Pithampur"},
    "D003": {"driver_id": "D003", "name": "Imran Khan", "contact_no": "9833333333", "vehicle_no": "MP10 EF 9012",
             "status": "OFFLINE", "curr_lat": None, "curr_long": None, "current_city": "Indore"},
}


def _line(item_id, qty, price, remarks=None):
    return {"item_id": item_id, "quantity": qty, "price_at_order": price, "remarks": remarks}


# food_order + order_item (lines) tables
ORDERS = [
    {"order_id": "ORD-DEMO-001", "customer_id": 1, "hotel_id": "H001", "driver_id": "D001", "address_id": 1,
     "status": "OUT_FOR_DELIVERY", "payment_id": "PAY-DEMO-001", "payment_mode": "UPI", "payment_status": "PAID",
     "total_price": 620.0, "tip": 30.0, "discount_pct": 0.0, "coupon": None,
     "time_of_order": NOW - timedelta(minutes=40), "delivery_time": None,
     "lines": [_line(1, 2, 220.0, "Less spicy"), _line(3, 4, 45.0)]},
    {"order_id": "ORD-DEMO-002", "customer_id": 1, "hotel_id": "H002", "driver_id": None, "address_id": 2,
     "status": "PLACED", "payment_id": None, "payment_mode": "CASH", "payment_status": "PENDING",
     "total_price": 428.0, "tip": 20.0, "discount_pct": 0.0, "coupon": None,
     "time_of_order": NOW - timedelta(minutes=5), "delivery_time": None,
     "lines": [_line(1, 1, 299.0, "Extra cheese"), _line(2, 1, 129.0)]},
    {"order_id": "ORD-DEMO-003", "customer_id": 1, "hotel_id": "H001", "driver_id": "D001", "address_id": 1,
     "status": "DELIVERED", "payment_id": "PAY-DEMO-003", "payment_mode": "CARD", "payment_status": "PAID",
     "total_price": 260.0, "tip": 10.0, "discount_pct": 0.0, "coupon": None,
     "time_of_order": NOW - timedelta(days=1, hours=2), "delivery_time": NOW - timedelta(days=1, hours=1),
     "lines": [_line(2, 1, 260.0)]},
    {"order_id": "ORD-DEMO-004", "customer_id": 2, "hotel_id": "H001", "driver_id": None, "address_id": 1,
     "status": "READY", "payment_id": None, "payment_mode": "CASH", "payment_status": "PENDING",
     "total_price": 300.0, "tip": 15.0, "discount_pct": 0.0, "coupon": None,
     "time_of_order": NOW - timedelta(minutes=25), "delivery_time": None,
     "lines": [_line(1, 1, 220.0), _line(4, 1, 80.0, "Serve warm")]},
    {"order_id": "ORD-DEMO-005", "customer_id": 2, "hotel_id": "H003", "driver_id": "D002", "address_id": 1,
     "status": "OUT_FOR_DELIVERY", "payment_id": "PAY-DEMO-005", "payment_mode": "UPI", "payment_status": "PAID",
     "total_price": 125.0, "tip": 5.0, "discount_pct": 0.0, "coupon": None,
     "time_of_order": NOW - timedelta(minutes=30), "delivery_time": None,
     "lines": [_line(1, 1, 30.0), _line(2, 1, 25.0), _line(3, 1, 70.0)]},
]

# review table
REVIEWS = [
    {"review_id": "REV-DEMO-001", "order_id": "ORD-DEMO-003", "target_type": "HOTEL", "rating": 5,
     "text_review": "Dal Makhani was fantastic, will order again."},
    {"review_id": "REV-DEMO-002", "order_id": "ORD-DEMO-003", "target_type": "DRIVER", "rating": 4,
     "text_review": "Delivered on time, polite driver."},
]


# ===========================================================================
# Small helpers
# ===========================================================================

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


# ===========================================================================
# CUSTOMER
# ===========================================================================

def user_dashboard(customer_id, hotel_id):
    customer = CUSTOMERS.get(customer_id)
    selected = HOTELS.get(hotel_id) if hotel_id else None
    active, delivered = [], []
    for o in reversed(ORDERS):
        if o["customer_id"] != customer_id:
            continue
        d = DRIVERS.get(o["driver_id"]) or {}
        if o["status"] == "DELIVERED":
            delivered.append({"order_id": o["order_id"], "hotel_name": _hotel_name(o["hotel_id"]),
                              "driver_name": d.get("name")})
        elif o["status"] != "CANCELLED":
            active.append({"order_id": o["order_id"], "hotel_name": _hotel_name(o["hotel_id"]),
                           "driver_name": d.get("name"), "contact_no": d.get("contact_no"),
                           "vehicle_no": d.get("vehicle_no"), "status": o["status"],
                           "total_price": o["total_price"], "time_of_order": _fmt(o["time_of_order"])})
    return {
        "customer": customer,
        "addresses": list(ADDRESSES.get(customer_id, [])),
        "hotels": list(HOTELS.values()),
        "selected_hotel": selected,
        "menu_items": list(MENU.get(hotel_id, [])) if selected else [],
        "active_orders": active,
        "delivered_orders": delivered,
    }


def user_register(customer_id):
    return CUSTOMERS.get(customer_id), list(ADDRESSES.get(customer_id, []))


def save_customer(customer_id, name, phone_number):
    if not customer_id or customer_id not in CUSTOMERS:
        customer_id = max(CUSTOMERS, default=0) + 1
        ADDRESSES[customer_id] = []
    CUSTOMERS[customer_id] = {"customer_id": customer_id, "name": name, "phone_number": phone_number}
    return customer_id


def add_address(customer_id, house, street, city, pin_code, geo_lat, geo_long):
    lst = ADDRESSES.setdefault(customer_id, [])
    new_id = max((a["address_id"] for a in lst), default=0) + 1
    lst.append({"address_id": new_id, "house": house, "street": street, "city": city,
                "geo_lat": geo_lat, "geo_long": geo_long, "pin_code": pin_code})


def place_order(customer_id, hotel_id, address_id, coupon, tip, payment_mode, lines):
    if hotel_id not in HOTELS:
        return {"ok": False, "message": "Hotel nahi mila."}
    subtotal, saved_lines = 0.0, []
    for l in lines:
        item = next((m for m in MENU.get(hotel_id, []) if m["item_id"] == l["item_id"]), None)
        if not item or not item["availability"]:
            return {"ok": False, "message": "Koi item available nahi hai. Cart check karo."}
        subtotal += item["price"] * l["quantity"]
        saved_lines.append({**l, "price_at_order": item["price"]})
    discount = 10.0 if (coupon or "").upper() == "SAVE10" else 0.0
    if coupon and not discount:
        return {"ok": False, "message": "Coupon invalid hai. (Dummy coupon: SAVE10)"}
    order_id = f"ORD-DEMO-{len(ORDERS) + 1:03d}"
    ORDERS.append({
        "order_id": order_id, "customer_id": customer_id, "hotel_id": hotel_id, "driver_id": None,
        "address_id": address_id, "status": "PLACED",
        "payment_id": None if payment_mode == "CASH" else f"PAY-{order_id}",
        "payment_mode": payment_mode, "payment_status": "PENDING" if payment_mode == "CASH" else "PAID",
        "total_price": round(subtotal * (1 - discount / 100), 2), "tip": tip, "discount_pct": discount,
        "coupon": (coupon or None), "time_of_order": datetime.now(), "delivery_time": None,
        "lines": saved_lines,
    })
    return {"ok": True, "message": f"Order place ho gaya! Order ID: {order_id}"}


def add_review(order_id, target_type, rating, text_review):
    review_id = f"REV-DEMO-{len(REVIEWS) + 1:03d}"
    REVIEWS.append({"review_id": review_id, "order_id": order_id, "target_type": target_type,
                    "rating": rating, "text_review": text_review})
    return "Review submit ho gaya. Shukriya!"


# ===========================================================================
# HOTEL
# ===========================================================================

def hotel_dashboard(hotel_id):
    hotel = HOTELS.get(hotel_id)
    if not hotel:
        return {"hotel": None, "menu_items": [], "orders": [], "reviews": [], "stats": {}}
    mine = [o for o in ORDERS if o["hotel_id"] == hotel_id]
    orders = [{"order_id": o["order_id"], "customer_name": _customer_name(o["customer_id"]),
               "status": o["status"], "total_price": o["total_price"],
               "time_of_order": _fmt(o["time_of_order"]), "driver_name": _driver_name(o["driver_id"]),
               "order_items": _order_items(o)} for o in reversed(mine)]
    ids = {o["order_id"] for o in mine}
    reviews = [r for r in REVIEWS if r["target_type"] == "HOTEL" and r["order_id"] in ids]
    stats = {"total_orders": len(mine), "pending_orders": sum(1 for o in mine if o["status"] == "PLACED"),
             "avg_rating": _avg([r["rating"] for r in reviews]), "menu_count": len(MENU.get(hotel_id, []))}
    return {"hotel": hotel, "menu_items": list(MENU.get(hotel_id, [])), "orders": orders,
            "reviews": reviews, "stats": stats}


def hotel_register(hotel_id):
    hotel = HOTELS.get(hotel_id)
    phones = [{"phone_no": p} for p in HOTEL_PHONES.get(hotel_id, [])] if hotel else []
    return hotel, phones


def save_hotel(hotel_id, hotel_name, opening_time, closing_time, street, city, pin_code, geo_lat, geo_long):
    if not hotel_id or hotel_id not in HOTELS:
        n = len(HOTELS) + 1
        while f"H{n:03d}" in HOTELS:
            n += 1
        hotel_id = f"H{n:03d}"
        HOTEL_PHONES[hotel_id] = []
        MENU[hotel_id] = []
    HOTELS[hotel_id] = {"hotel_id": hotel_id, "hotel_name": hotel_name, "opening_time": opening_time,
                        "closing_time": closing_time, "city": city, "street": street,
                        "geo_lat": geo_lat, "geo_long": geo_long, "pin_code": pin_code}
    return hotel_id


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


def set_order_status(order_id, status, driver_id=None):
    """Hotel / driver / admin teeno isi se order ka status badalte hain."""
    o = _find_order(order_id)
    if not o:
        return
    if driver_id and o["driver_id"] != driver_id:
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

def driver_dashboard(driver_id):
    driver = DRIVERS.get(driver_id)
    if not driver:
        return {"driver": None, "my_orders": [], "open_orders": [], "history": [], "reviews": [], "stats": {}}
    mine = [o for o in reversed(ORDERS) if o["driver_id"] == driver_id]
    my_orders = []
    for o in mine:
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
            "drop_lat": a.get("geo_lat"), "drop_long": a.get("geo_long"),
            "order_items": _order_items(o),
        })
    open_orders = []
    for o in reversed(ORDERS):
        if o["status"] == "READY" and o["driver_id"] is None:
            h = HOTELS.get(o["hotel_id"], {})
            a = _address(o["customer_id"], o["address_id"])
            open_orders.append({"order_id": o["order_id"], "hotel_name": h.get("hotel_name"),
                                "hotel_street": h.get("street"), "hotel_city": h.get("city"),
                                "city": a.get("city"), "total_price": o["total_price"], "tip": o["tip"]})
    done = [o for o in mine if o["status"] == "DELIVERED"]
    history = [{"order_id": o["order_id"], "hotel_name": _hotel_name(o["hotel_id"]),
                "delivery_time": _fmt(o["delivery_time"]), "tip": o["tip"]} for o in done]
    ids = {o["order_id"] for o in mine}
    reviews = [r for r in REVIEWS if r["target_type"] == "DRIVER" and r["order_id"] in ids]
    stats = {"completed": len(done),
             "active": sum(1 for o in mine if o["status"] not in ("DELIVERED", "CANCELLED")),
             "total_tips": sum(o["tip"] for o in done), "avg_rating": _avg([r["rating"] for r in reviews])}
    return {"driver": driver, "my_orders": my_orders, "open_orders": open_orders, "history": history,
            "reviews": reviews, "stats": stats}


def driver_register(driver_id):
    return DRIVERS.get(driver_id)


def save_driver(driver_id, name, contact_no, vehicle_no, current_city):
    if not driver_id or driver_id not in DRIVERS:
        n = len(DRIVERS) + 1
        while f"D{n:03d}" in DRIVERS:
            n += 1
        driver_id = f"D{n:03d}"
        DRIVERS[driver_id] = {"driver_id": driver_id, "status": "OFFLINE", "curr_lat": None,
                              "curr_long": None, "current_city": current_city}
    DRIVERS[driver_id].update({"name": name, "contact_no": contact_no, "vehicle_no": vehicle_no})
    return driver_id


def set_driver_status(driver_id, status):
    if driver_id in DRIVERS:
        DRIVERS[driver_id]["status"] = status


def set_driver_location(driver_id, current_city, curr_lat, curr_long):
    if driver_id in DRIVERS:
        DRIVERS[driver_id].update({"current_city": current_city, "curr_lat": curr_lat, "curr_long": curr_long})


def accept_order(driver_id, order_id):
    o = _find_order(order_id)
    d = DRIVERS.get(driver_id)
    if not o or not d:
        return "Order ya driver nahi mila."
    if d["status"] != "AVAILABLE":
        return "Pehle apna status Available karo."
    if o["driver_id"] is not None:
        return "Ye order kisi aur driver ne le liya."
    o["driver_id"] = driver_id
    d["status"] = "BUSY"
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
    if not o:
        return
    o["driver_id"] = driver_id if driver_id in DRIVERS else None
    set_order_status(order_id, status)


def delete_customer(customer_id):
    CUSTOMERS.pop(customer_id, None)
    ADDRESSES.pop(customer_id, None)


def delete_hotel(hotel_id):
    HOTELS.pop(hotel_id, None)
    HOTEL_PHONES.pop(hotel_id, None)
    MENU.pop(hotel_id, None)


def delete_driver(driver_id):
    DRIVERS.pop(driver_id, None)
    for o in ORDERS:
        if o["driver_id"] == driver_id:
            o["driver_id"] = None


def delete_review(review_id):
    REVIEWS[:] = [r for r in REVIEWS if r["review_id"] != review_id]