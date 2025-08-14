# Data Analyser app by Tawseef Ahmad
import io
import os
import pandas as pd
import numpy as np
import streamlit as st

# ----------------------------
# Excel-style UI + Watermark
# ----------------------------
st.set_page_config(page_title="Data Analyzer by Tawseef", layout="wide")

WATERMARK_CSS = """
<style>
/* Watermark */
body::before{
  content: "tawseef";
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%,-50%) rotate(-25deg);
  opacity: 0.08;
  font-size: 14rem;
  color: #000;
  z-index: 0;
  pointer-events: none;
  user-select: none;
}

/* Ribbon feel */
.block-container { padding-top: 1rem; }
.ribbon {
  background: linear-gradient(180deg, #f7f7fa 0%, #eef0f5 100%);
  border: 1px solid #e4e7ef;
  padding: 8px 12px;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.ribbon .group-title {
  font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: .06em;
  color: #475569; margin: 8px 0 4px;
}
.ribbon .tool-note {
  font-size: 0.8rem; color: #64748b; margin-top: 4px;
}
hr.soft { border: none; border-top: 1px solid #e5e7eb; margin: 8px 0 16px; }
</style>
"""
st.markdown(WATERMARK_CSS, unsafe_allow_html=True)

# ----------------------------
# Session State
# ----------------------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()
if "loaded_name" not in st.session_state:
    st.session_state.loaded_name = ""
if "preview_df" not in st.session_state:
    st.session_state.preview_df = None

# ----------------------------
# Helpers
# ----------------------------
def set_df(new_df: pd.DataFrame):
    st.session_state.df = new_df.copy()

def require_df():
    if st.session_state.df.empty:
        st.warning("Please load a file first.")
        return False
    return True

def download_button_for_df(df: pd.DataFrame, filename_base: str):
    c1, c2 = st.columns(2)
    with c1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("💾 Download CSV", data=csv, file_name=f"{filename_base}.csv", mime="text/csv")
    with c2:
        # Write Excel to bytes
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")
        st.download_button("📘 Download Excel (.xlsx)", data=buffer.getvalue(),
                           file_name=f"{filename_base}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ----------------------------
# Ribbon Tabs (Excel-like)
# ----------------------------
st.title("🧩 Data-Analyzer by Tawseef")

excel_tabs = st.tabs(["🏠 Home", "📊 Data", "🔎 View", "📚 Group", "💾 File & Save"])

# =========================================================
# TAB: File & Save  (kept options + save formats)
# =========================================================
with excel_tabs[4]:
    st.subheader("File & Save")
    st.markdown('<div class="ribbon">', unsafe_allow_html=True)

    cfile1, cfile2 = st.columns([2, 1])

    with cfile1:
        st.markdown("#### Open")
        uploaded = st.file_uploader("Open .csv / .xlsx / .json", type=["csv", "xlsx", "json"])
        if uploaded is not None:
            name = uploaded.name.lower()
            try:
                if name.endswith(".csv"):
                    df = pd.read_csv(uploaded)
                elif name.endswith(".xlsx"):
                    df = pd.read_excel(uploaded)
                elif name.endswith(".json"):
                    df = pd.read_json(uploaded)
                else:
                    st.error("Unsupported file type.")
                    df = None
                if df is not None:
                    set_df(df)
                    st.session_state.loaded_name = uploaded.name
                    st.success("File loaded successfully....")
            except Exception as e:
                st.error(f"Error loading file: {e}")

    with cfile2:
        st.markdown("#### Info")
        st.write("**Loaded:**", st.session_state.loaded_name or "—")
        if not st.session_state.df.empty:
            st.write("**Rows/Cols:**", st.session_state.df.shape)

    st.markdown("----")
    st.markdown("#### Save")
    if require_df():
        file_name = st.text_input("Enter your file name to save (no extension):", value="output")
        if st.button("Save as CSV"):
            try:
                path = f"{file_name.strip()}.csv"
                if os.path.exists(path):
                    st.warning("File already exists.")
                else:
                    st.session_state.df.to_csv(path, index=False)
                    st.success("File saved successfully....")
            except Exception as e:
                st.error(f"Save failed: {e}")

        if st.button("Save as Excel (.xlsx)"):
            try:
                path = f"{file_name.strip()}.xlsx"
                if os.path.exists(path):
                    st.warning("File already exists.")
                else:
                    with pd.ExcelWriter(path, engine="openpyxl") as writer:
                        st.session_state.df.to_excel(writer, index=False, sheet_name="Sheet1")
                    st.success("File saved successfully....")
            except Exception as e:
                st.error(f"Save failed: {e}")

        # Instant download (doesn't write to server disk)
        st.caption("Or download directly without saving on server disk:")
        download_button_for_df(st.session_state.df, file_name.strip() or "output")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TAB: Home (Show N rows + Replace + Sort)
# =========================================================
with excel_tabs[0]:
    st.subheader("Home")
    st.markdown('<div class="ribbon">', unsafe_allow_html=True)

    # --- Group: View N Rows (matches your show_N_rows)
    st.markdown('<div class="group-title">View N Rows</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1.2, 0.8])
    with c1:
        view_mode = st.selectbox("Choose an operation",
                                 ["1. Want to change actual Data", "2. Just take overview of N rows"])
    with c2:
        starts_with = st.number_input("Enter the starting Row number", min_value=0, value=0, step=1)
    with c3:
        ends_with = st.number_input("Enter the ending Row number", min_value=0, value=10, step=1)

    if require_df():
        x = st.session_state.df.iloc[int(starts_with):int(ends_with)]
        if st.button("Apply View/Change"):
            if view_mode.startswith("1."):
                # modify actual df to the slice
                set_df(x)
                st.success(f"From row {starts_with} to {ends_with} data is now the active data.")
                st.dataframe(st.session_state.df, use_container_width=True)
            else:
                st.info(f"From row {starts_with} to {ends_with} data preview:")
                st.dataframe(x, use_container_width=True)

    st.markdown("hr", unsafe_allow_html=True)

    # --- Group: Replace Values (matches your replace_value)
    st.markdown('<div class="group-title">Replace Values</div>', unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        case1 = st.selectbox("1. Replacable value is int (y/n)", ["y", "n"], index=0)
    with r2:
        case2 = st.selectbox("2. Your value is int (y/n)", ["y", "n"], index=0)

    repl_ok = require_df()
    if repl_ok:
        if case1 == "y" and case2 == "y":
            replacing = st.number_input("Enter a value to replace (int)", step=1, value=0)
            replace_with = st.number_input("Enter the replacing value (int)", step=1, value=0)
            if st.button("Replace (int→int)"):
                set_df(st.session_state.df.replace(to_replace=int(replacing), value=int(replace_with)))
                st.success("Replacement done.")
        elif case1 == "y" and case2 == "n":
            replacing = st.number_input("Enter a value to replace (int)", step=1, value=0)
            replace_with = st.text_input("Enter the replacing value (str)", value="")
            if st.button("Replace (int→str)"):
                set_df(st.session_state.df.replace(to_replace=int(replacing), value=replace_with))
                st.success("Replacement done.")
        elif case1 == "n" and case2 == "y":
            replacing = st.text_input("Enter a value to replace (str)", value="")
            replace_with = st.number_input("Enter the replacing value (int)", step=1, value=0)
            if st.button("Replace (str→int)"):
                set_df(st.session_state.df.replace(to_replace=replacing, value=int(replace_with)))
                st.success("Replacement done.")
        elif case1 == "n" and case2 == "n":
            replacing = st.text_input("Enter a value to replace (str)", value="")
            replace_with = st.text_input("Enter the replacing value (str)", value="")
            if st.button("Replace (str→str)"):
                set_df(st.session_state.df.replace(to_replace=replacing, value=replace_with))
                st.success("Replacement done.")

        if not st.session_state.df.empty:
            st.dataframe(st.session_state.df.head(10), use_container_width=True)

    st.markdown("hr", unsafe_allow_html=True)

    # --- Group: Sort (matches your sorting)
    st.markdown('<div class="group-title">Sort</div>', unsafe_allow_html=True)
    if require_df():
        cols = list(st.session_state.df.columns)
        col_idx = st.selectbox("Enter the column index", options=list(range(len(cols))),
                               format_func=lambda i: f"{i}. {cols[i]}")
        choose_method = st.selectbox("Choose the operation", ["1. Sort in ascending", "2. Sort in descending"], index=0)
        if st.button("Apply Sort"):
            column = cols[col_idx]
            ascending = True if choose_method.startswith("1.") else False
            set_df(st.session_state.df.sort_values(by=column, ascending=ascending))
            st.success("Sorted.")
            st.dataframe(st.session_state.df.head(10), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TAB: Data (Fill/Drop Nulls exactly like your menu)
# =========================================================
with excel_tabs[1]:
    st.subheader("Data")
    st.markdown('<div class="ribbon">', unsafe_allow_html=True)

    st.markdown('<div class="group-title">Null Data Operations</div>', unsafe_allow_html=True)
    null_choice = st.selectbox(
        "Choose an operation for Null Data",
        ["1. Fill null values", "2. Delete null columns", "3. Delete null rows"],
        index=0
    )

    if require_df():
        if null_choice.startswith("1."):
            fill_choice = st.selectbox(
                "Choose an operation to fill missing data",
                [
                    "1. Custom fill",
                    "2. Fill with average of a column",
                    "3. Fill with sum of a column",
                    "4. Fill with Interpolation",
                    "5. Fill with previous row",
                    "6. Fill with Next row"
                ],
                index=0
            )

            if fill_choice.startswith("1."):
                fill_value = st.text_input("Enter the value", value="")
                if st.button("Apply Custom Fill"):
                    set_df(st.session_state.df.fillna(fill_value))
                    st.success("Nulls filled.")
                    st.dataframe(st.session_state.df.head(10), use_container_width=True)

            elif fill_choice.startswith("2."):
                ccols = list(st.session_state.df.columns)
                col_sel = st.selectbox("Select a numeric column", ccols)
                if st.button("Fill with Average"):
                    try:
                        avg = st.session_state.df[col_sel].mean()
                        set_df(st.session_state.df.fillna({col_sel: avg}))
                        st.info(f"Null values filled with : {avg}")
                        st.write(st.session_state.df.isnull().sum())
                        st.dataframe(st.session_state.df.head(10), use_container_width=True)
                    except Exception:
                        st.error(f"{col_sel} isn't numeric, please select a numeric column")

            elif fill_choice.startswith("3."):
                ccols = list(st.session_state.df.columns)
                col_sel = st.selectbox("Select a numeric column", ccols)
                if st.button("Fill with Sum"):
                    try:
                        col_sum = st.session_state.df[col_sel].sum()
                        set_df(st.session_state.df.fillna({col_sel: col_sum}))
                        st.info(f"Null values filled with : {col_sum}")
                        st.write(st.session_state.df.isnull().sum())
                        st.dataframe(st.session_state.df.head(10), use_container_width=True)
                    except Exception:
                        st.error(f"{col_sel} isn't numeric, please select a numeric column")

            elif fill_choice.startswith("4."):
                ccols = list(st.session_state.df.columns)
                col_sel = st.selectbox("Enter the column name", ccols)
                if st.button("Interpolate Column"):
                    df_new = st.session_state.df.copy()
                    df_new[col_sel] = df_new[col_sel].interpolate()
                    set_df(df_new)
                    st.success("Null values filled successfully....")
                    st.write(st.session_state.df.isnull().sum())
                    st.dataframe(st.session_state.df.head(10), use_container_width=True)

            elif fill_choice.startswith("5."):
                if st.button("Fill with previous row (ffill)"):
                    set_df(st.session_state.df.ffill())
                    st.success("Null values filled successfully....")
                    st.write(st.session_state.df.isnull().sum())
                    st.dataframe(st.session_state.df.head(10), use_container_width=True)

            elif fill_choice.startswith("6."):
                if st.button("Fill with Next row (bfill)"):
                    set_df(st.session_state.df.bfill())
                    st.success("Null values filled successfully....")
                    st.write(st.session_state.df.isnull().sum())
                    st.dataframe(st.session_state.df.head(10), use_container_width=True)

        elif null_choice.startswith("2."):
            st.markdown("**Delete Null Columns**")
            dopt = st.selectbox("Choose an operation",
                                ["1. Keep columns with atleast N non-NaN",
                                 "2. Delete columns that contain any NaN"], index=0)
            if dopt.startswith("1."):
                count_nan = st.number_input("Enter the maximum NaN value (thresh for non-NaN)", min_value=0, value=1)
                if st.button("Apply (Columns with at least N non-NaN)"):
                    set_df(st.session_state.df.dropna(axis=1, thresh=int(count_nan)))
                    st.success(f"Columns filtered by thresh={int(count_nan)}")
                    st.dataframe(st.session_state.df.head(10), use_container_width=True)
            else:
                if st.button("Delete columns that contain any NaN"):
                    set_df(st.session_state.df.dropna(axis=1))
                    st.success("Columns containing Null Deleted successfully.....")
                    st.dataframe(st.session_state.df.head(10), use_container_width=True)

        elif null_choice.startswith("3."):
            st.markdown("**Delete Null Rows**")
            dopt = st.selectbox("Choose an operation",
                                ["1. Keep rows with atleast N non-NaN",
                                 "2. Delete rows that contain any NaN"], index=0)
            if dopt.startswith("1."):
                count_nan = st.number_input("Enter the maximum NaN value (thresh for non-NaN)", min_value=0, value=1)
                if st.button("Apply (Rows with at least N non-NaN)"):
                    set_df(st.session_state.df.dropna(axis=0, thresh=int(count_nan)))
                    st.success(f"Rows filtered by thresh={int(count_nan)}")
                    st.dataframe(st.session_state.df.head(10), use_container_width=True)
            else:
                if st.button("Delete rows that contain any NaN"):
                    set_df(st.session_state.df.dropna(axis=0))
                    st.success("Rows containing Null Deleted successfully.....")
                    st.dataframe(st.session_state.df.head(10), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TAB: View (Excel-like grid editor)
# =========================================================
with excel_tabs[2]:
    st.subheader("View")
    st.markdown('<div class="ribbon">', unsafe_allow_html=True)
    if require_df():
        st.markdown('<div class="group-title">Worksheet</div>', unsafe_allow_html=True)
        st.caption("Edit cells inline like Excel. Changes apply to the active DataFrame when you click **Apply Edits**.")
        edited = st.data_editor(st.session_state.df, use_container_width=True, num_rows="dynamic")
        if st.button("Apply Edits"):
            set_df(edited)
            st.success("Changes applied.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TAB: Group (matches your group_by)
# =========================================================
with excel_tabs[3]:
    st.subheader("Group")
    st.markdown('<div class="ribbon">', unsafe_allow_html=True)
    if require_df():
        st.markdown('<div class="group-title">Group By</div>', unsafe_allow_html=True)
        st.write(st.session_state.df.head(10))

        choice = st.selectbox(
            "Select your choice",
            [
                "1. Sum of Column X Grouped by Y",
                "2. count of Column X Grouped by Y",
                "3. Mean of Column X Grouped by Y",
                "4. Max of Column X Grouped by Y",
                "5. Min of Column X Grouped by Y",
            ],
            index=0
        )
        group_con = st.selectbox("Enter the grouping value (column)", list(st.session_state.df.columns))
        col_choose = st.selectbox("Enter the column name", list(st.session_state.df.columns))

        df1 = None
        if st.button("Run Group By"):
            try:
                if choice.startswith("1."):
                    df1 = st.session_state.df.groupby(group_con)[col_choose].sum()
                elif choice.startswith("2."):
                    df1 = st.session_state.df.groupby(group_con)[col_choose].count()
                elif choice.startswith("3."):
                    df1 = st.session_state.df.groupby(group_con)[col_choose].mean()
                elif choice.startswith("4."):
                    df1 = st.session_state.df.groupby(group_con)[col_choose].max()
                elif choice.startswith("5."):
                    df1 = st.session_state.df.groupby(group_con)[col_choose].min()
                else:
                    st.warning("Invalid choice")
                if df1 is not None:
                    st.success("Data Preview")
                    # turn Series → DataFrame for display
                    if isinstance(df1, pd.Series):
                        df1 = df1.to_frame(name="value")
                    st.dataframe(df1.head(10), use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# FOOTER/STATUS
# =========================================================
with st.expander("Status / Data Summary"):
    if not st.session_state.df.empty:
        st.write("**Shape:**", st.session_state.df.shape)
        st.write("**Columns:**", list(st.session_state.df.columns))
        st.write("**Nulls per column:**")
        st.write(st.session_state.df.isnull().sum())
    else:
        st.info("No data loaded yet. Use **File & Save → Open**.")
