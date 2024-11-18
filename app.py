import streamlit as st
from db_function import user, farmer, milk_collection
import time
import pandas as pd
import plotly.express as px
import sqlite3


def insert_new_farmer(farmer_name, contact_info):
    conn = sqlite3.connect('milk_collection_system.db')
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO FARMER (farmerName, contactInfo) VALUES (?, ?)", (farmer_name, contact_info))
        conn.commit()
        return "success"
    except:
        return "failure"
    finally:
        conn.close()
        
def insert_new_user(user_name, password):
    conn = sqlite3.connect('milk_collection_system.db')
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO USER (userName, password) VALUES (?, ?)", (user_name, password))
        conn.commit()
        return "success"
    except:
        return "failure"
    finally:
        conn.close()

# Function to insert milk collection data
def insert_milk_data(farmer_id, quantity, reading, price_per_liter,total_amount):
    conn = sqlite3.connect('milk_collection_system.db')
    cur = conn.cursor()
    
    try:
        cur.execute('''
            INSERT INTO MILKCOLLECTION (farmerId, quantity, reading, pricePerLiter, totalAmount, date) 
            VALUES (?, ?, ?, ?, ?, CURRENT_DATE)
        ''', (farmer_id, quantity, reading, price_per_liter, total_amount))
        conn.commit()
        conn.close()
        return "success"
    except Exception as e:
        conn.close()
        return f"failure: {str(e)}"
    
# Fetch data for the selected month and year
def fetch_monthly_report(year, month, farmer_id):
    conn = sqlite3.connect('milk_collection_system.db')
    query = f'''
        SELECT m.farmerId, f.farmerName, SUM(m.totalAmount) as totalAmount
        FROM MILKCOLLECTION m
        JOIN FARMER f ON m.farmerId = f.farmer_id
        WHERE strftime('%Y', m.date) = ? AND strftime('%m', m.date) = ? AND f.farmer_id = ?
        GROUP BY f.farmerName
        ORDER BY totalAmount DESC
    '''
    df = pd.read_sql_query(query, conn, params=(year, month, farmer_id))
    conn.close()
    return df   
        

def home_page():
    st.title("Milk Collection Center")
  
    col1, col2 = st.columns([1, 3])
    with col1:
        slide = st.radio("Navigation", ["Register Farmer", "Farmers List", "Milk Collection", "Milk Collection Data", "Monthly Reports", "Logout"], 
                         key='slide', horizontal=False)
    with col2:
        if slide == "Register Farmer":
            with st.form(key='farmer-registration-form',clear_on_submit=False):
                st.write("#### Farmer Registration Form")
                farmer_name = st.text_input("Farmer Name")
                contact_info = st.text_input("Contact Info")
                    
                if st.form_submit_button("Submit"):
                    conn = sqlite3.connect('milk_collection_system.db')
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM FARMER WHERE farmerName = ?", (farmer_name,))
                    existing_user = cur.fetchone()
                    conn.close()
                        
                    if existing_user:
                        st.error(f"Farmer with name {farmer_name} already exists. Please use different name.")
                    else:
                        status = insert_new_farmer(farmer_name, contact_info)
                        if status == 'success':
                            st.success("Farmer registered successfully!")
                            time.sleep(1)
                            st.rerun()  # Rerun after successful submission
                        else:
                            st.error("Failed to register farmer. Please try again.")
        
        elif slide == "Farmers List":
            st.write("#### Farmers List")
            conn = sqlite3.connect('milk_collection_system.db')
            df = pd.read_sql_query("SELECT * FROM FARMER", conn)
            conn.close()
            st.dataframe(df,use_container_width=True, hide_index =True)

        elif slide == "Milk Collection":
            with st.form(key='milk-collection-form',clear_on_submit=False):
                st.write("#### Enter Milk Collection Data")
                farmer_id = st.number_input("Farmer Id",step=0)
                farmer_id = int(farmer_id)
                quantity = st.number_input("Milk Quantity (in liters)", step=0.1)
                reading = st.number_input("Fat Reading", step=0.1)
                price_per_liter = st.number_input("Price per Liter", step=0.1)
                
                
                if st.form_submit_button("Submit"):
                    conn = sqlite3.connect('milk_collection_system.db')
                    cur = conn.cursor()
                    
                    cur.execute('''
                        SELECT * FROM FARMER 
                        WHERE farmer_id = ?
                    ''', (farmer_id,))
                    
                    existing_farmer = cur.fetchone()
                    
                    if not existing_farmer:
                        st.error("Farmer does not exist. Please register the farmer first.")
                        conn.close()
                
                    else:
                        cur.execute('''
                            SELECT * FROM MILKCOLLECTION 
                            WHERE farmerId = ? AND date = CURRENT_DATE
                        ''', (farmer_id,))
                        
                        existing_entry = cur.fetchone()
                        
                        if existing_entry:
                            conn.close()
                            st.error("This user record already existed for today")
                        
                        else:
                            total_amount = round(quantity * reading * (price_per_liter / 10), 2)
                            status = insert_milk_data(farmer_id, quantity, reading, price_per_liter,total_amount)
                            if status == 'success':
                                st.success("Milk collection data added successfully!")
                                time.sleep(2)
                                st.rerun()  # Rerun after successful submission
                            else:
                                st.error("Failed to add data. Please try again.")

        elif slide == "Milk Collection Data":
            st.write("#### Milk collection Data")
            conn = sqlite3.connect('milk_collection_system.db')
            df = pd.read_sql_query("SELECT * FROM MILKCOLLECTION", conn)
            df = df.sort_values(by='date', ascending=False)
            conn.close()
            st.dataframe(df,use_container_width=True, hide_index =True)
        
        elif slide == "Monthly Reports":
            st.write("#### Monthly Report")
            conn = sqlite3.connect('milk_collection_system.db')
            cur = conn.cursor()
            data = cur.execute("SELECT distinct farmer_id FROM FARMER").fetchall()
            conn.close()
            # Dropdowns for year and month selection
            year = st.selectbox("Select Year", ["2024","2023"])
            month = st.selectbox("Select Month", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])
            farmer_ids = st.selectbox("Select Farmer ID", [str(i[0]) for i in data])


            # Fetch data for the selected month and year
            df = fetch_monthly_report(year, month, farmer_ids)

            # If there is no data for the selected month and year, display a message
            if df.empty:
                st.write(f"No data found for {year}-{month}. Farmer ID: {farmer_ids}")
            else:
                st.dataframe(df,use_container_width=True, hide_index =True)
      
        elif slide == "Logout":
            st.write("Logged out successfully.")
            st.session_state.logged_in = False
            st.rerun()
        

def main():
    user()
    farmer()
    milk_collection()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if st.session_state.logged_in:
        home_page()
    else:
        col1, col2 = st.columns([1, 0.1])  # Adjust the width ratio to minimize the gap
        with col1:
            page = st.radio("  ", ["Login", "Registration"], key='page', horizontal=True)

        if page == 'Login':
            with st.form(key='login-form',clear_on_submit=False):
                user_name = st.text_input('User Name')
                password = st.text_input('Password', type='password')
                
                if st.form_submit_button("Login"):
                    conn = sqlite3.connect('milk_collection_system.db')
                    cur = conn.cursor()
                    data = cur.execute("SELECT * FROM User WHERE userName = ? AND password = ?", (user_name, password)).fetchone()
                    conn.close()
                    
                    if data:
                        st.session_state.logged_in = True
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Incorrect username or password.")
        
        elif page == 'Registration':
            with st.form(key='registration-form',clear_on_submit=False):
                user_name = st.text_input('User Name')
                password = st.text_input('Password', type='password')
                
                if st.form_submit_button("Register"):
                    conn = sqlite3.connect('milk_collection_system.db')
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM USER WHERE userName = ?", (user_name,))
                    existing_user = cur.fetchone()
                    conn.close()
                    
                    if existing_user:
                        st.error("Username already exists. Please choose a different username.")
                    else:
                        status = insert_new_user(user_name, password)
                        if status == 'success':
                            st.success("Registered successfully!")
                            st.stop()
                        else:
                            st.error("Failed to register. Please try again.")
                

# Run the app
if __name__ == '__main__':
    main()
    
    
    
    









