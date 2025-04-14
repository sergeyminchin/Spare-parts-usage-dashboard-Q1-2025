import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Spare Parts Dashboard", layout="wide", page_icon="logo.png")

try:
    logo = Image.open("logo.png")
    st.image(logo, use_container_width=False)
except:
    st.warning("🔧 Logo not found.")

st.title("🔧 Spare Parts Usage Summary")

uploaded_file = st.file_uploader("📤 Upload Spare Parts Excel File", type=["xlsx"])
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="DataSheet")
        st.success("✅ File loaded successfully.")

        def map_unit_category(row):
            part_code = str(row.get('מק"ט בטיפול', '')).upper()
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
                return row.get('מק"ט בטיפול', ''), row.get('תאור מוצר בטיפול', '')

        df[['סוג מערכת', 'תאור מערכת']] = df.apply(map_unit_category, axis=1, result_type="expand")
        df['כמות בפועל'] = pd.to_numeric(df['כמות בפועל'], errors="coerce").fillna(0)

        st.header("📦 Used Spare Parts Summary")
        parts_summary = (
            df.groupby(['מק"ט - חלק', 'תאור מוצר - חלק'])['כמות בפועל']
            .sum()
            .reset_index(name="Total Used")
            .sort_values(by="Total Used", ascending=False)
        )
        st.dataframe(parts_summary)

        st.header("🧰 Export Parts by System")
        system_options = ["All"] + sorted(df['סוג מערכת'].dropna().unique())
        selected_system = st.selectbox("Select System Type", options=system_options)

        towrite_sys = BytesIO()
        with pd.ExcelWriter(towrite_sys, engine="xlsxwriter") as writer:
            if selected_system == "All":
                for sys, group in df.groupby('סוג מערכת'):
                    summary = (
                        group.groupby(['מק"ט - חלק', 'תאור מוצר - חלק'])['כמות בפועל']
                        .sum()
                        .reset_index(name="Total Used")
                    )
                    summary.to_excel(writer, sheet_name=str(sys)[:31], index=False)
            else:
                group = df[df['סוג מערכת'] == selected_system]
                summary = (
                    group.groupby(['מק"ט - חלק', 'תאור מוצר - חלק'])['כמות בפועל']
                    .sum()
                    .reset_index(name="Total Used")
                )
                summary.to_excel(writer, sheet_name=str(selected_system)[:31], index=False)
        towrite_sys.seek(0)
        st.download_button("📥 Download System Summary", data=towrite_sys, file_name="parts_by_system.xlsx")

        st.header("👨‍🔧 Export Parts by Technician")
        tech_options = ["All"] + sorted(df['לטיפול'].dropna().unique())
        selected_tech = st.selectbox("Select Technician", options=tech_options)

        towrite_tech = BytesIO()
        with pd.ExcelWriter(towrite_tech, engine="xlsxwriter") as writer:
            if selected_tech == "All":
                for tech, group in df.groupby('לטיפול'):
                    group = group[group['כמות בפועל'] > 0]
                    summary = (
                        group.groupby(['מק"ט - חלק', 'תאור מוצר - חלק'])['כמות בפועל']
                        .sum()
                        .reset_index(name="Total Used")
                    )
                    summary.to_excel(writer, sheet_name=str(tech)[:31], index=False)
            else:
                group = df[df['לטיפול'] == selected_tech]
                group = group[group['כמות בפועל'] > 0]
                summary = (
                    group.groupby(['מק"ט - חלק', 'תאור מוצר - חלק'])['כמות בפועל']
                    .sum()
                    .reset_index(name="Total Used")
                )
                summary.to_excel(writer, sheet_name=str(selected_tech)[:31], index=False)
        towrite_tech.seek(0)
        st.download_button("📥 Download Technician Summary", data=towrite_tech, file_name="parts_by_technician.xlsx")

    except Exception as e:
        st.error(f"❌ Failed to process file: {e}")
else:
    st.info("Please upload an Excel file to begin.")
