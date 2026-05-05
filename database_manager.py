import mysql.connector
from mysql.connector import Error

def create_connection():
    """Establishes and returns a secure connection to the hospital database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Keeping your blank password!
            database='hospital_db'
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def get_all_doctors():
    """Fetches all doctors from the database with their department names."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Advanced Query: Joining Doctors and Departments tables
            query = """
                SELECT d.first_name, d.last_name, d.specialization, dept.department_name
                FROM Doctors d
                JOIN Departments dept ON d.department_id = dept.department_id;
            """
            cursor.execute(query)
            doctors = cursor.fetchall()
            return doctors
        except Error as e:
            print(f"Error fetching doctors: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

def insert_new_patient(first_name, last_name, dob, gender, phone, address, emergency_contact):
    """Securely inserts a brand new patient into the database."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # The SQL Query using %s placeholders for security
            query = """
                INSERT INTO Patients 
                (first_name, last_name, dob, gender, phone, address, emergency_contact)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            # The actual data we want to insert
            patient_data = (first_name, last_name, dob, gender, phone, address, emergency_contact)
            
            # Execute the query with the data
            cursor.execute(query, patient_data)
            
            # CRITICAL STEP: You must commit() to lock the changes into the database!
            conn.commit()
            
            print(f"Success! {first_name} {last_name} has been officially registered.")
            print(f"Their automatically assigned Patient ID is: {cursor.lastrowid}")
            
        except Error as e:
            print(f"Error inserting patient: {e}")
        finally:
            cursor.close()
            conn.close()

# ========== NEW PATIENT LIST VIEW FUNCTIONS ==========

def get_all_patients():
    """
    Fetches all registered patients from the database.
    Returns: List of tuples containing (patient_id, first_name, last_name, dob, gender, phone, address)
    """
    try:
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed")
            return []
        
        cursor = conn.cursor()
        query = """
        SELECT 
            patient_id,
            first_name,
            last_name,
            dob,
            gender,
            phone,
            address
        FROM Patients
        ORDER BY patient_id DESC
        """
        cursor.execute(query)
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return patients if patients else []
    
    except Error as e:
        print(f"❌ Error fetching patients: {e}")
        return []


def search_patients(search_term):
    """
    Searches for patients by name or phone number.
    Args: search_term (str): Name or phone number to search
    Returns: List of matching patient records
    """
    try:
        conn = create_connection()
        if conn is None:
            print("❌ Database connection failed")
            return []
        
        cursor = conn.cursor()
        query = """
        SELECT 
            patient_id,
            first_name,
            last_name,
            dob,
            gender,
            phone,
            address
        FROM Patients
        WHERE CONCAT(first_name, ' ', last_name) LIKE %s 
           OR phone LIKE %s
        ORDER BY first_name ASC
        """
        search_pattern = f"%{search_term}%"
        cursor.execute(query, (search_pattern, search_pattern))
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return patients if patients else []
    
    except Error as e:
        print(f"❌ Error searching patients: {e}")
        return []


def get_patient_details(patient_id):
    """
    Fetches detailed information for a specific patient.
    Args: patient_id (int): ID of the patient
    Returns: Tuple with complete patient record or None
    """
    try:
        conn = create_connection()
        if conn is None:
            return None
        
        cursor = conn.cursor()
        query = """
        SELECT 
            patient_id,
            first_name,
            last_name,
            dob,
            gender,
            phone,
            address,
            emergency_contact
        FROM Patients
        WHERE patient_id = %s
        """
        cursor.execute(query, (patient_id,))
        patient = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return patient
    
    except Error as e:
        print(f"❌ Error fetching patient details: {e}")
        return None


def get_patient_admission_history(patient_id):
    """
    Fetches admission history for a patient.
    Args: patient_id (int): ID of the patient
    Returns: List of admission records with ward and bed information
    """
    try:
        conn = create_connection()
        if conn is None:
            return []
        
        cursor = conn.cursor()
        query = """
        SELECT 
            a.admission_id,
            a.admission_date,
            a.discharge_date,
            w.ward_name,
            b.bed_id,
            w.ward_type
        FROM Admissions a
        LEFT JOIN Beds b ON a.bed_id = b.bed_id
        LEFT JOIN Wards w ON b.ward_id = w.ward_id
        WHERE a.patient_id = %s
        ORDER BY a.admission_date DESC
        """
        cursor.execute(query, (patient_id,))
        admissions = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return admissions if admissions else []
    
    except Error as e:
        print(f"❌ Error fetching admission history: {e}")
        return []

# --- TESTING THE NEW INSERT FUNCTION ---
if __name__ == "__main__":
    print("\n--- Registering a New Patient ---")
    
    # Testing our function with a new localized patient record
    insert_new_patient(
        first_name='Omar',
        last_name='Shafiq',
        dob='1995-10-12',
        gender='Male',
        phone='0333-5556677',
        address='House 45, Sector F-10, Islamabad',
        emergency_contact='0333-5556688'
    )
    print("---------------------------------\n")
