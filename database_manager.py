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

# ========== ROOM ALLOCATION & BED MANAGEMENT FUNCTIONS ==========

def get_all_wards():
    """
    Fetches all hospital wards.
    Returns: List of tuples (ward_id, ward_name, ward_type)
    """
    try:
        conn = create_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        query = """
        SELECT ward_id, ward_name, ward_type
        FROM Wards
        ORDER BY ward_name ASC
        """
        cursor.execute(query)
        wards = cursor.fetchall()
        cursor.close()
        conn.close()
        return wards if wards else []
    except Error as e:
        print(f"❌ Error fetching wards: {e}")
        return []


def get_available_beds(ward_id):
    """
    Gets available (unoccupied) beds in a specific ward.
    Args: ward_id (int): ID of the ward
    Returns: List of tuples (bed_id, ward_id, status)
    """
    try:
        conn = create_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        query = """
        SELECT bed_id, ward_id, status
        FROM Beds
        WHERE ward_id = %s AND status = 'Available'
        ORDER BY bed_id ASC
        """
        cursor.execute(query, (ward_id,))
        beds = cursor.fetchall()
        cursor.close()
        conn.close()
        return beds if beds else []
    except Error as e:
        print(f"❌ Error fetching available beds: {e}")
        return []


def get_all_beds_in_ward(ward_id):
    """
    Gets all beds (available + occupied) in a specific ward.
    Args: ward_id (int): ID of the ward
    Returns: List of tuples (bed_id, ward_id, status)
    """
    try:
        conn = create_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        query = """
        SELECT bed_id, ward_id, status
        FROM Beds
        WHERE ward_id = %s
        ORDER BY bed_id ASC
        """
        cursor.execute(query, (ward_id,))
        beds = cursor.fetchall()
        cursor.close()
        conn.close()
        return beds if beds else []
    except Error as e:
        print(f"❌ Error fetching beds in ward: {e}")
        return []


def admit_patient(patient_id, bed_id, admission_date):
    """
    Admits a patient to a specific bed with validation.
    Validates that the patient exists, the bed is available,
    and the patient does not already have an active admission.
    Args:
        patient_id (int): ID of the patient
        bed_id (int): ID of the bed to assign
        admission_date (str): Admission date in YYYY-MM-DD format
    Returns: (bool, str) - (success, message)
    """
    try:
        conn = create_connection()
        if conn is None:
            return False, "❌ Database connection failed."
        cursor = conn.cursor()

        # Validate patient exists
        cursor.execute("SELECT patient_id FROM Patients WHERE patient_id = %s", (patient_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return False, f"❌ Patient ID {patient_id} not found."

        # Validate bed exists and is available
        cursor.execute("SELECT status FROM Beds WHERE bed_id = %s", (bed_id,))
        bed = cursor.fetchone()
        if bed is None:
            cursor.close()
            conn.close()
            return False, f"❌ Bed ID {bed_id} not found."
        if bed[0] != 'Available':
            cursor.close()
            conn.close()
            return False, f"❌ Bed {bed_id} is currently occupied."

        # Check for existing active admission
        cursor.execute(
            "SELECT admission_id FROM Admissions WHERE patient_id = %s AND discharge_date IS NULL",
            (patient_id,)
        )
        if cursor.fetchone() is not None:
            cursor.close()
            conn.close()
            return False, f"❌ Patient {patient_id} already has an active admission."

        # Insert admission record
        cursor.execute(
            """
            INSERT INTO Admissions (patient_id, bed_id, admission_date)
            VALUES (%s, %s, %s)
            """,
            (patient_id, bed_id, admission_date)
        )

        # Mark bed as occupied
        cursor.execute(
            "UPDATE Beds SET status = 'Occupied' WHERE bed_id = %s",
            (bed_id,)
        )

        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return True, f"✅ Patient {patient_id} admitted to Bed {bed_id}. Admission ID: {new_id}"

    except Error as e:
        print(f"❌ Error admitting patient: {e}")
        return False, f"❌ Error: {e}"


def get_patient_active_admission(patient_id):
    """
    Gets the active (non-discharged) admission for a patient.
    Args: patient_id (int): ID of the patient
    Returns: Tuple (admission_id, patient_id, bed_id, admission_date, ward_name, ward_type)
             or None if no active admission exists.
    """
    try:
        conn = create_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        query = """
        SELECT
            a.admission_id,
            a.patient_id,
            a.bed_id,
            a.admission_date,
            w.ward_name,
            w.ward_type
        FROM Admissions a
        LEFT JOIN Beds b ON a.bed_id = b.bed_id
        LEFT JOIN Wards w ON b.ward_id = w.ward_id
        WHERE a.patient_id = %s AND a.discharge_date IS NULL
        LIMIT 1
        """
        cursor.execute(query, (patient_id,))
        admission = cursor.fetchone()
        cursor.close()
        conn.close()
        return admission
    except Error as e:
        print(f"❌ Error fetching active admission: {e}")
        return None


def get_all_active_admissions():
    """
    Gets all currently active (non-discharged) admissions.
    Returns: List of tuples (admission_id, patient_id, full_name, bed_id, ward_name, ward_type, admission_date)
    """
    try:
        conn = create_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        query = """
        SELECT
            a.admission_id,
            a.patient_id,
            CONCAT(p.first_name, ' ', p.last_name) AS full_name,
            a.bed_id,
            w.ward_name,
            w.ward_type,
            a.admission_date
        FROM Admissions a
        JOIN Patients p ON a.patient_id = p.patient_id
        LEFT JOIN Beds b ON a.bed_id = b.bed_id
        LEFT JOIN Wards w ON b.ward_id = w.ward_id
        WHERE a.discharge_date IS NULL
        ORDER BY a.admission_date DESC
        """
        cursor.execute(query)
        admissions = cursor.fetchall()
        cursor.close()
        conn.close()
        return admissions if admissions else []
    except Error as e:
        print(f"❌ Error fetching active admissions: {e}")
        return []


def discharge_patient(admission_id):
    """
    Discharges a patient by setting the discharge_date to now.
    The Bed Manager trigger will automatically update the bed status to 'Available'.
    If no trigger exists, this function updates the bed status directly as a fallback.
    Args: admission_id (int): ID of the admission record
    Returns: (bool, str) - (success, message)
    """
    try:
        conn = create_connection()
        if conn is None:
            return False, "❌ Database connection failed."
        cursor = conn.cursor()

        # Validate admission exists and is active
        cursor.execute(
            "SELECT patient_id, bed_id FROM Admissions WHERE admission_id = %s AND discharge_date IS NULL",
            (admission_id,)
        )
        admission = cursor.fetchone()
        if admission is None:
            cursor.close()
            conn.close()
            return False, f"❌ Active admission with ID {admission_id} not found."

        patient_id, bed_id = admission

        # Set discharge date to current timestamp
        cursor.execute(
            "UPDATE Admissions SET discharge_date = NOW() WHERE admission_id = %s",
            (admission_id,)
        )

        # Update bed status to Available (fallback if Bed Manager trigger is not present)
        cursor.execute(
            "UPDATE Beds SET status = 'Available' WHERE bed_id = %s",
            (bed_id,)
        )

        conn.commit()
        cursor.close()
        conn.close()
        return True, f"✅ Patient {patient_id} discharged from Bed {bed_id}. Admission {admission_id} closed."

    except Error as e:
        print(f"❌ Error discharging patient: {e}")
        return False, f"❌ Error: {e}"


def get_ward_bed_summary():
    """
    Gets a summary of beds per ward showing total, available, and occupied counts.
    Returns: List of tuples (ward_id, ward_name, ward_type, total_beds, available_beds, occupied_beds)
    """
    try:
        conn = create_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        query = """
        SELECT
            w.ward_id,
            w.ward_name,
            w.ward_type,
            COUNT(b.bed_id)                                          AS total_beds,
            SUM(CASE WHEN b.status = 'Available' THEN 1 ELSE 0 END) AS available_beds,
            SUM(CASE WHEN b.status = 'Occupied'  THEN 1 ELSE 0 END) AS occupied_beds
        FROM Wards w
        LEFT JOIN Beds b ON w.ward_id = b.ward_id
        GROUP BY w.ward_id, w.ward_name, w.ward_type
        ORDER BY w.ward_name ASC
        """
        cursor.execute(query)
        summary = cursor.fetchall()
        cursor.close()
        conn.close()
        return summary if summary else []
    except Error as e:
        print(f"❌ Error fetching ward bed summary: {e}")
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
