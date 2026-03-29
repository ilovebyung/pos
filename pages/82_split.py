import streamlit as st
import pandas as pd
from utils.database import get_db_connection
from utils.util import format_price


# ── Reuse data fetchers from 11_CFD.py ──────────────────────────────────────

def get_modifiers_details(modifier_ids):
    """Return a list of modifier dicts given a modifier id string/list."""
    if not modifier_ids:
        return []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if isinstance(modifier_ids, str):
            ids = [m.strip() for m in modifier_ids.split(",") if m.strip()]
        else:
            ids = list(modifier_ids)
        if not ids:
            return []
        placeholders = ",".join("?" * len(ids))
        cursor.execute(
            f"SELECT description, price FROM Modifier WHERE modifier_id IN ({placeholders})",
            ids,
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"description": r[0], "price": r[1]} for r in rows]
    except Exception:
        return []


def get_order_details():
    """Fetch the active order from Order_Cart / Order_Product (order_status = 10)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                oc.order_id,
                oc.subtotal,
                op.product_id,
                op.modifiers,
                pi.description  AS product_description,
                op.product_quantity,
                pi.price        AS product_price,
                pi.tax          AS tax
            FROM Order_Cart oc
            LEFT JOIN Order_Product op ON oc.order_id = op.order_id
            LEFT JOIN Product pi       ON op.product_id = pi.product_id
            WHERE oc.order_status IN (3) 
            ORDER BY oc.order_id, pi.description
        """)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows
    except Exception:
        return []


# ── Build order items from order_data ────────────────────────────────────────

def build_order_items(order_data):
    """Convert raw order_data rows into a flat list of display-ready item dicts."""
    items = []
    for row in order_data:
        if not row.get("product_id"):
            continue
        modifiers = get_modifiers_details(row.get("modifiers"))
        modifier_total = sum(mod["price"] for mod in modifiers)
        unit_price = row["product_price"] + modifier_total
        quantity = row["product_quantity"]
        total_price = unit_price * quantity

        description = row["product_description"]
        if modifiers:
            modifier_text = ", ".join(
                f"{mod['description']} (+{format_price(mod['price'])})"
                for mod in modifiers
            )
            description += f" [{modifier_text}]"

        items.append({
            "Description": description,
            "Quantity": quantity,
            "Unit Price": unit_price,
            "Price": total_price,
        })
    return items


# ── Main app ──────────────────────────────────────────────────────────────────

st.title("Bill Splitting App 🍽️")

# Load live order data
order_data = get_order_details()
order_items = build_order_items(order_data)

if not order_items:
    st.info("No active order found. Please start an order first.")
    st.stop()

# Input for payer names
payer_input = st.text_input(
    "Enter payer names (comma-separated):",
    placeholder="e.g. Alice, Bob, Charlie",
)
payers = [p.strip() for p in payer_input.split(",") if p.strip()]

# Display order items
st.subheader("Order Items")
df_order = pd.DataFrame([
    {
        "Description": item["Description"],
        "Qty": item["Quantity"],
        "Unit Price": format_price(item["Unit Price"]),
        "Total": format_price(item["Price"]),
    }
    for item in order_items
])
st.table(df_order)

if not payers:
    st.info("Enter payer names above to start splitting the bill.")
    st.stop()

# Matrix of checkboxes — assign payers to items
st.subheader("Assign Payers to Items")
assignments = {}  # item_index -> list of payers

for i, item in enumerate(order_items):
    st.markdown(f"**{item['Description']}** — {format_price(item['Price'])}")
    selected = []
    cols = st.columns(len(payers))
    for j, payer in enumerate(payers):
        if cols[j].checkbox(payer, key=f"item_{i}_payer_{j}"):
            selected.append(payer)
    assignments[i] = selected

# Calculate and display splits
st.subheader("Bill Split Results")
totals = {payer: 0.0 for payer in payers}

for i, item in enumerate(order_items):
    selected = assignments[i]
    if selected:
        share = item["Price"] / len(selected)
        for payer in selected:
            totals[payer] += share

df_results = pd.DataFrame(
    [{"Payer": payer, "Amount Owed": format_price(amount)} for payer, amount in totals.items()]
)
st.table(df_results)

# Grand total check
assigned_total = sum(
    order_items[i]["Price"]
    for i, selected in assignments.items()
    if selected
)
unassigned_total = sum(
    order_items[i]["Price"]
    for i, selected in assignments.items()
    if not selected
)

if unassigned_total > 0:
    st.warning(f"⚠️ {format_price(unassigned_total)} worth of items have not been assigned to any payer.")

st.markdown(f"**Total assigned: {format_price(assigned_total)}**")