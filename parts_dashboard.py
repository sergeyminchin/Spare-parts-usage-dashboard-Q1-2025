import streamlit as st
st.set_page_config(page_title="Spare Parts Dashboard", layout="wide", page_icon="logo.png")
import pandas as pd
import plotly.express as px

from PIL import Image

try:
    logo = Image.open("logo.png")
    st.image(logo, use_container_width=False)
except:
    st.warning("🔧 Logo not found.")



st.title("🔧 Spare Parts Usage Dashboard")

uploaded_file = st.file_uploader("📤 Upload Spare Parts Excel File", type=["xlsx"])
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="DataSheet")
        st.success("✅ File loaded successfully.")

        # Map system types based on מק"ט בטיפול
        def map_unit_category(row):
            part_code = str(row.get('מק"ט בטיפול', "")).upper()
            if any(x in part_code for x in ["200P", "300P", "PRO"]):
                return "DX00 PRO", "DX00 PRO Distribution Cabinet"
            elif any(x in part_code for x in ["D200", "D300"]) and not any(x in part_code for x in ["PRO", "P"]):
                return "DX00", "DX00 Distribution Cabinet"
            elif any(x in part_code for x in ["310P", "31XP"]):
                return "R310 PRO", "R310 PRO Return Unit"
            elif any(x in part_code for x in ["R31X", "R310", "R300", "R310X"]) and not any(x in part_code for x in ["PRO", "P"]):
                return "R310", "R310 Return Unit"
            elif any(x in part_code for x in ["R11X", "R110", "R100", "R110X"]) and not any(x in part_code for x in ["PRO", "P"]):
                return "R110", "R110 Return Unit"
            else:
                return row.get('מק"ט בטיפול', ""), row.get("תאור מוצר בטיפול", "")

        df[["סוג מערכת", "תאור מערכת"]] = df.apply(map_unit_category, axis=1, result_type="expand")

        df["כמות בפועל"] = pd.to_numeric(df["כמות בפועל"], errors="coerce").fillna(0)

        # Sidebar filters
        st.sidebar.header("📊 Filters")
        techs = df["לטיפול"].dropna().unique()
        customers = df["שם לקוח"].dropna().unique()
        part_names = df["תאור מוצר - חלק"].dropna().unique()
        systems = df["סוג מערכת"].dropna().unique()

        selected_techs = st.sidebar.multiselect("👨‍🔧 Select Technicians", options=techs, default=techs)
        selected_customers = st.sidebar.multiselect("🏥 Select Customers", options=customers, default=customers)
        selected_parts = st.sidebar.multiselect("🔩 Select Part Descriptions", options=part_names, default=part_names)
        selected_systems = st.sidebar.multiselect("📦 Select System Types", options=systems, default=systems)

        filtered_df = df[
            (df["לטיפול"].isin(selected_techs)) &
            (df["שם לקוח"].isin(selected_customers)) &
            (df["תאור מוצר - חלק"].isin(selected_parts)) &
            (df["סוג מערכת"].isin(selected_systems))
        ]

        st.markdown(f"📦 **Total Parts Records:** {len(filtered_df)}")
        st.markdown(f"🧮 **Total Quantity Used:** {filtered_df['כמות בפועל'].sum():,.0f}")

        # Most Used Spare Parts
        top_parts = (
            filtered_df.groupby(['מק"ט - חלק', "תאור מוצר - חלק"])['כמות בפועל']
            .sum()
            .reset_index(name="Total Used")
            .sort_values(by="Total Used", ascending=False)
        )
        st.subheader("🔝 Most Frequently Used Spare Parts")
        fig1 = px.bar(top_parts.head(20), x="Total Used", y="תאור מוצר - חלק", orientation='h',
                      title="Top 20 Spare Parts by Quantity Used")
        st.plotly_chart(fig1, use_container_width=True)

        # Usage by Technician
        st.subheader("👨‍🔧 Part Usage by Technician")
        tech_usage = (
            filtered_df.groupby("לטיפול")["כמות בפועל"]
            .sum()
            .reset_index(name="Total Used")
            .sort_values(by="Total Used", ascending=False)
        )
        fig2 = px.bar(tech_usage, x="לטיפול", y="Total Used", title="Part Usage per Technician")
        st.plotly_chart(fig2, use_container_width=True)

        # Usage by Customer
        st.subheader("🏥 Part Usage by Customer")
        customer_usage = (
            filtered_df.groupby("שם לקוח")["כמות בפועל"]
            .sum()
            .reset_index(name="Total Used")
            .sort_values(by="Total Used", ascending=False)
        )
        fig3 = px.bar(customer_usage, x="שם לקוח", y="Total Used", title="Part Usage per Customer")
        st.plotly_chart(fig3, use_container_width=True)

        # Usage by System Type
        st.subheader("📦 Part Usage by System Type")
        system_usage = (
            filtered_df.groupby("סוג מערכת")["כמות בפועל"]
            .sum()
            .reset_index(name="Total Used")
            .sort_values(by="Total Used", ascending=False)
        )
        fig4 = px.bar(system_usage, x="סוג מערכת", y="Total Used", title="Part Usage by System")
        st.plotly_chart(fig4, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Failed to process file: {e}")
else:
    st.info("Please upload an Excel file to begin.")
