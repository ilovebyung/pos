import streamlit as st
import pandas as pd
from utils.util import format_price
from utils.database import get_db_connection
from utils.style import load_css
from streamlit_autorefresh import st_autorefresh


# ── Data fetchers ────────────────────────────────────────────────────────────

def get_modifiers_details(modifier_ids):
    """Return a list of modifier dicts given a modifier id string/list."""
    if not modifier_ids:
        return []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # modifier_ids may be a comma-separated string or already a list
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
            WHERE oc.order_status = 10
            ORDER BY oc.order_id, pi.description
        """)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return rows
    except Exception:
        return []


# ── Display helpers ──────────────────────────────────────────────────────────

DEFAULT_TAX_RATE = 4.712

def _display_from_order_details(order_data):
    """Render the CFD from Order_Cart / Order_Product data."""
    orders = {}
    subtotal = 0
    tax_amount = 0

    for row in order_data:
        order_id = row["order_id"]
        if order_id not in orders:
            orders[order_id] = []

        if row.get("product_id"):
            modifiers = get_modifiers_details(row.get("modifiers"))
            modifier_total_price = sum(mod["price"] for mod in modifiers)
            item_total = (row["product_price"] + modifier_total_price) * row["product_quantity"]

            try:
                tax_rate = row["tax"] if row["tax"] is not None else DEFAULT_TAX_RATE
            except (KeyError, TypeError):
                tax_rate = DEFAULT_TAX_RATE

            item_tax = item_total * (tax_rate / 100)

            orders[order_id].append({
                "description": row["product_description"],
                "quantity": row["product_quantity"],
                "base_price": row["product_price"],
                "modifiers": modifiers,
                "modifier_total": modifier_total_price,
                "item_total": item_total,
                "tax_rate": tax_rate,
                "item_tax": item_tax,
            })

            subtotal += item_total
            tax_amount += item_tax

    total = subtotal + tax_amount

    # st.subheader(f'Order: {", ".join(str(k) for k in orders.keys())}')

    table_data = []
    for order_id, items in orders.items():
        for item in items:
            description = item["description"]
            if item["modifiers"]:
                modifier_text = ", ".join(
                    f"{mod['description']} (+{format_price(mod['price'])})"
                    for mod in item["modifiers"]
                )
                description += f"\n  └─ {modifier_text}"

            table_data.append({
                "Description": description,
                "Quantity": item["quantity"],
                "Unit Price": format_price(item["base_price"] + item["modifier_total"]),
                "Price": format_price(item["item_total"]),
            })

    if table_data:
        df = pd.DataFrame(table_data)
        with st.container(height=500, border=True):
            st.dataframe(df.set_index(df.columns[0]), width='stretch')

        display_tax_rate = orders[list(orders.keys())[-1]][-1]["tax_rate"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Subtotal: {format_price(subtotal)}**")
        with col2:
            st.markdown(f"**Tax ({display_tax_rate:.3f}%): {format_price(tax_amount)}**")
        with col3:
            st.markdown(f"**Total: {format_price(total)}**")
    else:
        st.info("No items to display in the order.")


# ── Main entry point ─────────────────────────────────────────────────────────

def display_cfd():
    st.set_page_config(
        page_title="Customer Display",
        page_icon="🗒",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    load_css()

    with st.container(height=600, border=True):

        # Order_Cart / Order_Product
        order_data = get_order_details()
        if order_data:
            _display_from_order_details(order_data)
            return

        # 3. Nothing to show
        st.info("Welcome! Please start your order.")


if __name__ == "__main__":
    st_autorefresh(interval=1000, limit=None, key="cfd_refresh")
    display_cfd()
 