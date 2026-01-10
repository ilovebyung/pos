import streamlit as st
import pandas as pd

# Example data
payers = ['brian', 'shawn', 'chris']
order = {
    "items": [
        {"Description": "Chicken Bucket (8 pcs)", "Quantity": 1, "Price": 12.99},
        {"Description": "Grilled Chicken Club", "Quantity": 1, "Price": 7.99}
    ]
}

st.title("Bill Splitting App 🍽️")

# Input for payer names
payer_input = st.text_area("Enter payer names (comma separated):", ",".join(payers))
payers = [p.strip() for p in payer_input.split(",") if p.strip()]

# Display order items
st.subheader("Order Items")
df_order = pd.DataFrame(order["items"])
st.table(df_order)

# Matrix of checkboxes
st.subheader("Assign Payers to Items")
assignments = {}

for i, item in enumerate(order["items"]):
    st.markdown(f"**{item['Description']} (${item['Price']})**")
    selected = []
    cols = st.columns(len(payers))
    for j, payer in enumerate(payers):
        if cols[j].checkbox(payer, key=f"{i}_{j}"):
            selected.append(payer)
    assignments[i] = selected

# Calculate splits
st.subheader("Bill Split Results")
results = {payer: 0 for payer in payers}

for i, item in enumerate(order["items"]):
    price = float(item["Price"])
    selected = assignments[i]
    if selected:
        share = price / len(selected)
        for payer in selected:
            results[payer] += share

# Show results
df_results = pd.DataFrame(list(results.items()), columns=["Payer", "Amount Owed"])
st.table(df_results)
