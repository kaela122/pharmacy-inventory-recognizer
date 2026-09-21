"""Create tables and seed demo data on first run (matches the UI screenshots)."""
from __future__ import annotations
from datetime import date
from sqlalchemy import select
from app.db.base import Base
from app.db.session import get_engine, _init, new_session
from app import models  # noqa: F401 registers models
from app.models import (User, Category, Product, Inventory, Supplier,
                        PurchaseOrder, PurchaseOrderItem, StockMovement)
from app.core.security import hash_password

USERS = [
    ("ADMIN001", "Dr. Ana Reyes", "admin123", "admin"),
    ("PHARM001", "Ben Santos", "pharma123", "pharmacist"),
    ("INVMGR01", "Clara Uy", "invmgr123", "inventory_manager"),
]

CATEGORIES = [
    ("Analgesic", "Pain relief medications"),
    ("Antibiotic", "Bacterial infection treatment"),
    ("Antacid", "Stomach acid neutralizers"),
    ("Antihypertensive", "Blood pressure management"),
    ("Antidiabetic", "Diabetes management drugs"),
    ("Supplement", "Vitamins and nutritional support"),
    ("Consumable", "Medical supplies and equipment"),
    ("Vitamin", "Essential vitamin supplements"),
]

# sku, name, category, price, stock, reorder
PRODUCTS = [
    ("M001", "Paracetamol 500mg", "Analgesic",       5.50, 245, 50),
    ("M002", "Amoxicillin 250mg",  "Antibiotic",     12.75, 18, 30),
    ("M003", "Omeprazole 20mg",    "Antacid",         8.00, 132, 25),
    ("M004", "Losartan 50mg",      "Antihypertensive",15.50, 0, 20),
    ("M005", "Metformin 500mg",    "Antidiabetic",    6.25, 88, 40),
    ("S001", "Vitamin C 500mg",    "Supplement",      3.25, 380, 100),
    ("S002", "Zinc 10mg",          "Supplement",      4.00, 9, 50),
    ("C001", "Surgical Mask (box)","Consumable",      2.50, 500, 100),
    ("C002", "Syringe 5ml",        "Consumable",      1.75, 12, 30),
]

# name, contact person, phone, email
SUPPLIERS = [
    ("MedCore Supply Co.",     "Rosa Lim",    "+63 917 555 0110", "sales@medcore.ph"),
    ("PharmaTech Inc.",        "Joel Aquino",   "+63 917 555 0142", "orders@pharmatech.ph"),
    ("GlobalMed Distributors", "Marco Tan",   "+63 917 555 0187", "hello@globalmed.ph"),
    ("Regional Pharma",        "Ella Cruz",   "+63 917 555 0203", "info@regionalpharma.ph"),
]

# number, supplier, status, date, [(sku, qty, subtotal), ...]
ORDERS = [
    ("ORD-2026-001", "MedCore Supply Co.",     "Fulfilled",  date(2026, 9, 15),
        [("M001", 500, 2250.00), ("M003", 200, 1400.00)]),
    ("ORD-2026-002", "PharmaTech Inc.",        "Fulfilled",  date(2026, 9, 18),
        [("M005", 300, 1875.00), ("S001", 700, 2275.00)]),
    ("ORD-2026-003", "GlobalMed Distributors", "Processing", date(2026, 9, 19),
        [("M002", 150, 1912.50), ("C001", 625, 1562.50)]),
    ("ORD-2026-004", "MedCore Supply Co.",     "Pending",    date(2026, 9, 20),
        [("C002", 200, 350.00), ("S002", 75, 300.00)]),
    ("ORD-2026-005", "PharmaTech Inc.",        "Pending",    date(2026, 9, 21),
        [("M004", 142, 2200.00)]),
    ("ORD-2026-006", "Regional Pharma",        "Cancelled",  date(2026, 9, 10),
        [("M003", 112, 900.00)]),
]


def seed():
    _init()
    Base.metadata.create_all(get_engine())
    db = new_session()
    try:
        if db.scalar(select(User).limit(1)):
            return
        for emp, name, pw, role in USERS:
            db.add(User(employee_id=emp, full_name=name,
                        password_hash=hash_password(pw), role=role))
        cats = {}
        for name, desc in CATEGORIES:
            c = Category(name=name, description=desc); db.add(c); db.flush()
            cats[name] = c.category_id
        prods = {}
        for sku, name, cat, price, stock, reorder in PRODUCTS:
            p = Product(sku=sku, name=name, category_id=cats[cat],
                        price=price, reorder_level=reorder)
            db.add(p); db.flush()
            db.add(Inventory(product_id=p.product_id, quantity=stock))
            prods[sku] = p.product_id
        sups = {}
        for name, contact, phone, email in SUPPLIERS:
            sp = Supplier(name=name, contact_person=contact, phone=phone, email=email)
            db.add(sp); db.flush()
            sups[name] = sp.supplier_id
        for number, supplier, status, odate, items in ORDERS:
            total = sum(sub for _, _, sub in items)
            po = PurchaseOrder(order_number=number, supplier_id=sups[supplier],
                               status=status, order_date=odate, total=total)
            db.add(po); db.flush()
            for sku, qty, sub in items:
                db.add(PurchaseOrderItem(order_id=po.order_id, product_id=prods[sku],
                                         quantity=qty, subtotal=sub))
        # a few example stock movements so the history has data on first run
        # (sku, type, change, resulting_stock, note, who)
        MOVES = [
            ("M001", "in",  100, 245, "Delivery from MedCore",     "INVMGR01"),
            ("M002", "out",  -7,  18, "Dispensed to ward",         "PHARM001"),
            ("S002", "out", -11,   9, "Dispensed - running low",   "PHARM001"),
            ("C002", "in",   12,  12, "Restock",                   "INVMGR01"),
        ]
        for sku, mtype, change, result, note, who in MOVES:
            db.add(StockMovement(product_id=prods[sku], movement_type=mtype, change=change,
                                 resulting_stock=result, note=note, employee_id=who))
        db.commit()
    finally:
        db.close()
