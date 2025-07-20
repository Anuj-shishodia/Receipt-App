# frontend/app.py
import streamlit as st
import requests
import pandas as pd
import json
import base64
from datetime import date, datetime

# Backend API URL (adjust if your backend is on a different port/host)
BACKEND_URL = "http://localhost:8000/api"

st.set_page_config(layout="wide", page_title="Receipt Dashboard")
st.title("Receipt and Bill Processing Dashboard")

# --- Sidebar for Upload and Filters ---
st.sidebar.header("Upload New Receipt")
uploaded_file = st.sidebar.file_uploader("Choose a file (JPG, PNG, PDF, TXT)", type=["jpg", "png", "pdf", "txt"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_type = uploaded_file.type
    file_name = uploaded_file.name
    
    # Encode file content to Base64 for sending to API
    encoded_content = base64.b64encode(file_bytes).decode('utf-8')

    upload_payload = {
        "file_name": file_name,
        "file_content_base64": encoded_content,
        "file_type": file_type
    }

    if st.sidebar.button("Upload and Process"):
        with st.spinner("Processing receipt..."):
            try:
                response = requests.post(f"{BACKEND_URL}/upload_receipt/", json=upload_payload)
                if response.status_code == 200:
                    st.sidebar.success("Receipt processed successfully!")
                    st.sidebar.json(response.json()['data'])
                    st.rerun() # Refresh the page to show new data
                else:
                    st.sidebar.error(f"Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
            except requests.exceptions.ConnectionError:
                st.sidebar.error("Could not connect to backend. Is the FastAPI server running?")
            except Exception as e:
                st.sidebar.error(f"An unexpected error occurred: {e}")

st.sidebar.header("Filter Receipts")
search_query = st.sidebar.text_input("Search (Vendor/Category)")
start_date_filter = st.sidebar.date_input("Start Date", value=date(2023, 1, 1))
end_date_filter = st.sidebar.date_input("End Date", value=date.today())
min_amount_filter = st.sidebar.number_input("Minimum Amount", value=None, min_value=0.0, format="%.2f")
max_amount_filter = st.sidebar.number_input("Maximum Amount", value=None, min_value=0.0, format="%.2f")
category_options = ["All", "Groceries", "Utilities (Electricity)", "Utilities (Internet)", "Utilities (Water)", "Dining", "Transportation", "Other"]
category_filter = st.sidebar.selectbox("Category", category_options)
if category_filter == "All":
    category_filter = None

st.sidebar.header("Sort Receipts")
sort_by_options = ["id", "vendor", "date", "amount", "category"]
sort_by = st.sidebar.selectbox("Sort By", sort_by_options)
sort_order = st.sidebar.radio("Sort Order", ["asc", "desc"])

# --- Main Content Area ---

# Fetch and display receipts
st.header("Uploaded Receipts")

params = {
    "query": search_query if search_query else None,
    "start_date": start_date_filter.isoformat() if start_date_filter else None,
    "end_date": end_date_filter.isoformat() if end_date_filter else None,
    "min_amount": min_amount_filter if min_amount_filter is not None else None,
    "max_amount": max_amount_filter if max_amount_filter is not None else None,
    "category": category_filter,
    "sort_by": sort_by,
    "sort_order": sort_order
}

# Filter out None values from params for cleaner API requests
params = {k: v for k, v in params.items() if v is not None}

receipts_data = []
try:
    response = requests.get(f"{BACKEND_URL}/receipts/", params=params)
    if response.status_code == 200:
        receipts_data = response.json()
        if receipts_data:
            df_receipts = pd.DataFrame(receipts_data)
            # Convert transaction_date to datetime objects for better display/sorting
            df_receipts['transaction_date'] = pd.to_datetime(df_receipts['transaction_date'])
            st.subheader("Tabular View of Records")
            st.dataframe(df_receipts)

            # Bonus Feature: Manual Correction (Select a row to edit)
            st.subheader("Manual Correction (Select a row to edit)")
            # Create a dictionary for easier lookup by ID
            receipts_dict = {r['id']: r for r in receipts_data}
            
            # Use receipt ID as key for selection
            selected_id = st.selectbox(
                "Select Receipt ID to Edit",
                options=[r['id'] for r in receipts_data],
                format_func=lambda x: f"ID: {x} - {receipts_dict[x]['vendor']}"
            )

            if selected_id:
                selected_receipt = receipts_dict[selected_id]
                with st.form(key=f"edit_form_{selected_id}"):
                    # Ensure date is a datetime.date object for st.date_input
                    initial_date = datetime.fromisoformat(selected_receipt['transaction_date']).date() if isinstance(selected_receipt['transaction_date'], str) else selected_receipt['transaction_date']

                    edited_vendor = st.text_input("Vendor", value=selected_receipt.get('vendor', ''))
                    edited_date = st.date_input("Date", value=initial_date)
                    edited_amount = st.number_input("Amount", value=selected_receipt.get('amount', 0.0), format="%.2f")
                    edited_category = st.text_input("Category", value=selected_receipt.get('category', ''))
                    
                    submit_edit = st.form_submit_button("Update Receipt")

                    if submit_edit:
                        update_payload = {
                            "vendor": edited_vendor,
                            "transaction_date": edited_date.isoformat(),
                            "amount": edited_amount,
                            "category": edited_category
                        }
                        update_response = requests.put(f"{BACKEND_URL}/receipts/{selected_id}/", json=update_payload)
                        if update_response.status_code == 200:
                            st.success("Receipt updated successfully!")
                            st.rerun() # Refresh
                        else:
                            st.error(f"Failed to update: {update_response.json().get('detail', 'Unknown error')}")

        else:
            st.info("No receipts found matching the criteria.")
    else:
        st.error(f"Error fetching receipts: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
except requests.exceptions.ConnectionError:
    st.error("Could not connect to backend. Please ensure the backend server is running.")
except Exception as e:
    st.error(f"An unexpected error occurred while fetching receipts: {e}")


# Fetch and display statistical visualizations
st.header("Summarized Insights")

try:
    response = requests.get(f"{BACKEND_URL}/receipts/aggregates/")
    if response.status_code == 200:
        aggregates = response.json()
        st.subheader("Overall Expenditure")
        st.write(f"**Total Spend:** ${aggregates['total_spend']:.2f}")
        st.write(f"**Average Spend:** ${aggregates['mean_spend']:.2f}")
        st.write(f"**Median Spend:** ${aggregates['median_spend']:.2f}")
        st.write(f"**Mode Spend:** {', '.join([f'${s:.2f}' for s in aggregates['mode_spend']]) if aggregates['mode_spend'] else 'N/A'}")


        st.subheader("Vendor Distribution")
        if aggregates['vendor_frequency']:
            vendor_df = pd.DataFrame.from_dict(aggregates['vendor_frequency'], orient='index', columns=['Count'])
            vendor_df.index.name = 'Vendor'
            st.bar_chart(vendor_df)
        else:
            st.info("No vendor data for distribution.")


        st.subheader("Monthly Spend Trend")
        if aggregates['monthly_spend_trend']:
            trend_df = pd.DataFrame(list(aggregates['monthly_spend_trend'].items()), columns=['Month', 'Amount'])
            trend_df['Month'] = pd.to_datetime(trend_df['Month'])
            trend_df = trend_df.sort_values('Month')
            st.line_chart(trend_df.set_index('Month'))
        else:
            st.info("No monthly spend data available.")

    else:
        st.error(f"Error fetching aggregates: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
except requests.exceptions.ConnectionError:
    st.error("Could not connect to backend. Please ensure the backend server is running.")
except Exception as e:
    st.error(f"An unexpected error occurred while fetching aggregates: {e}")


# Bonus Feature: Export Data
st.sidebar.header("Export Data")
export_format = st.sidebar.radio("Export Format", ["CSV", "JSON"])
if st.sidebar.button("Download Data"):
    try:
        export_response = requests.get(f"{BACKEND_URL}/export_receipts/?format={export_format.lower()}")
        if export_response.status_code == 200:
            if export_format == "CSV":
                st.sidebar.download_button(
                    label=f"Click to Download {export_format}",
                    data=export_response.content,
                    file_name="receipts.csv",
                    mime="text/csv"
                )
            elif export_format == "JSON":
                st.sidebar.download_button(
                    label=f"Click to Download {export_format}",
                    data=export_response.content,
                    file_name="receipts.json",
                    mime="application/json"
                )
        else:
            st.sidebar.error(f"Failed to export: {export_response.status_code} - {export_response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.ConnectionError:
        st.sidebar.error("Could not connect to backend for export. Is the FastAPI server running?")
    except Exception as e:
        st.sidebar.error(f"An unexpected error occurred during export: {e}")