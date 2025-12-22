import streamlit as st
import requests
import pandas as pd
from io import BytesIO
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Subsidiary Data Extractor",
    page_icon="📊",
    layout="wide"
)

def get_subsidiaries(parent_name):
    """
    Fetch subsidiaries data from the API using parent name
    Returns the full response including status, count, and subsidiaries list
    """
    base_url = "https://dev-monotypeai.huhoka.com/tools/subsidiaries"
    params = {"main_parent_name": parent_name}
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def json_to_csv(api_response, parent_identifier):
    """
    Convert API response to CSV format in memory, excluding specified columns
    """
    try:
        # Check if we have a successful response with subsidiaries
        if not api_response or "status" not in api_response or api_response["status"] != "success":
            st.error("Invalid or empty response from the API")
            return None, None
            
        # Extract the subsidiaries list
        subsidiaries = api_response.get("subsidiaries", [])
        if not subsidiaries:
            st.warning("No subsidiaries found for the given criteria")
            return None, None
            
        # Create a DataFrame from the subsidiaries list
        df = pd.json_normalize(subsidiaries)
        
        # Columns to exclude
        columns_to_exclude = [
            'id', 'uId', 'dType', 'main_parent_id', 'record_update_date',
            'createdBy', 'createdAt', 'updatedBy', 'updatedAt', 'version',
            'active', 'archived', 'domains', 'validatedAt', '_rid', '_self',
            '_etag', '_attachments', '_ts'
        ]
        
        # Remove the columns we want to exclude (if they exist)
        df = df.drop(columns=[col for col in columns_to_exclude if col in df.columns], errors='ignore')
        
        # Create a StringIO buffer to store the CSV data
        output = BytesIO()
        
        # Write the DataFrame to the buffer as CSV
        df.to_csv(output, index=False, encoding='utf-8')
        
        # Get the CSV data from the buffer
        csv_data = output.getvalue()
        
        # Create a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{parent_identifier}_subsidiaries_{timestamp}.csv"
        
        return csv_data, filename
    except Exception as e:
        st.error(f"Error converting data to CSV: {str(e)}")
        return None, None

def main():
    st.title("📊 Subsidiary Data Extractor")
    st.write("Enter Parent Name to fetch subsidiary data")
    
    # Single input field for parent name
    parent_name = st.text_input("Parent Name", "")
    
    # Add some spacing
    st.write("")
    
    # Add a button to fetch data
    if st.button("Get Subsidiaries"):
        if not parent_name:
            st.warning("Please enter a Parent Name")
            return
            
        with st.spinner("Fetching subsidiary data..."):
            # Get data from API using only parent name
            data = get_subsidiaries(parent_name=parent_name)
            
            if data:
                # Determine the parent identifier for the filename
                parent_identifier = parent_name
                
                # Convert to CSV
                csv_data, filename = json_to_csv(data, parent_identifier)
                
                if csv_data and filename:
                    # Display the count of subsidiaries
                    st.success(f"Found {data.get('count', 0)} subsidiaries")
                    
                    # Create a download button for CSV
                    st.download_button(
                        label="Download CSV File",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv"
                    )
                    
                    # Display success message
                    st.success("Data fetched successfully! Click the button above to download the CSV file.")
                    
                    # Display a preview of the data (using the same column exclusion as in json_to_csv)
                    st.subheader("Data Preview")
                    df_preview = pd.json_normalize(data.get("subsidiaries", []))
                    
                    # Apply the same column exclusion as in json_to_csv
                    columns_to_exclude = [
                        'id', 'uId', 'dType', 'main_parent_id', 'record_update_date',
                        'createdBy', 'createdAt', 'updatedBy', 'updatedAt', 'version',
                        'active', 'archived', 'domains', 'validatedAt', '_rid', '_self',
                        '_etag', '_attachments', '_ts'
                    ]
                    df_preview = df_preview.drop(columns=[col for col in columns_to_exclude if col in df_preview.columns], errors='ignore')
                    
                    st.dataframe(df_preview.head())

if __name__ == "__main__":
    main()