import streamlit as st
import pandas as pd
import joblib
from datetime import datetime, date

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="RetailIQ",
    page_icon="📦",
    layout="wide"
)

# ----------------------------
# LOAD MODEL
# ----------------------------
model = joblib.load("retailiq_model.pkl")
preprocessor = joblib.load("preprocessor.pkl")
dropdown = joblib.load("dropdown_values.pkl")

# ----------------------------
# SESSION STATE
# ----------------------------
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame()

# ----------------------------
# TITLE
# ----------------------------
st.title("📦 RetailIQ")
st.subheader("AI-Powered Inventory Intelligence Platform")

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:

    store = st.selectbox(
        "Store ID",
        dropdown["Store ID"]
    )

    product = st.selectbox(
        "Product ID",
        dropdown["Product ID"]
    )

    category = st.selectbox(
        "Category",
        dropdown["Category"]
    )

    region = st.selectbox(
        "Region",
        dropdown["Region"]
    )

with col2:

    inventory = int(st.text_input(
        "Inventory Level",
        "120"
    ))

    units_sold = int(st.text_input(
        "Units Sold",
        "25"
    ))

    units_ordered = int(st.text_input(
        "Units Ordered",
        "20"
    ))

    price = float(st.text_input(
        "Price",
        "99.50"
    ))

    discount = float(st.text_input(
        "Discount",
        "10"
    ))

with col3:

    competitor_price = float(st.text_input(
        "Competitor Pricing",
        "95"
    ))

    weather = st.selectbox(
        "Weather Condition",
        dropdown["Weather Condition"]
    )

    season = st.selectbox(
        "Seasonality",
        dropdown["Seasonality"]
    )

    promotion = st.selectbox(
        "Promotion",
        [0,1]
    )

    epidemic = st.selectbox(
        "Epidemic",
        [0,1]
    )

selected_date = st.date_input(
    "Select Date",
    date.today()
)
# ====================================
# PREDICT BUTTON
# ====================================

if st.button("🚀 Predict Demand", use_container_width=True):

    year = selected_date.year
    month = selected_date.month
    day = selected_date.day
    day_of_week = selected_date.weekday()
    weekend = 1 if day_of_week >= 5 else 0

    price_difference = competitor_price - price
    inventory_to_sales = inventory / (units_sold + 1)

    input_df = pd.DataFrame({

        "Store ID":[store],
        "Product ID":[product],
        "Category":[category],
        "Region":[region],
        "Inventory Level":[inventory],
        "Units Sold":[units_sold],
        "Units Ordered":[units_ordered],
        "Price":[price],
        "Discount":[discount],
        "Weather Condition":[weather],
        "Promotion":[promotion],
        "Competitor Pricing":[competitor_price],
        "Seasonality":[season],
        "Epidemic":[epidemic],
        "Year":[year],
        "Month":[month],
        "Day":[day],
        "Day_of_Week":[day_of_week],
        "Is_Weekend":[weekend],
        "Price_Difference":[price_difference],
        "Inventory_to_Sales":[inventory_to_sales]

    })

    # Ensure same order as training
    input_df = input_df[preprocessor.feature_names_in_]

    processed = preprocessor.transform(input_df)

    prediction = model.predict(processed)[0]

    revenue = prediction * price

    # -------------------------
    # KPI Cards
    # -------------------------

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "📦 Predicted Demand",
            f"{prediction:.2f} Units"
        )

    with col2:
        st.metric(
            "💰 Estimated Revenue",
            f"${revenue:,.2f}"
        )

    st.markdown("---")

    # -------------------------
    # AI Recommendation
    # -------------------------

    if prediction > inventory:

        status = "Restock"

        st.error(
            f"""
### ⚠ AI Recommendation

Predicted demand is **{prediction:.0f} units** while inventory is only **{inventory} units**.

**Recommendation:** Restock inventory to avoid stock shortages.
"""
        )

    elif prediction < inventory * 0.5:

        status = "Overstock"

        st.warning(
            f"""
### 📦 AI Recommendation

Current inventory is much higher than predicted demand.

**Recommendation:** Reduce future orders or increase promotions.
"""
        )

    else:

        status = "Balanced"

        st.success(
            f"""
### ✅ AI Recommendation

Inventory level appears balanced.

No immediate action required.
"""
        )

    # -------------------------
    # Save Prediction
    # -------------------------

    history_row = pd.DataFrame({

        "Timestamp":[datetime.now().strftime("%d-%m-%Y %H:%M:%S")],
        "Store":[store],
        "Product":[product],
        "Category":[category],
        "Inventory":[inventory],
        "Predicted Demand":[round(prediction,2)],
        "Revenue ($)":[round(revenue,2)],
        "Status":[status]

    })

    st.session_state.history = pd.concat(
        [st.session_state.history, history_row],
        ignore_index=True
    )
    # ====================================
# PREDICTION HISTORY
# ====================================

if not st.session_state.history.empty:

    st.markdown("---")
    st.subheader("📋 Prediction History")

    st.dataframe(
        st.session_state.history,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------
    # Download CSV
    # --------------------------
    csv = st.session_state.history.to_csv(index=False).encode("utf-8")

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            label="⬇ Download History",
            data=csv,
            file_name="RetailIQ_Prediction_History.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:

        if st.button("🗑 Clear History", use_container_width=True):
            st.session_state.history = pd.DataFrame()
            st.rerun()

    # --------------------------
    # Demand Trend Chart
    # --------------------------

    st.markdown("---")
    st.subheader("📈 Predicted Demand Trend")

    chart_df = st.session_state.history.copy()

    chart_df.index = range(1, len(chart_df) + 1)

    st.line_chart(
        chart_df["Predicted Demand"]
    )

    # --------------------------
    # Revenue Trend
    # --------------------------

    st.subheader("💰 Revenue Trend")

    st.bar_chart(
        chart_df["Revenue ($)"]
    )