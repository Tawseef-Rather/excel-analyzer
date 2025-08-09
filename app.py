import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Excel Data Manipulator", layout="wide")

# Title
st.title("📊 Excel Data Manipulator")

# File uploader
uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file:
    # Load data
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    # Store in session state
    if "data" not in st.session_state:
        st.session_state.data = data

    st.write("### Preview of Data")
    st.dataframe(st.session_state.data.head(10))

    # Sidebar options
    st.sidebar.header("Choose an Operation")

    choice = st.sidebar.selectbox(
        "Select operation",
        [
            "Get specified row range",
            "Get sum of a column",
            "Delete null columns",
            "Fill null values",
            "Delete a column",
            "Sort data",
            "Download updated file"
        ]
    )

    # Operation 1: Get specific row range
    if choice == "Get specified row range":
        start_range = st.number_input("Start row", min_value=0, value=0)
        end_range = st.number_input("End row", min_value=1, value=len(st.session_state.data))
        st.dataframe(st.session_state.data.iloc[start_range:end_range])

    # Operation 2: Sum of a column
    elif choice == "Get sum of a column":
        col = st.selectbox("Select column", st.session_state.data.columns)
        if pd.api.types.is_numeric_dtype(st.session_state.data[col]):
            st.success(f"Sum of {col}: {st.session_state.data[col].sum()}")
        else:
            st.error("Selected column is not numeric.")

    # Operation 3: Delete null columns
    elif choice == "Delete null columns":
        st.session_state.data = st.session_state.data.dropna(axis=1)
        st.success("Null columns deleted.")

    # Operation 4: Fill null values
    elif choice == "Fill null values":
        value = st.text_input("Enter value to fill")
        if st.button("Fill"):
            st.session_state.data = st.session_state.data.fillna(value)
            st.success(f"Null values filled with {value}")

    # Operation 5: Delete a column
    elif choice == "Delete a column":
        col = st.selectbox("Select column to delete", st.session_state.data.columns)
        if st.button("Delete"):
            st.session_state.data = st.session_state.data.drop(columns=[col])
            st.success(f"Column {col} deleted.")

    # Operation 6: Sort data
    elif choice == "Sort data":
        col = st.selectbox("Select column to sort by", st.session_state.data.columns)
        st.session_state.data = st.session_state.data.sort_values(by=col)
        st.success(f"Data sorted by {col}")

    # Operation 7: Download file
    elif choice == "Download updated file":
        file_type = st.radio("Select file format", ["Excel", "CSV"])
        if file_type == "Excel":
            towrite = BytesIO()
            with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
                st.session_state.data.to_excel(writer, index=False)
            towrite.seek(0)
            st.download_button(
                label="📥 Download Excel file",
                data=towrite,
                file_name="updated_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            csv = st.session_state.data.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV file",
                data=csv,
                file_name="updated_data.csv",
                mime="text/csv"
            )

    st.write("### Updated Data Preview")
    st.dataframe(st.session_state.data.head(10))
else:
    st.info("Please upload a file to start.")
