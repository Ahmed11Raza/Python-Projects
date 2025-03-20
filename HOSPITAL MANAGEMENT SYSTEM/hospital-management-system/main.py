import streamlit as st
import pandas as pd
import os
from datetime import datetime
import hashlib
import uuid
import plotly.express as px
import csv
import json

# Create data directory if it doesn't exist
DATA_DIR = "hospital_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# File paths for CSV data storage
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
PATIENTS_FILE = os.path.join(DATA_DIR, "patients.csv")
DOCTORS_FILE = os.path.join(DATA_DIR, "doctors.csv")
APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.csv")
PRESCRIPTIONS_FILE = os.path.join(DATA_DIR, "prescriptions.csv")
BILLING_FILE = os.path.join(DATA_DIR, "billing.csv")

# Initialize the CSV files if they don't exist
def init_csv_files():
    # Define the headers for each CSV file
    files_headers = {
        USERS_FILE: ["id", "username", "password", "role", "name", "created_at"],
        PATIENTS_FILE: ["id", "name", "dob", "gender", "contact", "address", "email", "blood_group", "medical_history", "registered_on"],
        DOCTORS_FILE: ["id", "name", "specialization", "contact", "email", "working_hours", "joined_on"],
        APPOINTMENTS_FILE: ["id", "patient_id", "doctor_id", "date", "time", "status", "reason", "notes", "created_at"],
        PRESCRIPTIONS_FILE: ["id", "appointment_id", "medication", "dosage", "instructions", "created_at"],
        BILLING_FILE: ["id", "patient_id", "appointment_id", "description", "amount", "payment_status", "payment_date", "created_at"]
    }
    
    # Create the files if they don't exist
    for file_path, headers in files_headers.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
    
    # Add admin user if not exists
    if os.path.exists(USERS_FILE):
        users_df = pd.read_csv(USERS_FILE)
        if users_df.empty or "admin" not in users_df["username"].values:
            hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
            admin_data = {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "password": hashed_password,
                "role": "admin",
                "name": "Administrator",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            users_df = pd.concat([users_df, pd.DataFrame([admin_data])], ignore_index=True)
            users_df.to_csv(USERS_FILE, index=False)

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User authentication
def authenticate(username, password):
    init_csv_files()
    if os.path.exists(USERS_FILE):
        users_df = pd.read_csv(USERS_FILE)
        hashed_password = hash_password(password)
        user = users_df[(users_df["username"] == username) & (users_df["password"] == hashed_password)]
        if not user.empty:
            return user.iloc[0].to_dict()
    return None

# CRUD operations for patients
def add_patient(name, dob, gender, contact, address, email, blood_group, medical_history):
    init_csv_files()
    patients_df = pd.read_csv(PATIENTS_FILE)
    
    patient_id = str(uuid.uuid4())
    new_patient = {
        "id": patient_id,
        "name": name,
        "dob": dob,
        "gender": gender,
        "contact": contact,
        "address": address,
        "email": email,
        "blood_group": blood_group,
        "medical_history": medical_history,
        "registered_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    patients_df = pd.concat([patients_df, pd.DataFrame([new_patient])], ignore_index=True)
    patients_df.to_csv(PATIENTS_FILE, index=False)
    return patient_id

def get_all_patients():
    init_csv_files()
    if os.path.exists(PATIENTS_FILE):
        return pd.read_csv(PATIENTS_FILE)
    return pd.DataFrame()

def get_patient(patient_id):
    init_csv_files()
    patients_df = pd.read_csv(PATIENTS_FILE)
    patient = patients_df[patients_df["id"] == patient_id]
    if not patient.empty:
        return patient.iloc[0].to_dict()
    return None

def update_patient(patient_id, name, dob, gender, contact, address, email, blood_group, medical_history):
    init_csv_files()
    patients_df = pd.read_csv(PATIENTS_FILE)
    idx = patients_df.index[patients_df["id"] == patient_id].tolist()
    
    if idx:
        patients_df.at[idx[0], "name"] = name
        patients_df.at[idx[0], "dob"] = dob
        patients_df.at[idx[0], "gender"] = gender
        patients_df.at[idx[0], "contact"] = contact
        patients_df.at[idx[0], "address"] = address
        patients_df.at[idx[0], "email"] = email
        patients_df.at[idx[0], "blood_group"] = blood_group
        patients_df.at[idx[0], "medical_history"] = medical_history
        
        patients_df.to_csv(PATIENTS_FILE, index=False)
        return True
    return False

def delete_patient(patient_id):
    init_csv_files()
    patients_df = pd.read_csv(PATIENTS_FILE)
    patients_df = patients_df[patients_df["id"] != patient_id]
    patients_df.to_csv(PATIENTS_FILE, index=False)

# CRUD operations for doctors
def add_doctor(name, specialization, contact, email, working_hours):
    init_csv_files()
    doctors_df = pd.read_csv(DOCTORS_FILE)
    
    doctor_id = str(uuid.uuid4())
    new_doctor = {
        "id": doctor_id,
        "name": name,
        "specialization": specialization,
        "contact": contact,
        "email": email,
        "working_hours": working_hours,
        "joined_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    doctors_df = pd.concat([doctors_df, pd.DataFrame([new_doctor])], ignore_index=True)
    doctors_df.to_csv(DOCTORS_FILE, index=False)
    return doctor_id

def get_all_doctors():
    init_csv_files()
    if os.path.exists(DOCTORS_FILE):
        return pd.read_csv(DOCTORS_FILE)
    return pd.DataFrame()

def get_doctor(doctor_id):
    init_csv_files()
    doctors_df = pd.read_csv(DOCTORS_FILE)
    doctor = doctors_df[doctors_df["id"] == doctor_id]
    if not doctor.empty:
        return doctor.iloc[0].to_dict()
    return None

def update_doctor(doctor_id, name, specialization, contact, email, working_hours):
    init_csv_files()
    doctors_df = pd.read_csv(DOCTORS_FILE)
    idx = doctors_df.index[doctors_df["id"] == doctor_id].tolist()
    
    if idx:
        doctors_df.at[idx[0], "name"] = name
        doctors_df.at[idx[0], "specialization"] = specialization
        doctors_df.at[idx[0], "contact"] = contact
        doctors_df.at[idx[0], "email"] = email
        doctors_df.at[idx[0], "working_hours"] = working_hours
        
        doctors_df.to_csv(DOCTORS_FILE, index=False)
        return True
    return False

def delete_doctor(doctor_id):
    init_csv_files()
    doctors_df = pd.read_csv(DOCTORS_FILE)
    doctors_df = doctors_df[doctors_df["id"] != doctor_id]
    doctors_df.to_csv(DOCTORS_FILE, index=False)

# CRUD operations for appointments
def add_appointment(patient_id, doctor_id, date, time, status, reason, notes):
    init_csv_files()
    appointments_df = pd.read_csv(APPOINTMENTS_FILE)
    
    appointment_id = str(uuid.uuid4())
    new_appointment = {
        "id": appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "date": date,
        "time": time,
        "status": status,
        "reason": reason,
        "notes": notes,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    appointments_df = pd.concat([appointments_df, pd.DataFrame([new_appointment])], ignore_index=True)
    appointments_df.to_csv(APPOINTMENTS_FILE, index=False)
    return appointment_id

def get_all_appointments():
    init_csv_files()
    if os.path.exists(APPOINTMENTS_FILE) and os.path.exists(PATIENTS_FILE) and os.path.exists(DOCTORS_FILE):
        appointments_df = pd.read_csv(APPOINTMENTS_FILE)
        patients_df = pd.read_csv(PATIENTS_FILE)
        doctors_df = pd.read_csv(DOCTORS_FILE)
        
        if not appointments_df.empty and not patients_df.empty and not doctors_df.empty:
            # Merge dataframes to get patient and doctor names
            result_df = appointments_df.merge(
                patients_df[["id", "name"]],
                left_on="patient_id",
                right_on="id",
                how="left",
                suffixes=("", "_patient")
            )
            result_df = result_df.rename(columns={"name": "patient_name"})
            
            result_df = result_df.merge(
                doctors_df[["id", "name"]],
                left_on="doctor_id",
                right_on="id",
                how="left",
                suffixes=("", "_doctor")
            )
            result_df = result_df.rename(columns={"name": "doctor_name"})
            
            # Select relevant columns
            result_df = result_df[["id", "patient_name", "doctor_name", "date", "time", "status", "reason"]]
            return result_df
    
    return pd.DataFrame()

def get_appointment(appointment_id):
    init_csv_files()
    appointments_df = pd.read_csv(APPOINTMENTS_FILE)
    patients_df = pd.read_csv(PATIENTS_FILE)
    doctors_df = pd.read_csv(DOCTORS_FILE)
    
    appointment = appointments_df[appointments_df["id"] == appointment_id]
    
    if not appointment.empty:
        appointment_data = appointment.iloc[0].to_dict()
        
        # Get patient name
        patient = patients_df[patients_df["id"] == appointment_data["patient_id"]]
        if not patient.empty:
            appointment_data["patient_name"] = patient.iloc[0]["name"]
        else:
            appointment_data["patient_name"] = "Unknown"
        
        # Get doctor name
        doctor = doctors_df[doctors_df["id"] == appointment_data["doctor_id"]]
        if not doctor.empty:
            appointment_data["doctor_name"] = doctor.iloc[0]["name"]
        else:
            appointment_data["doctor_name"] = "Unknown"
        
        return appointment_data
    
    return None

def update_appointment_status(appointment_id, status):
    init_csv_files()
    appointments_df = pd.read_csv(APPOINTMENTS_FILE)
    idx = appointments_df.index[appointments_df["id"] == appointment_id].tolist()
    
    if idx:
        appointments_df.at[idx[0], "status"] = status
        appointments_df.to_csv(APPOINTMENTS_FILE, index=False)
        return True
    return False

# Prescription functions
def add_prescription(appointment_id, medication, dosage, instructions):
    init_csv_files()
    prescriptions_df = pd.read_csv(PRESCRIPTIONS_FILE)
    
    prescription_id = str(uuid.uuid4())
    new_prescription = {
        "id": prescription_id,
        "appointment_id": appointment_id,
        "medication": medication,
        "dosage": dosage,
        "instructions": instructions,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    prescriptions_df = pd.concat([prescriptions_df, pd.DataFrame([new_prescription])], ignore_index=True)
    prescriptions_df.to_csv(PRESCRIPTIONS_FILE, index=False)
    return prescription_id

def get_prescriptions_by_appointment(appointment_id):
    init_csv_files()
    if os.path.exists(PRESCRIPTIONS_FILE):
        prescriptions_df = pd.read_csv(PRESCRIPTIONS_FILE)
        return prescriptions_df[prescriptions_df["appointment_id"] == appointment_id]
    return pd.DataFrame()

# Billing functions
def add_bill(patient_id, appointment_id, description, amount, payment_status):
    init_csv_files()
    billing_df = pd.read_csv(BILLING_FILE)
    
    bill_id = str(uuid.uuid4())
    payment_date = datetime.now().strftime("%Y-%m-%d") if payment_status == "Paid" else None
    
    new_bill = {
        "id": bill_id,
        "patient_id": patient_id,
        "appointment_id": appointment_id if appointment_id else "",
        "description": description,
        "amount": amount,
        "payment_status": payment_status,
        "payment_date": payment_date,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    billing_df = pd.concat([billing_df, pd.DataFrame([new_bill])], ignore_index=True)
    billing_df.to_csv(BILLING_FILE, index=False)
    return bill_id

def get_patient_bills(patient_id):
    init_csv_files()
    if os.path.exists(BILLING_FILE):
        billing_df = pd.read_csv(BILLING_FILE)
        return billing_df[billing_df["patient_id"] == patient_id].sort_values("created_at", ascending=False)
    return pd.DataFrame()

def update_bill_status(bill_id, status):
    init_csv_files()
    billing_df = pd.read_csv(BILLING_FILE)
    idx = billing_df.index[billing_df["id"] == bill_id].tolist()
    
    if idx:
        billing_df.at[idx[0], "payment_status"] = status
        if status == "Paid":
            billing_df.at[idx[0], "payment_date"] = datetime.now().strftime("%Y-%m-%d")
        else:
            billing_df.at[idx[0], "payment_date"] = None
        
        billing_df.to_csv(BILLING_FILE, index=False)
        return True
    return False

# Dashboard metrics and statistics
def get_dashboard_metrics():
    init_csv_files()
    
    # Total patients
    patients_df = pd.read_csv(PATIENTS_FILE)
    total_patients = len(patients_df)
    
    # Total doctors
    doctors_df = pd.read_csv(DOCTORS_FILE)
    total_doctors = len(doctors_df)
    
    # Appointments today
    appointments_df = pd.read_csv(APPOINTMENTS_FILE)
    today = datetime.now().strftime("%Y-%m-%d")
    appointments_today = len(appointments_df[appointments_df["date"] == today])
    
    # Pending bills
    billing_df = pd.read_csv(BILLING_FILE)
    pending_bills = len(billing_df[billing_df["payment_status"] == "Pending"])
    
    # Total revenue this month
    first_day = datetime(datetime.now().year, datetime.now().month, 1).strftime("%Y-%m-%d")
    paid_bills = billing_df[
        (billing_df["payment_status"] == "Paid") & 
        (billing_df["payment_date"] >= first_day)
    ]
    revenue = paid_bills["amount"].sum() if not paid_bills.empty else 0
    
    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "appointments_today": appointments_today,
        "pending_bills": pending_bills,
        "monthly_revenue": revenue
    }

def get_appointment_stats():
    init_csv_files()
    
    appointments_df = pd.read_csv(APPOINTMENTS_FILE)
    doctors_df = pd.read_csv(DOCTORS_FILE)
    
    # If no appointments yet, return empty stats
    if appointments_df.empty:
        return {
            "status": pd.DataFrame(columns=["status", "count"]),
            "by_doctor": pd.DataFrame(columns=["name", "count"]),
            "by_day": pd.DataFrame(columns=["day_of_week", "day_name", "count"])
        }
    
    # Appointments by status
    status_counts = appointments_df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    
    # Appointments by doctor
    doctor_counts = appointments_df["doctor_id"].value_counts().reset_index()
    doctor_counts.columns = ["doctor_id", "count"]
    
    # Merge with doctors to get names
    if not doctors_df.empty and not doctor_counts.empty:
        doctor_counts = doctor_counts.merge(doctors_df[["id", "name"]], left_on="doctor_id", right_on="id", how="left")
        doctor_counts = doctor_counts[["name", "count"]].sort_values("count", ascending=False).head(5)
    else:
        doctor_counts = pd.DataFrame(columns=["name", "count"])
    
    # Appointments by day of week (for the last 30 days)
    thirty_days_ago = (datetime.now() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
    recent_appointments = appointments_df[appointments_df["date"] >= thirty_days_ago]
    
    # Convert date strings to datetime and extract day of week
    if not recent_appointments.empty:
        recent_appointments["datetime"] = pd.to_datetime(recent_appointments["date"])
        recent_appointments["day_of_week"] = recent_appointments["datetime"].dt.dayofweek
        day_counts = recent_appointments["day_of_week"].value_counts().reset_index()
        day_counts.columns = ["day_of_week", "count"]
        
        # Add day names
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_counts["day_name"] = day_counts["day_of_week"].apply(lambda x: day_names[x])
        day_counts = day_counts.sort_values("day_of_week")
    else:
        day_counts = pd.DataFrame(columns=["day_of_week", "day_name", "count"])
    
    return {
        "status": status_counts,
        "by_doctor": doctor_counts,
        "by_day": day_counts
    }

# User management functions
def add_user(username, password, role, name):
    # Check if username already exists
    if username in users_df["username"].values:
        return False
    init_csv_files()
    users_df = pd.read_csv(USERS_FILE)
    
    # Check if username already exists
    if username in users_df["username"].values:
        return False
    
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(password)
    
    new_user = {
        "id": user_id,
        "username": username,
        "password": hashed_password,
        "role": role,
        "name": name,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    new_user = {
        "id": user_id,
        "username": username,
        "password": hashed_password,
        "role": role,
        "name": name,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
    users_df.to_csv(USERS_FILE, index=False)
    return True

def get_all_users():
    init_csv_files()
    if os.path.exists(USERS_FILE):
        users_df = pd.read_csv(USERS_FILE)
        return users_df[["id", "username", "role", "name", "created_at"]]
    return pd.DataFrame()

def delete_user(user_id):
    init_csv_files()
    users_df = pd.read_csv(USERS_FILE)
    
    # Don't delete the last admin
    admins = users_df[users_df["role"] == "admin"]
    if len(admins) <= 1 and user_id in admins["id"].values:
        return False
    
    users_df = users_df[users_df["id"] != user_id]
    users_df.to_csv(USERS_FILE, index=False)
    return True

# UI Functions
def login_page():
    st.title("Hospital Management System")
    st.subheader("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = user["role"]
            st.session_state.user_name = user["name"]
            st.success(f"Welcome {st.session_state.user_name}!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

def main_layout():
    # Sidebar navigation
    st.sidebar.title(f"Welcome, {st.session_state.user_name}")
    st.sidebar.subheader(f"Role: {st.session_state.user_role.capitalize()}")
    
    menu_options = ["Dashboard", "Patients", "Doctors", "Appointments", "Prescriptions", "Billing"]
    
    if st.session_state.user_role == "admin":
        menu_options.append("User Management")
    
        menu_selection = st.sidebar.selectbox("Menu", menu_options)
        
        if st.sidebar.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
        
        # Main content based on menu selection
        if menu_selection == "Dashboard":
            show_dashboard()
        elif menu_selection == "Patients":
            show_patients_page()
        elif menu_selection == "Doctors":
            show_doctors_page()
        elif menu_selection == "Appointments":
            show_appointments_page()
        elif menu_selection == "Prescriptions":
            show_prescriptions_page()
        elif menu_selection == "Billing":
            show_billing_page()
        elif menu_selection == "User Management" and st.session_state.user_role == "admin":
            show_user_management_page()
    
    def show_appointments_page():
        st.title("Appointment Management")
        # Add your code to manage appointments here
    
    def show_doctors_page():
        st.title("Doctor Management")
        # Add your code to manage doctors here
    
    def show_prescriptions_page():
        st.title("Prescription Management")
        # Add your code to manage prescriptions here
    
    def show_billing_page():
        st.title("Billing Management")
        # Add your code to manage billing here

    def show_user_management_page():
        st.title("User Management")
        
        tab1, tab2 = st.tabs(["User List", "Add New User"])
        
        with tab1:
            users_df = get_all_users()
            if not users_df.empty:
                st.dataframe(users_df)
                
                selected_user = st.selectbox("Select user to delete:", users_df['username'])
                if st.button("Delete User"):
                    user_id = users_df[users_df['username'] == selected_user]['id'].iloc[0]
                    if delete_user(user_id):
                        st.success(f"User {selected_user} deleted successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Cannot delete the last admin user!")
            else:
                st.info("No users found.")
        
        with tab2:
            with st.form("add_user_form"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["staff", "admin"])
                new_name = st.text_input("Full Name")
                
                if st.form_submit_button("Add User"):
                    if add_user(new_username, new_password, new_role, new_name):
                        st.success("User added successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Username already exists!")

def show_dashboard():
    st.title("Hospital Dashboard")
    metrics = get_dashboard_metrics()
    
    # Display key metrics in a grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Patients", metrics["total_patients"])
        
    with col2:
        st.metric("Total Doctors", metrics["total_doctors"])
        
    with col3:
        st.metric("Today's Appointments", metrics["appointments_today"])
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.metric("Pending Bills", metrics["pending_bills"])
        
    with col5:
        st.metric("Monthly Revenue", f"${metrics['monthly_revenue']:,.2f}")
    
    st.subheader("Appointment Statistics")
    
    stats = get_appointment_stats()
    
    # Only show charts if there's data
    if not stats["status"].empty:
        # Appointments by status
        status_fig = px.pie(stats["status"], values='count', names='status', 
                            title='Appointments by Status',
                            color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(status_fig)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top doctors by appointments
            if not stats["by_doctor"].empty:
                doctor_fig = px.bar(stats["by_doctor"], x='name', y='count', 
                                    title='Top Doctors by Appointments',
                                    labels={'name': 'Doctor', 'count': 'Number of Appointments'},
                                    color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(doctor_fig)
            else:
                st.info("No doctor appointment data available")
        
        with col2:
            # Appointments by day of week
            if not stats["by_day"].empty:
                day_fig = px.bar(stats["by_day"], x='day_name', y='count', 
                                  title='Appointments by Day of Week (Last 30 Days)',
                                  labels={'day_name': 'Day', 'count': 'Number of Appointments'},
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(day_fig)
            else:
                st.info("No recent appointment data available")
    else:
        st.info("No appointment data available to display statistics")

def show_patients_page():
    st.title("Patient Management")
    
    tab1, tab2 = st.tabs(["Patient Records", "Add New Patient"])
    
    with tab1:
        patients_df = get_all_patients()
        if not patients_df.empty:
            # Add search functionality
            search_term = st.text_input("Search Patients (Name or Contact)")
            if search_term:
                patients_df = patients_df[
                    patients_df["name"].str.contains(search_term, case=False, na=False) | 
                    patients_df["contact"].str.contains(search_term, case=False, na=False)
                ]
            
            st.dataframe(patients_df[['id', 'name', 'gender', 'dob', 'contact', 'blood_group']])
            
            # Patient details section
            st.subheader("Patient Details")
            
            if not patients_df.empty:
                patient_options = patients_df['name'].tolist()
                patient_options.insert(0, "Select a patient")
                selected_patient_name = st.selectbox("Select Patient", patient_options)
                
                if selected_patient_name != "Select a patient":
                    patient_row = patients_df[patients_df['name'] == selected_patient_name].iloc[0]
                    selected_patient_id = patient_row['id']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Name:** {patient_row['name']}")
                        st.write(f"**Gender:** {patient_row['gender']}")
                        st.write(f"**Date of Birth:** {patient_row['dob']}")
                        st.write(f"**Blood Group:** {patient_row['blood_group']}")
                    
                    with col2:
                        st.write(f"**Contact:** {patient_row['contact']}")
                        st.write(f"**Email:** {patient_row['email']}")
                        st.write(f"**Address:** {patient_row['address']}")
                        st.write(f"**Registered On:** {patient_row['registered_on']}")
                    
                    st.write(f"**Medical History:**")
                    st.text_area("", value=patient_row['medical_history'], height=100, disabled=True)
                    
                    # Edit and Delete options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Edit Patient"):
                            st.session_state.edit_patient = patient_row.to_dict()
                            st.experimental_rerun()
                    
                    with col2:
                        if st.button("Delete Patient"):
                            delete_patient(selected_patient_id)
                            st.success(f"Patient {patient_row['name']} deleted successfully!")
                            st.experimental_rerun()
                    
                    # Show patient bills
                    st.subheader("Patient Bills")
                    bills_df = get_patient_bills(selected_patient_id)
                    if not bills_df.empty:
                        st.dataframe(bills_df[['id', 'description', 'amount', 'payment_status', 'payment_date', 'created_at']])
                    else:
                        st.info("No billing records found for this patient.")
            else:
                st.info("No patients match your search criteria.")
        else:
            st.info("No patients registered yet.")
    
    with tab2:
        # Check if we're in edit mode
        is_edit_mode = 'edit_patient' in st.session_state
        
        if is_edit_mode:
            st.subheader(f"Edit Patient: {st.session_state.edit_patient['name']}")
            patient_data = st.session_state.edit_patient
            patient_id = patient_data['id']
        else:
            st.subheader("Register New Patient")
            patient_data = {
                'name': '',
                'dob': datetime.now().date(),
                'gender': 'Male',
                'contact': '',
                'address': '',
                'email': '',
                'blood_group': 'A+',
                'medical_history': ''
            }
            patient_id = None
        
        # Form for adding/editing patient
        with st.form("patient_form"):
            name = st.text_input("Full Name", value=patient_data['name'])
            
            col1, col2 = st.columns(2)
            with col1:
                dob = st.date_input("Date of Birth", value=pd.to_datetime(patient_data['dob']).date() if isinstance(patient_data['dob'], str) else patient_data['dob'])
                gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(patient_data['gender']) if patient_data['gender'] in ["Male", "Female", "Other"] else 0)
                blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], index=0)# Correct syntax:
blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

