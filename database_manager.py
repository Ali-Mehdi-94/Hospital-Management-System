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
                SELECT d.doctor_id, d.first_name, d.last_name, d.specialization, dept.department_name
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


def get_all_departments():
    """Fetches all departments for doctor registration workflows."""
    try:
        conn = create_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT department_id, department_name
            FROM Departments
            ORDER BY department_name ASC
            """
        )
        departments = cursor.fetchall()
        cursor.close()
        conn.close()
        return departments if departments else []
    except Error as e:
        print(f"❌ Error fetching departments: {e}")
        return []


def insert_new_doctor(first_name, last_name, specialization, department_id):
    """Inserts a new doctor after validating the selected department."""
    try:
        conn = create_connection()
        if conn is None:
            return False, "❌ Database connection failed."
        cursor = conn.cursor()

        cursor.execute("SELECT department_id FROM Departments WHERE department_id = %s", (department_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return False, f"❌ Department ID {department_id} not found."

        cursor.execute(
            """
            INSERT INTO Doctors (first_name, last_name, specialization, department_id)
            VALUES (%s, %s, %s, %s)
            """,
            (first_name, last_name, specialization, department_id),
        )
        conn.commit()
        doctor_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return True, f"✅ Doctor added successfully (Doctor ID: {doctor_id})."
    except Error as e:
        print(f"❌ Error inserting doctor: {e}")
        return False, f"❌ Error: {e}"


def get_doctor_dependency_counts(doctor_id):
    """Returns dependency counts for a doctor (appointments, prescriptions)."""
    try:
        conn = create_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Appointments WHERE doctor_id = %s", (doctor_id,))
        appointments_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Prescriptions WHERE doctor_id = %s", (doctor_id,))
        prescriptions_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {"appointments": appointments_count, "prescriptions": prescriptions_count}
    except Error as e:
        print(f"❌ Error checking doctor dependencies: {e}")
        return None


def delete_doctor(doctor_id, confirm_cascade=False, dependency_counts=None):
    """
    Deletes a doctor. If dependent appointments/prescriptions exist, confirm_cascade must be True.
    Returns: (success: bool, message: str, dependency_counts: dict|None)
    """
    try:
        conn = create_connection()
        if conn is None:
            return False, "❌ Database connection failed.", None
        cursor = conn.cursor()

        cursor.execute("SELECT doctor_id FROM Doctors WHERE doctor_id = %s", (doctor_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return False, f"❌ Doctor ID {doctor_id} not found.", None

        if dependency_counts is None:
            cursor.execute("SELECT COUNT(*) FROM Appointments WHERE doctor_id = %s", (doctor_id,))
            appointments_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Prescriptions WHERE doctor_id = %s", (doctor_id,))
            dependency_counts = {
                "appointments": appointments_count,
                "prescriptions": cursor.fetchone()[0],
            }

        if (dependency_counts["appointments"] > 0 or dependency_counts["prescriptions"] > 0) and not confirm_cascade:
            cursor.close()
            conn.close()
            return (
                False,
                "⚠️ Doctor has related appointments/prescriptions. Confirmation required for cascade delete.",
                dependency_counts,
            )

        if not conn.in_transaction:
            conn.start_transaction()

        cursor.execute("DELETE FROM Appointments WHERE doctor_id = %s", (doctor_id,))
        cursor.execute("DELETE FROM Prescriptions WHERE doctor_id = %s", (doctor_id,))
        cursor.execute("DELETE FROM Doctors WHERE doctor_id = %s", (doctor_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"✅ Doctor ID {doctor_id} and related records deleted.", dependency_counts
    except Error as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print(f"❌ Error deleting doctor: {e}")
        return False, f"❌ Error: {e}", None

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
        normalized_phone_expr = (
            "REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone, '-', ''), ' ', ''), '+', ''), '(', ''), ')', '')"
        )
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
        ORDER BY patient_id ASC
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
           OR (%s <> '' AND {normalized_phone_expr} LIKE %s)
        ORDER BY first_name ASC
        """.format(normalized_phone_expr=normalized_phone_expr)
        search_pattern = f"%{search_term}%"
        normalized_search_term = "".join(ch for ch in str(search_term) if ch.isdigit())
        normalized_search_pattern = f"%{normalized_search_term}%"
        cursor.execute(
            query,
            (search_pattern, search_pattern, normalized_search_term, normalized_search_pattern),
        )
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


def add_ward(ward_name, ward_type):
    """Adds a new ward."""
    try:
        conn = create_connection()
        if conn is None:
            return False, "❌ Database connection failed."
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Wards (ward_name, ward_type)
            VALUES (%s, %s)
            """,
            (ward_name, ward_type),
        )
        conn.commit()
        ward_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return True, f"✅ Ward added successfully (Ward ID: {ward_id})."
    except Error as e:
        print(f"❌ Error adding ward: {e}")
        return False, f"❌ Error: {e}"


def delete_ward(ward_id):
    """Deletes a ward if it has no linked beds."""
    try:
        conn = create_connection()
        if conn is None:
            return False, "❌ Database connection failed."
        cursor = conn.cursor()
        cursor.execute("SELECT ward_id FROM Wards WHERE ward_id = %s", (ward_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return False, f"❌ Ward ID {ward_id} not found."

        cursor.execute("SELECT COUNT(*) FROM Beds WHERE ward_id = %s", (ward_id,))
        beds_count = cursor.fetchone()[0] or 0
        if beds_count > 0:
            cursor.close()
            conn.close()
            return False, f"⚠️ Ward {ward_id} has {beds_count} bed(s). Delete beds first."

        cursor.execute("DELETE FROM Wards WHERE ward_id = %s", (ward_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"✅ Ward ID {ward_id} deleted successfully."
    except Error as e:
        print(f"❌ Error deleting ward: {e}")
        return False, f"❌ Error: {e}"


def add_bed(ward_id):
    """Adds an available bed to the given ward."""
    try:
        conn = create_connection()
        if conn is None:
            return False, "❌ Database connection failed."
        cursor = conn.cursor()
        cursor.execute("SELECT ward_id FROM Wards WHERE ward_id = %s", (ward_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return False, f"❌ Ward ID {ward_id} not found."

        cursor.execute(
            """
            INSERT INTO Beds (ward_id, status)
            VALUES (%s, 'Available')
            """,
            (ward_id,),
        )
        conn.commit()
        bed_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return True, f"✅ Bed added successfully (Bed ID: {bed_id}) in Ward {ward_id}."
    except Error as e:
        print(f"❌ Error adding bed: {e}")
        return False, f"❌ Error: {e}"


def delete_bed(bed_id):
    """Deletes a bed if it is not occupied and has no admission history."""
    try:
        conn = create_connection()
        if conn is None:
            return False, "❌ Database connection failed."
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM Beds WHERE bed_id = %s", (bed_id,))
        bed_row = cursor.fetchone()
        if bed_row is None:
            cursor.close()
            conn.close()
            return False, f"❌ Bed ID {bed_id} not found."

        if str(bed_row[0]).lower() == "occupied":
            cursor.close()
            conn.close()
            return False, f"⚠️ Bed {bed_id} is currently occupied. Discharge patient first."

        cursor.execute("SELECT COUNT(*) FROM Admissions WHERE bed_id = %s", (bed_id,))
        admissions_count = cursor.fetchone()[0] or 0
        if admissions_count > 0:
            cursor.close()
            conn.close()
            return False, f"⚠️ Bed {bed_id} has admission records. Delete not allowed."

        cursor.execute("DELETE FROM Beds WHERE bed_id = %s", (bed_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"✅ Bed ID {bed_id} deleted successfully."
    except Error as e:
        print(f"❌ Error deleting bed: {e}")
        return False, f"❌ Error: {e}"


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


# ========== DIAGNOSTIC TESTS & VITALS MANAGEMENT FUNCTIONS ==========

def get_vital_ranges():
    """
    Returns the valid min/max ranges for each vital sign measurement.
    These match the CHECK constraints on the Diagnoses_and_Vitals table.
    Returns: dict with keys 'bp_systolic', 'bp_diastolic', 'heart_rate', 'sugar_level',
             each containing 'min', 'max', and 'unit'.
    """
    return {
        'bp_systolic':  {'min': 70,  'max': 200, 'unit': 'mmHg'},
        'bp_diastolic': {'min': 40,  'max': 130, 'unit': 'mmHg'},
        'heart_rate':   {'min': 40,  'max': 200, 'unit': 'bpm'},
        'sugar_level':  {'min': 50,  'max': 500, 'unit': 'mg/dL'},
    }


def insert_vital_record(admission_id, bp_sys, bp_dia, heart_beat, sugar_level):
    """
    Records a new set of vital signs for an active admission.
    Validates all values against the allowed ranges before inserting.
    Args:
        admission_id (int): ID of the active admission
        bp_sys (int/float): Blood pressure systolic (70-200 mmHg)
        bp_dia (int/float): Blood pressure diastolic (40-130 mmHg)
        heart_beat (int/float): Heart rate (40-200 bpm)
        sugar_level (int/float): Blood sugar level (50-500 mg/dL)
    Returns: (bool, str) - (success, message)
    """
    ranges = get_vital_ranges()

    # Client-side validation before hitting the database
    validations = [
        (bp_sys,      ranges['bp_systolic'],  'Blood Pressure Systolic'),
        (bp_dia,      ranges['bp_diastolic'], 'Blood Pressure Diastolic'),
        (heart_beat,  ranges['heart_rate'],   'Heart Rate'),
        (sugar_level, ranges['sugar_level'],  'Sugar Level'),
    ]
    for value, r, label in validations:
        try:
            v = float(value)
        except (TypeError, ValueError):
            return False, f"❌ {label} must be a numeric value."
        if not (r['min'] <= v <= r['max']):
            return False, (
                f"❌ {label} ({v} {r['unit']}) is out of range. "
                f"Valid range: {r['min']}–{r['max']} {r['unit']}."
            )

    try:
        conn = create_connection()
        if conn is None:
            return False, "❌ Database connection failed."
        cursor = conn.cursor()

        # Validate admission exists and is active
        cursor.execute(
            "SELECT admission_id FROM Admissions WHERE admission_id = %s AND discharge_date IS NULL",
            (admission_id,)
        )
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return False, f"❌ Active admission with ID {admission_id} not found."

        cursor.execute(
            """
            INSERT INTO Diagnoses_and_Vitals
                (admission_id, blood_pressure_sys, blood_pressure_dia, heart_beat, sugar_level, recorded_time)
            VALUES (%s, %s, %s, %s, %s, NOW())
            """,
            (admission_id, bp_sys, bp_dia, heart_beat, sugar_level)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return True, f"✅ Vital record saved. Vital ID: {new_id}"

    except Error as e:
        print(f"❌ Error inserting vital record: {e}")
        return False, f"❌ Error: {e}"


def get_patient_vitals(admission_id):
    """
    Fetches all vital sign records for a given admission, ordered by recorded time.
    Args: admission_id (int): ID of the admission
    Returns: List of tuples (vital_id, admission_id, bp_sys, bp_dia, heart_beat, sugar_level, recorded_time)
    """
    try:
        conn = create_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT vital_id, admission_id, blood_pressure_sys, blood_pressure_dia,
                   heart_beat, sugar_level, recorded_time
            FROM Diagnoses_and_Vitals
            WHERE admission_id = %s
            ORDER BY recorded_time DESC
            """,
            (admission_id,)
        )
        vitals = cursor.fetchall()
        cursor.close()
        conn.close()
        return vitals if vitals else []
    except Error as e:
        print(f"❌ Error fetching patient vitals: {e}")
        return []


def get_latest_vitals(admission_id):
    """
    Fetches the most recently recorded vital signs for an admission.
    Args: admission_id (int): ID of the admission
    Returns: Tuple (vital_id, admission_id, bp_sys, bp_dia, heart_beat, sugar_level, recorded_time)
             or None if no records exist.
    """
    try:
        conn = create_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT vital_id, admission_id, blood_pressure_sys, blood_pressure_dia,
                   heart_beat, sugar_level, recorded_time
            FROM Diagnoses_and_Vitals
            WHERE admission_id = %s
            ORDER BY recorded_time DESC
            LIMIT 1
            """,
            (admission_id,)
        )
        vital = cursor.fetchone()
        cursor.close()
        conn.close()
        return vital
    except Error as e:
        print(f"❌ Error fetching latest vitals: {e}")
        return None


def get_vitals_summary(admission_id):
    """
    Calculates aggregate statistics (average, minimum, maximum) for all vital
    records belonging to an admission.
    Args: admission_id (int): ID of the admission
    Returns: Tuple (count, avg_bp_sys, avg_bp_dia, avg_hr, avg_sugar,
                    min_bp_sys, min_bp_dia, min_hr, min_sugar,
                    max_bp_sys, max_bp_dia, max_hr, max_sugar)
             or None if no records exist.
    """
    try:
        conn = create_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*)                           AS record_count,
                AVG(blood_pressure_sys)            AS avg_bp_sys,
                AVG(blood_pressure_dia)            AS avg_bp_dia,
                AVG(heart_beat)                    AS avg_hr,
                AVG(sugar_level)                   AS avg_sugar,
                MIN(blood_pressure_sys)            AS min_bp_sys,
                MIN(blood_pressure_dia)            AS min_bp_dia,
                MIN(heart_beat)                    AS min_hr,
                MIN(sugar_level)                   AS min_sugar,
                MAX(blood_pressure_sys)            AS max_bp_sys,
                MAX(blood_pressure_dia)            AS max_bp_dia,
                MAX(heart_beat)                    AS max_hr,
                MAX(sugar_level)                   AS max_sugar
            FROM Diagnoses_and_Vitals
            WHERE admission_id = %s
            """,
            (admission_id,)
        )
        summary = cursor.fetchone()
        cursor.close()
        conn.close()
        return summary if summary and summary[0] else None
    except Error as e:
        print(f"❌ Error fetching vitals summary: {e}")
        return None


def calculate_bed_charges(patient_id):
    """
    Calculates bed charges for all admissions of a patient.
    Formula: total_admission_days * 5000 PKR.
    """
    BED_DAILY_RATE = 5000.0
    try:
        conn = create_connection()
        if conn is None:
            return 0.0
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COALESCE(
                SUM(
                    GREATEST(
                        DATEDIFF(COALESCE(discharge_date, CURDATE()), admission_date),
                        1
                    )
                ),
                0
            )
            FROM Admissions
            WHERE patient_id = %s
            """,
            (patient_id,),
        )
        total_days = cursor.fetchone()[0] or 0
        cursor.close()
        conn.close()
        return float(total_days) * BED_DAILY_RATE
    except Error as e:
        print(f"❌ Error calculating bed charges: {e}")
        return 0.0


def calculate_medicine_charges(patient_id):
    """Calculates medicine charges from all patient prescriptions."""
    try:
        conn = create_connection()
        if conn is None:
            return 0.0
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COALESCE(SUM(pi.price_per_unit), 0)
            FROM Prescriptions p
            JOIN Pharmacy_Inventory pi ON p.inventory_id = pi.inventory_id
            WHERE p.patient_id = %s
            """,
            (patient_id,),
        )
        amount = cursor.fetchone()[0] or 0
        cursor.close()
        conn.close()
        return float(amount)
    except Error as e:
        print(f"❌ Error calculating medicine charges: {e}")
        return 0.0


def calculate_test_charges(patient_id):
    """Calculates diagnostic/vitals charges for a patient."""
    TEST_RECORD_RATE = 500.0
    try:
        conn = create_connection()
        if conn is None:
            return 0.0
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM Diagnoses_and_Vitals dv
            JOIN Admissions a ON dv.admission_id = a.admission_id
            WHERE a.patient_id = %s
            """,
            (patient_id,),
        )
        records_count = cursor.fetchone()[0] or 0
        cursor.close()
        conn.close()
        return float(records_count) * TEST_RECORD_RATE
    except Error as e:
        print(f"❌ Error calculating test charges: {e}")
        return 0.0


def generate_bill(patient_id, payment_status="Pending"):
    """
    Generates a bill by calculating bed, medicine, and test charges.
    Returns: (success: bool, message: str)
    """
    try:
        conn = create_connection()
        if conn is None:
            return False, "❌ Database connection failed."
        cursor = conn.cursor()

        cursor.execute(
            "SELECT CONCAT(first_name, ' ', last_name) FROM Patients WHERE patient_id = %s",
            (patient_id,),
        )
        patient_row = cursor.fetchone()
        if not patient_row:
            cursor.close()
            conn.close()
            return False, f"❌ Patient ID {patient_id} not found."

        cursor.execute(
            """
            SELECT admission_id
            FROM Admissions
            WHERE patient_id = %s
            ORDER BY admission_date DESC, admission_id DESC
            LIMIT 1
            """,
            (patient_id,),
        )
        admission_row = cursor.fetchone()
        if not admission_row:
            cursor.close()
            conn.close()
            return False, f"❌ No admission found for Patient ID {patient_id}. Cannot generate discharge bill."

        bed_charges = calculate_bed_charges(patient_id)
        medicine_charges = calculate_medicine_charges(patient_id)
        test_charges = calculate_test_charges(patient_id)
        total_amount = round(bed_charges + medicine_charges + test_charges, 2)

        cursor.execute(
            """
            INSERT INTO Billing (patient_id, admission_id, total_amount, payment_status)
            VALUES (%s, %s, %s, %s)
            """,
            (patient_id, admission_row[0], total_amount, payment_status),
        )
        conn.commit()
        bill_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return (
            True,
            f"✅ Bill #{bill_id} generated for {patient_row[0]} | Total: PKR {total_amount:.2f}",
        )
    except Error as e:
        print(f"❌ Error generating bill: {e}")
        return False, f"❌ Error: {e}"


def get_patient_bill(patient_id):
    """Fetches latest bill and itemized charges for a patient."""
    try:
        conn = create_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                b.bill_id,
                b.patient_id,
                b.admission_id,
                CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
                b.total_amount,
                b.payment_status
            FROM Billing b
            JOIN Patients p ON b.patient_id = p.patient_id
            WHERE b.patient_id = %s
            ORDER BY b.bill_id DESC
            LIMIT 1
            """,
            (patient_id,),
        )
        bill = cursor.fetchone()
        cursor.close()
        conn.close()

        if not bill:
            return None

        bed_charges = round(calculate_bed_charges(patient_id), 2)
        medicine_charges = round(calculate_medicine_charges(patient_id), 2)
        test_charges = round(calculate_test_charges(patient_id), 2)
        return {
            "bill": bill,
            "bed_charges": bed_charges,
            "medicine_charges": medicine_charges,
            "test_charges": test_charges,
            "total_charges": round(bed_charges + medicine_charges + test_charges, 2),
        }
    except Error as e:
        print(f"❌ Error fetching patient bill: {e}")
        return None


def get_all_bills():
    """Fetches all bills in the system."""
    try:
        conn = create_connection()
        if conn is None:
            return []
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                b.bill_id,
                b.patient_id,
                b.admission_id,
                CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
                b.total_amount,
                b.payment_status
            FROM Billing b
            JOIN Patients p ON b.patient_id = p.patient_id
            ORDER BY b.bill_id DESC
            """
        )
        bills = cursor.fetchall()
        cursor.close()
        conn.close()
        return bills if bills else []
    except Error as e:
        print(f"❌ Error fetching all bills: {e}")
        return []


def get_patient_statistics():
    """Returns aggregate statistics for patient records."""
    try:
        conn = create_connection()
        if conn is None:
            return {
                "total_patients": 0,
                "male_patients": 0,
                "female_patients": 0,
                "registered_last_30_days": 0,
            }

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_patients,
                SUM(CASE WHEN LOWER(gender) = 'male' THEN 1 ELSE 0 END) AS male_patients,
                SUM(CASE WHEN LOWER(gender) = 'female' THEN 1 ELSE 0 END) AS female_patients
            FROM Patients
            """
        )
        totals_row = cursor.fetchone() or (0, 0, 0)

        cursor.close()
        conn.close()
        stats = {
            "total_patients": totals_row[0] or 0,
            "male_patients": totals_row[1] or 0,
            "female_patients": totals_row[2] or 0,
            "registered_last_30_days": None,
        }
        if stats["registered_last_30_days"] is None:
            stats["message"] = "Registration-date tracking is not available in current schema."
        return stats
    except Error as e:
        print(f"❌ Error fetching patient statistics: {e}")
        return {
            "total_patients": 0,
            "male_patients": 0,
            "female_patients": 0,
            "registered_last_30_days": 0,
        }


def get_admission_statistics():
    """Returns aggregate statistics for admissions."""
    try:
        conn = create_connection()
        if conn is None:
            return {
                "total_admissions": 0,
                "active_admissions": 0,
                "discharged_admissions": 0,
                "most_used_ward": "N/A",
                "most_used_ward_count": 0,
            }

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_admissions,
                SUM(CASE WHEN discharge_date IS NULL THEN 1 ELSE 0 END) AS active_admissions,
                SUM(CASE WHEN discharge_date IS NOT NULL THEN 1 ELSE 0 END) AS discharged_admissions
            FROM Admissions
            """
        )
        row = cursor.fetchone() or (0, 0, 0)

        cursor.execute(
            """
            SELECT
                w.ward_name,
                COUNT(*) AS admission_count
            FROM Admissions a
            JOIN Beds b ON a.bed_id = b.bed_id
            JOIN Wards w ON b.ward_id = w.ward_id
            GROUP BY w.ward_name
            ORDER BY admission_count DESC, w.ward_name ASC
            LIMIT 1
            """
        )
        top_ward = cursor.fetchone()

        cursor.close()
        conn.close()

        return {
            "total_admissions": row[0] or 0,
            "active_admissions": row[1] or 0,
            "discharged_admissions": row[2] or 0,
            "most_used_ward": top_ward[0] if top_ward else "N/A",
            "most_used_ward_count": top_ward[1] if top_ward else 0,
        }
    except Error as e:
        print(f"❌ Error fetching admission statistics: {e}")
        return {
            "total_admissions": 0,
            "active_admissions": 0,
            "discharged_admissions": 0,
            "most_used_ward": "N/A",
            "most_used_ward_count": 0,
        }


def get_vitals_statistics():
    """Returns aggregate vitals analytics across all records."""
    try:
        conn = create_connection()
        if conn is None:
            return {
                "total_vitals_records": 0,
                "avg_bp_sys": 0.0,
                "avg_bp_dia": 0.0,
                "avg_heart_rate": 0.0,
                "avg_sugar": 0.0,
            }

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_vitals_records,
                AVG(blood_pressure_sys) AS avg_bp_sys,
                AVG(blood_pressure_dia) AS avg_bp_dia,
                AVG(heart_beat) AS avg_heart_rate,
                AVG(sugar_level) AS avg_sugar
            FROM Diagnoses_and_Vitals
            """
        )
        row = cursor.fetchone() or (0, 0, 0, 0, 0)
        cursor.close()
        conn.close()
        return {
            "total_vitals_records": row[0] or 0,
            "avg_bp_sys": float(row[1] or 0.0),
            "avg_bp_dia": float(row[2] or 0.0),
            "avg_heart_rate": float(row[3] or 0.0),
            "avg_sugar": float(row[4] or 0.0),
        }
    except Error as e:
        print(f"❌ Error fetching vitals statistics: {e}")
        return {
            "total_vitals_records": 0,
            "avg_bp_sys": 0.0,
            "avg_bp_dia": 0.0,
            "avg_heart_rate": 0.0,
            "avg_sugar": 0.0,
        }


def get_billing_statistics():
    """Returns aggregate statistics for billing and revenue."""
    try:
        conn = create_connection()
        if conn is None:
            return {
                "total_bills": 0,
                "total_revenue": 0.0,
                "pending_bills": 0,
                "paid_bills": 0,
            }
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_bills,
                SUM(total_amount) AS total_revenue,
                SUM(CASE WHEN LOWER(payment_status) = %s THEN 1 ELSE 0 END) AS pending_bills,
                SUM(CASE WHEN LOWER(payment_status) = %s THEN 1 ELSE 0 END) AS paid_bills
            FROM Billing
            """,
            ("pending", "paid"),
        )
        row = cursor.fetchone() or (0, 0, 0, 0)
        cursor.close()
        conn.close()
        return {
            "total_bills": row[0] or 0,
            "total_revenue": float(row[1] or 0.0),
            "pending_bills": row[2] or 0,
            "paid_bills": row[3] or 0,
        }
    except Error as e:
        error_text = str(e).lower()
        if "doesn't exist" in error_text and "billing" in error_text:
            print("ℹ️ Billing table is unavailable. Returning zeroed billing statistics.")
            return {
                "total_bills": 0,
                "total_revenue": 0.0,
                "pending_bills": 0,
                "paid_bills": 0,
                "message": "Billing table is missing; billing analytics are currently unavailable.",
            }
        print(f"❌ Error fetching billing statistics: {e}")
        return {
            "total_bills": 0,
            "total_revenue": 0.0,
            "pending_bills": 0,
            "paid_bills": 0,
        }


def get_patient_dependency_counts(patient_id):
    """Returns dependency counts for a patient (admissions, vitals, prescriptions, appointments)."""
    try:
        conn = create_connection()
        if conn is None:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Admissions WHERE patient_id = %s", (patient_id,))
        admissions_count = cursor.fetchone()[0]
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM Diagnoses_and_Vitals dv
            JOIN Admissions a ON dv.admission_id = a.admission_id
            WHERE a.patient_id = %s
            """,
            (patient_id,),
        )
        vitals_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Prescriptions WHERE patient_id = %s", (patient_id,))
        prescriptions_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Appointments WHERE patient_id = %s", (patient_id,))
        appointments_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Billing WHERE patient_id = %s", (patient_id,))
        bills_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {
            "admissions": admissions_count,
            "vitals": vitals_count,
            "prescriptions": prescriptions_count,
            "appointments": appointments_count,
            "bills": bills_count,
        }
    except Error as e:
        print(f"❌ Error checking patient dependencies: {e}")
        return None


def delete_patient(patient_id, confirm_cascade=False, dependency_counts=None):
    """
    Deletes a patient. If dependent records exist, confirm_cascade must be True to proceed.
    Cascades deletion of vitals, appointments, prescriptions, billing, and admissions before deleting the patient.
    Returns: (success: bool, message: str, dependency_counts: dict|None)
    """
    try:
        conn = create_connection()
        if conn is None:
            return False, "❌ Database connection failed.", None
        cursor = conn.cursor()

        cursor.execute("SELECT patient_id FROM Patients WHERE patient_id = %s", (patient_id,))
        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            return False, f"❌ Patient ID {patient_id} not found.", None

        if dependency_counts is None:
            cursor.execute("SELECT COUNT(*) FROM Admissions WHERE patient_id = %s", (patient_id,))
            admissions_count = cursor.fetchone()[0]
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM Diagnoses_and_Vitals dv
                JOIN Admissions a ON dv.admission_id = a.admission_id
                WHERE a.patient_id = %s
                """,
                (patient_id,),
            )
            vitals_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Prescriptions WHERE patient_id = %s", (patient_id,))
            prescriptions_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Appointments WHERE patient_id = %s", (patient_id,))
            appointments_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Billing WHERE patient_id = %s", (patient_id,))
            bills_count = cursor.fetchone()[0]

            dependency_counts = {
                "admissions": admissions_count,
                "vitals": vitals_count,
                "prescriptions": prescriptions_count,
                "appointments": appointments_count,
                "bills": bills_count,
            }

        if any(dependency_counts.values()) and not confirm_cascade:
            cursor.close()
            conn.close()
            return (
                False,
                "⚠️ Patient has related records. Confirmation required for cascade delete.",
                dependency_counts,
            )

        if not conn.in_transaction:
            conn.start_transaction()

        cursor.execute(
            """
            DELETE dv
            FROM Diagnoses_and_Vitals dv
            JOIN Admissions a ON dv.admission_id = a.admission_id
            WHERE a.patient_id = %s
            """,
            (patient_id,),
        )
        cursor.execute("DELETE FROM Appointments WHERE patient_id = %s", (patient_id,))
        cursor.execute("DELETE FROM Prescriptions WHERE patient_id = %s", (patient_id,))
        cursor.execute("DELETE FROM Billing WHERE patient_id = %s", (patient_id,))
        cursor.execute("DELETE FROM Admissions WHERE patient_id = %s", (patient_id,))
        cursor.execute("DELETE FROM Patients WHERE patient_id = %s", (patient_id,))

        conn.commit()
        cursor.close()
        conn.close()
        return True, f"✅ Patient ID {patient_id} and related records deleted.", dependency_counts

    except Error as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print(f"❌ Error deleting patient: {e}")
        return False, f"❌ Error: {e}", None


def get_complete_patient_profile_data(patient_id):
    """Fetches complete profile data for a patient across core HMS modules."""
    try:
        conn = create_connection()
        if conn is None:
            return None
        cursor = conn.cursor()

        blood_type = "N/A"
        medical_history = "N/A"
        try:
            cursor.execute(
                """
                SELECT
                    patient_id, first_name, last_name, dob, gender, phone, address, emergency_contact,
                    blood_type, medical_history
                FROM Patients
                WHERE patient_id = %s
                """,
                (patient_id,),
            )
            patient_row = cursor.fetchone()
            if not patient_row:
                cursor.close()
                conn.close()
                return None
            patient = patient_row[:8]
            blood_type = patient_row[8] if patient_row[8] else "N/A"
            medical_history = patient_row[9] if patient_row[9] else "N/A"
        except Error:
            cursor.execute(
                """
                SELECT patient_id, first_name, last_name, dob, gender, phone, address, emergency_contact
                FROM Patients
                WHERE patient_id = %s
                """,
                (patient_id,),
            )
            patient = cursor.fetchone()
            if not patient:
                cursor.close()
                conn.close()
                return None

        active_admissions = []
        try:
            cursor.execute(
                """
                SELECT
                    a.admission_id,
                    a.admission_date,
                    a.discharge_date,
                    a.bed_id,
                    w.ward_name,
                    w.ward_type
                FROM Admissions a
                LEFT JOIN Beds b ON a.bed_id = b.bed_id
                LEFT JOIN Wards w ON b.ward_id = w.ward_id
                WHERE a.patient_id = %s AND a.discharge_date IS NULL
                ORDER BY a.admission_date DESC
                """,
                (patient_id,),
            )
            active_admissions = cursor.fetchall()
        except Error:
            active_admissions = []

        admission_history = []
        try:
            cursor.execute(
                """
                SELECT
                    a.admission_id,
                    a.admission_date,
                    a.discharge_date,
                    a.bed_id,
                    w.ward_name,
                    w.ward_type
                FROM Admissions a
                LEFT JOIN Beds b ON a.bed_id = b.bed_id
                LEFT JOIN Wards w ON b.ward_id = w.ward_id
                WHERE a.patient_id = %s
                ORDER BY a.admission_date DESC
                """,
                (patient_id,),
            )
            admission_history = cursor.fetchall()
        except Error:
            admission_history = []

        vitals_history = []
        try:
            cursor.execute(
                """
                SELECT
                    dv.vital_id,
                    dv.admission_id,
                    dv.blood_pressure_sys,
                    dv.blood_pressure_dia,
                    dv.heart_beat,
                    dv.sugar_level,
                    dv.recorded_time
                FROM Diagnoses_and_Vitals dv
                JOIN Admissions a ON dv.admission_id = a.admission_id
                WHERE a.patient_id = %s
                ORDER BY dv.recorded_time DESC
                """,
                (patient_id,),
            )
            vitals_history = cursor.fetchall()
        except Error:
            vitals_history = []
        latest_vitals = vitals_history[0] if vitals_history else None

        prescriptions = []
        try:
            cursor.execute(
                """
                SELECT
                    p.prescription_id,
                    pi.item_name,
                    CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
                    p.dosage,
                    p.duration,
                    p.prescribed_date
                FROM Prescriptions p
                LEFT JOIN Pharmacy_Inventory pi ON p.inventory_id = pi.inventory_id
                LEFT JOIN Doctors d ON p.doctor_id = d.doctor_id
                WHERE p.patient_id = %s
                ORDER BY p.prescribed_date DESC
                """,
                (patient_id,),
            )
            prescriptions = cursor.fetchall()
        except Error:
            prescriptions = []

        bills = []
        try:
            cursor.execute(
                """
                SELECT bill_id, admission_id, total_amount, payment_status
                FROM Billing
                WHERE patient_id = %s
                ORDER BY bill_id DESC
                """,
                (patient_id,),
            )
            bills = cursor.fetchall()
        except Error:
            bills = []

        cursor.close()
        conn.close()

        return {
            "patient": patient,
            "blood_type": blood_type,
            "medical_history": medical_history,
            "active_admissions": active_admissions,
            "admission_history": admission_history,
            "latest_vitals": latest_vitals,
            "vitals_history": vitals_history,
            "prescriptions": prescriptions,
            "bills": bills,
        }
    except Error as e:
        print(f"❌ Error fetching complete patient profile: {e}")
        return None
