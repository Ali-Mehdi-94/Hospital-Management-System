import customtkinter as ctk
from tkinter import messagebox
import database_manager as db

# --- 1. SET UP THE MAIN WINDOW ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("700x700")
app.title("Hospital Management System")
app.withdraw()

session = {"is_authenticated": False, "username": "Guest"}
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
btn_delete_patient = None
btn_complete_profile = None
login_status_label = None
btn_logout = None

# ========== PATIENT LIST VIEW CLASS ==========

class PatientListView:
    """
    Manages the Patient List View UI component with search, sort, and detail viewing.
    """
    
    def __init__(self, parent_text_box, database_manager):
        """
        Initialize the Patient List View.
        Args:
            parent_text_box: CTkTextbox to display results
            database_manager: Reference to database_manager module
        """
        self.text_box = parent_text_box
        self.db = database_manager
        self.current_patients = []
        self.selected_patient_id = None
    
    def format_date(self, date_obj):
        """Format date object to DD-MM-YYYY string."""
        if date_obj is None:
            return "N/A"
        try:
            if isinstance(date_obj, str):
                return date_obj
            return date_obj.strftime("%d-%m-%Y")
        except:
            return str(date_obj)
    
    def display_all_patients(self):
        """Fetch and display all registered patients in the text box."""
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        
        patients = self.db.get_all_patients()
        
        if not patients:
            self.text_box.insert("end", "❌ No patients found in the database.\n")
            self.text_box.configure(state="disabled")
            return
        
        self.current_patients = patients
        
        # Header
        header = "╔" + "═" * 120 + "╗\n"
        header += "║ " + "PATIENT LIST VIEW".center(118) + " ║\n"
        header += "╠" + "═" * 120 + "╣\n"
        self.text_box.insert("end", header)
        
        # Column headers
        col_header = (
            "║ ID    │ First Name      │ Last Name       │ DOB        │ Gender │ Phone Number   │ Address                 ║\n"
        )
        self.text_box.insert("end", col_header)
        self.text_box.insert("end", "╠" + "═" * 120 + "╣\n")
        
        # Patient rows
        for idx, patient in enumerate(patients, 1):
            patient_id = patient[0]
            first_name = str(patient[1])[:15].ljust(15)
            last_name = str(patient[2])[:15].ljust(15)
            dob = self.format_date(patient[3])[:10].ljust(10)
            gender = str(patient[4])[:6].ljust(6)
            phone = str(patient[5])[:14].ljust(14)
            address = str(patient[6])[:23].ljust(23)
            
            row = (
                f"║ {str(patient_id):5} │ {first_name} │ {last_name} │ {dob} │ {gender} │ {phone} │ {address} ║\n"
            )
            self.text_box.insert("end", row)
        
        # Footer
        footer = "╚" + "═" * 120 + "╝\n"
        self.text_box.insert("end", footer)
        self.text_box.insert("end", f"\n📊 Total Patients: {len(patients)}\n")
        self.text_box.insert("end", "💡 Tip: Use 'Search Patient' button to find specific patients.\n")
        
        self.text_box.configure(state="disabled")
    
    def display_patient_details(self, patient_id):
        """Display comprehensive details for a specific patient."""
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        
        patient = self.db.get_patient_details(patient_id)
        
        if not patient:
            self.text_box.insert("end", f"❌ Patient with ID {patient_id} not found.\n")
            self.text_box.configure(state="disabled")
            return
        
        # Patient Details Header
        header = "╔" + "═" * 100 + "╗\n"
        header += "║ " + f"PATIENT DETAILS - ID: {patient[0]}".center(98) + " ║\n"
        header += "╠" + "═" * 100 + "╣\n"
        self.text_box.insert("end", header)
        
        # Personal Information
        self.text_box.insert("end", "║ PERSONAL INFORMATION\n")
        self.text_box.insert("end", "╟─ " + "─" * 96 + " ─╢\n")
        self.text_box.insert("end", f"║ Full Name:         {patient[1]} {patient[2]}\n")
        self.text_box.insert("end", f"║ Date of Birth:     {self.format_date(patient[3])}\n")
        self.text_box.insert("end", f"║ Gender:            {patient[4]}\n")
        self.text_box.insert("end", f"║ Contact Number:    {patient[5]}\n")
        self.text_box.insert("end", f"║ Address:           {patient[6]}\n")
        self.text_box.insert("end", f"║ Emergency Contact: {patient[7]}\n")
        self.text_box.insert("end", "╟─ " + "─" * 96 + " ─╢\n")
        
        # Admission History
        admissions = self.db.get_patient_admission_history(patient_id)
        self.text_box.insert("end", "║ ADMISSION HISTORY\n")
        
        if admissions:
            self.text_box.insert("end", "╟─ " + "─" * 96 + " ─╢\n")
            for admission in admissions:
                admission_id, admission_date, discharge_date, ward_name, bed_id, ward_type = admission
                status = "🔴 ACTIVE" if discharge_date is None else "🟢 DISCHARGED"
                self.text_box.insert(
                    "end",
                    f"║ • Admission {admission_id}: {self.format_date(admission_date)} → {self.format_date(discharge_date)} | {ward_name} ({ward_type}) | Bed {bed_id} | {status}\n"
                )
        else:
            self.text_box.insert("end", "╟─ " + "─" * 96 + " ─╢\n")
            self.text_box.insert("end", "║ ℹ️ No admission records found.\n")
        
        self.text_box.insert("end", "╚" + "═" * 100 + "╝\n")
        self.text_box.insert("end", "\n✅ Use 'Back to Patient List' button to return to the full list.\n")
        
        self.text_box.configure(state="disabled")
    
    def search_patients_ui(self, search_term):
        """Display search results for a patient."""
        if not search_term.strip():
            self.text_box.configure(state="normal")
            self.text_box.delete("1.0", "end")
            self.text_box.insert("end", "⚠️ Please enter a name or phone number to search.\n")
            self.text_box.configure(state="disabled")
            return
        
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        
        results = self.db.search_patients(search_term)
        
        if not results:
            self.text_box.insert("end", f"❌ No patients found matching '{search_term}'.\n")
            self.text_box.configure(state="disabled")
            return
        
        self.current_patients = results
        
        # Header
        header = "╔" + "═" * 120 + "╗\n"
        header += "║ " + f"SEARCH RESULTS: '{search_term}'".center(118) + " ║\n"
        header += "╠" + "═" * 120 + "╣\n"
        self.text_box.insert("end", header)
        
        # Column headers
        col_header = (
            "║ ID    │ First Name      │ Last Name       │ DOB        │ Gender │ Phone Number   │ Address                 ║\n"
        )
        self.text_box.insert("end", col_header)
        self.text_box.insert("end", "╠" + "═" * 120 + "╣\n")
        
        # Result rows
        for patient in results:
            patient_id = patient[0]
            first_name = str(patient[1])[:15].ljust(15)
            last_name = str(patient[2])[:15].ljust(15)
            dob = self.format_date(patient[3])[:10].ljust(10)
            gender = str(patient[4])[:6].ljust(6)
            phone = str(patient[5])[:14].ljust(14)
            address = str(patient[6])[:23].ljust(23)
            
            row = (
                f"║ {str(patient_id):5} │ {first_name} │ {last_name} │ {dob} │ {gender} │ {phone} │ {address} ║\n"
            )
            self.text_box.insert("end", row)
        
        # Footer
        footer = "╚" + "═" * 120 + "╝\n"
        self.text_box.insert("end", footer)
        self.text_box.insert("end", f"\n🔍 Found {len(results)} patient(s).\n")
        
        self.text_box.configure(state="disabled")

# ========== ROOM ALLOCATION VIEW CLASS ==========

class RoomAllocationView:
    """
    Manages the Room Allocation & Bed Management UI component.
    Handles ward summary, bed listing, admissions, and discharge operations.
    """

    def __init__(self, parent_text_box, database_manager):
        """
        Initialize the Room Allocation View.
        Args:
            parent_text_box: CTkTextbox to display results
            database_manager: Reference to database_manager module
        """
        self.text_box = parent_text_box
        self.db = database_manager

    def format_date(self, date_obj):
        """Format date/datetime object to DD-MM-YYYY string."""
        if date_obj is None:
            return "N/A"
        try:
            if isinstance(date_obj, str):
                return date_obj
            return date_obj.strftime("%d-%m-%Y")
        except Exception:
            return str(date_obj)

    def show_ward_summary(self):
        """Display ward bed availability summary in the main text box."""
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")

        summary = self.db.get_ward_bed_summary()

        if not summary:
            self.text_box.insert("end", "❌ No ward data found in the database.\n")
            self.text_box.configure(state="disabled")
            return

        header = "╔" + "═" * 90 + "╗\n"
        header += "║ " + "WARD BED AVAILABILITY SUMMARY".center(88) + " ║\n"
        header += "╠" + "═" * 90 + "╣\n"
        self.text_box.insert("end", header)

        col_header = (
            "║ Ward ID │ Ward Name              │ Ward Type       │ Total │ Available │ Occupied ║\n"
        )
        self.text_box.insert("end", col_header)
        self.text_box.insert("end", "╠" + "═" * 90 + "╣\n")

        total_beds = total_available = total_occupied = 0
        for row in summary:
            ward_id, ward_name, ward_type, t_beds, avail, occup = row
            t_beds = t_beds or 0
            avail = avail or 0
            occup = occup or 0
            total_beds += t_beds
            total_available += avail
            total_occupied += occup

            ward_name_fmt = str(ward_name)[:22].ljust(22)
            ward_type_fmt = str(ward_type)[:15].ljust(15)
            self.text_box.insert(
                "end",
                f"║ {str(ward_id):7} │ {ward_name_fmt} │ {ward_type_fmt} │ {str(t_beds):5} │ {str(avail):9} │ {str(occup):8} ║\n"
            )

        self.text_box.insert("end", "╠" + "═" * 90 + "╣\n")
        self.text_box.insert(
            "end",
            f"║ {'TOTALS':7}   {'':24}  {'':17} │ {str(total_beds):5} │ {str(total_available):9} │ {str(total_occupied):8} ║\n"
        )
        self.text_box.insert("end", "╚" + "═" * 90 + "╝\n")
        self.text_box.insert("end", f"\n🏥 Total Wards: {len(summary)}  |  Total Beds: {total_beds}  |  Available: {total_available}  |  Occupied: {total_occupied}\n")
        self.text_box.insert("end", "💡 Tip: Use 'View Ward Beds' to see individual beds in a ward.\n")

        self.text_box.configure(state="disabled")

    def show_ward_beds(self, ward_id, ward_name):
        """Display all beds in a specific ward in the main text box."""
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")

        beds = self.db.get_all_beds_in_ward(ward_id)

        header = "╔" + "═" * 60 + "╗\n"
        header += "║ " + f"BEDS IN WARD: {ward_name}".center(58) + " ║\n"
        header += "╠" + "═" * 60 + "╣\n"
        self.text_box.insert("end", header)

        if not beds:
            self.text_box.insert("end", "║ " + "No beds found in this ward.".center(58) + " ║\n")
            self.text_box.insert("end", "╚" + "═" * 60 + "╝\n")
            self.text_box.configure(state="disabled")
            return

        col_header = "║ Bed ID │ Ward ID │ Status                               ║\n"
        self.text_box.insert("end", col_header)
        self.text_box.insert("end", "╠" + "═" * 60 + "╣\n")

        for bed in beds:
            bed_id, w_id, status = bed
            status_icon = "🟢 Available" if status == "Available" else "🔴 Occupied "
            self.text_box.insert(
                "end",
                f"║ {str(bed_id):6} │ {str(w_id):7} │ {status_icon:<38} ║\n"
            )

        self.text_box.insert("end", "╚" + "═" * 60 + "╝\n")
        available = sum(1 for b in beds if b[2] == "Available")
        occupied = len(beds) - available
        self.text_box.insert("end", f"\n📊 Total: {len(beds)}  |  Available: {available}  |  Occupied: {occupied}\n")

        self.text_box.configure(state="disabled")

    def show_active_admissions(self):
        """Display all currently active admissions in the main text box."""
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")

        admissions = self.db.get_all_active_admissions()

        header = "╔" + "═" * 110 + "╗\n"
        header += "║ " + "ACTIVE ADMISSIONS".center(108) + " ║\n"
        header += "╠" + "═" * 110 + "╣\n"
        self.text_box.insert("end", header)

        if not admissions:
            self.text_box.insert("end", "║ " + "No active admissions found.".center(108) + " ║\n")
            self.text_box.insert("end", "╚" + "═" * 110 + "╝\n")
            self.text_box.configure(state="disabled")
            return

        col_header = (
            "║ Adm.ID │ Pat.ID │ Patient Name           │ Bed ID │ Ward Name              │ Ward Type       │ Adm. Date  ║\n"
        )
        self.text_box.insert("end", col_header)
        self.text_box.insert("end", "╠" + "═" * 110 + "╣\n")

        for adm in admissions:
            adm_id, pat_id, full_name, bed_id, ward_name, ward_type, adm_date = adm
            full_name_fmt = str(full_name)[:22].ljust(22)
            ward_name_fmt = str(ward_name or "N/A")[:22].ljust(22)
            ward_type_fmt = str(ward_type or "N/A")[:15].ljust(15)
            adm_date_fmt = self.format_date(adm_date)

            self.text_box.insert(
                "end",
                f"║ {str(adm_id):6} │ {str(pat_id):6} │ {full_name_fmt} │ {str(bed_id):6} │ {ward_name_fmt} │ {ward_type_fmt} │ {adm_date_fmt} ║\n"
            )

        self.text_box.insert("end", "╚" + "═" * 110 + "╝\n")
        self.text_box.insert("end", f"\n🛏️  Total Active Admissions: {len(admissions)}\n")
        self.text_box.insert("end", "💡 Tip: Use 'Discharge Patient' to close an active admission.\n")

        self.text_box.configure(state="disabled")


# ========== DIAGNOSTIC TESTS & VITALS VIEW CLASS ==========

class DiagnosticVitalsView:
    """
    Manages the Diagnostic Tests & Vitals Management UI component.
    Handles vital sign recording, history display, statistics, and date-range search.
    """

    # Normal / warning thresholds used for status indicators
    _WARN = {
        'bp_systolic':  (90,  160),   # below 90 or above 160 → warning/critical
        'bp_diastolic': (60,  100),
        'heart_rate':   (60,  100),
        'sugar_level':  (70,  180),
    }

    def __init__(self, parent_text_box, database_manager):
        self.text_box = parent_text_box
        self.db = database_manager

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fmt_datetime(self, dt_obj):
        """Format a datetime or date object as DD-MM-YYYY HH:MM:SS."""
        if dt_obj is None:
            return "N/A"
        try:
            if hasattr(dt_obj, 'strftime'):
                if hasattr(dt_obj, 'hour'):
                    return dt_obj.strftime("%d-%m-%Y %H:%M:%S")
                return dt_obj.strftime("%d-%m-%Y")
            return str(dt_obj)
        except Exception:
            return str(dt_obj)

    def _status_icon(self, vital_key, value):
        """Return 🟢 Normal, 🟡 Warning, or 🔴 Critical based on thresholds."""
        if value is None:
            return "⚪ N/A   "
        lo, hi = self._WARN[vital_key]
        if lo <= float(value) <= hi:
            return "🟢 Normal "
        ranges = self.db.get_vital_ranges()
        r = ranges[vital_key]
        if r['min'] <= float(value) <= r['max']:
            return "🟡 Warning"
        return "🔴 Critical"

    def _write(self, text):
        self.text_box.insert("end", text)

    # ------------------------------------------------------------------
    # Public display methods
    # ------------------------------------------------------------------

    def show_vitals_history(self, admission_id):
        """Display all vital records for the given admission in an ASCII table."""
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")

        vitals = self.db.get_patient_vitals(admission_id)

        self._write("╔" + "═" * 118 + "╗\n")
        self._write("║ " + f"VITAL SIGNS HISTORY  —  Admission ID: {admission_id}".center(116) + " ║\n")
        self._write("╠" + "═" * 118 + "╣\n")

        if not vitals:
            self._write("║ " + "No vital records found for this admission.".center(116) + " ║\n")
            self._write("╚" + "═" * 118 + "╝\n")
            self.text_box.configure(state="disabled")
            return

        self._write(
            "║ VitalID │ BP Sys (mmHg) │ BP Dia (mmHg) │ Heart Rate (bpm) │ Sugar (mg/dL) │ Recorded At              ║\n"
        )
        self._write("╠" + "═" * 118 + "╣\n")

        for row in vitals:
            vital_id, adm_id, bp_sys, bp_dia, hr, sugar, rec_time = row
            ts = self._fmt_datetime(rec_time)
            bp_sys_s  = f"{bp_sys} {self._status_icon('bp_systolic',  bp_sys)}"
            bp_dia_s  = f"{bp_dia} {self._status_icon('bp_diastolic', bp_dia)}"
            hr_s      = f"{hr} {self._status_icon('heart_rate',   hr)}"
            sugar_s   = f"{sugar} {self._status_icon('sugar_level',  sugar)}"
            self._write(
                f"║ {str(vital_id):7} │ {str(bp_sys_s):<13} │ {str(bp_dia_s):<13} │ {str(hr_s):<16} │ {str(sugar_s):<13} │ {ts:<24} ║\n"
            )

        self._write("╚" + "═" * 118 + "╝\n")
        self._write(f"\n📋 Total Records: {len(vitals)}\n")
        self._write("💡 Legend: 🟢 Normal  🟡 Warning  🔴 Critical\n")
        self.text_box.configure(state="disabled")

    def show_vitals_summary(self, admission_id):
        """Display aggregate statistics for vitals of the given admission."""
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")

        summary = self.db.get_vitals_summary(admission_id)

        self._write("╔" + "═" * 80 + "╗\n")
        self._write("║ " + f"VITALS SUMMARY  —  Admission ID: {admission_id}".center(78) + " ║\n")
        self._write("╠" + "═" * 80 + "╣\n")

        if not summary:
            self._write("║ " + "No vital records found for this admission.".center(78) + " ║\n")
            self._write("╚" + "═" * 80 + "╝\n")
            self.text_box.configure(state="disabled")
            return

        count = summary[0]
        avg_bp_sys, avg_bp_dia, avg_hr, avg_sugar = summary[1], summary[2], summary[3], summary[4]
        min_bp_sys, min_bp_dia, min_hr, min_sugar = summary[5], summary[6], summary[7], summary[8]
        max_bp_sys, max_bp_dia, max_hr, max_sugar = summary[9], summary[10], summary[11], summary[12]

        def _r(v):
            return round(float(v), 1) if v is not None else "N/A"

        self._write(f"║  Total Records Analyzed : {count}\n")
        self._write("╟─" + "─" * 78 + "─╢\n")
        self._write(f"║  {'Vital':<28} {'Average':>10}  {'Minimum':>10}  {'Maximum':>10}\n")
        self._write("╟─" + "─" * 78 + "─╢\n")
        rows = [
            ("Blood Pressure Systolic (mmHg)",  _r(avg_bp_sys),  _r(min_bp_sys),  _r(max_bp_sys)),
            ("Blood Pressure Diastolic (mmHg)", _r(avg_bp_dia),  _r(min_bp_dia),  _r(max_bp_dia)),
            ("Heart Rate (bpm)",                _r(avg_hr),      _r(min_hr),      _r(max_hr)),
            ("Sugar Level (mg/dL)",             _r(avg_sugar),   _r(min_sugar),   _r(max_sugar)),
        ]
        for label, avg, mn, mx in rows:
            self._write(f"║  {label:<28} {str(avg):>10}  {str(mn):>10}  {str(mx):>10}\n")

        self._write("╚" + "═" * 80 + "╝\n")
        self.text_box.configure(state="disabled")

    def show_search_results(self, admission_id, start_date, end_date):
        """Display vitals filtered by date range."""
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")

        vitals = self.db.search_vitals_by_date(admission_id, start_date, end_date)

        start_fmt = start_date if start_date else "N/A"
        end_fmt   = end_date   if end_date   else "N/A"

        self._write("╔" + "═" * 118 + "╗\n")
        self._write("║ " + f"VITALS SEARCH  —  Admission: {admission_id}  |  {start_fmt} → {end_fmt}".center(116) + " ║\n")
        self._write("╠" + "═" * 118 + "╣\n")

        if not vitals:
            self._write("║ " + "No records found in the selected date range.".center(116) + " ║\n")
            self._write("╚" + "═" * 118 + "╝\n")
            self.text_box.configure(state="disabled")
            return

        self._write(
            "║ VitalID │ BP Sys (mmHg) │ BP Dia (mmHg) │ Heart Rate (bpm) │ Sugar (mg/dL) │ Recorded At              ║\n"
        )
        self._write("╠" + "═" * 118 + "╣\n")

        for row in vitals:
            vital_id, adm_id, bp_sys, bp_dia, hr, sugar, rec_time = row
            ts = self._fmt_datetime(rec_time)
            bp_sys_s = f"{bp_sys} {self._status_icon('bp_systolic',  bp_sys)}"
            bp_dia_s = f"{bp_dia} {self._status_icon('bp_diastolic', bp_dia)}"
            hr_s     = f"{hr} {self._status_icon('heart_rate',   hr)}"
            sugar_s  = f"{sugar} {self._status_icon('sugar_level',  sugar)}"
            self._write(
                f"║ {str(vital_id):7} │ {str(bp_sys_s):<13} │ {str(bp_dia_s):<13} │ {str(hr_s):<16} │ {str(sugar_s):<13} │ {ts:<24} ║\n"
            )

        self._write("╚" + "═" * 118 + "╝\n")
        self._write(f"\n🔍 Found {len(vitals)} record(s).\n")
        self._write("💡 Legend: 🟢 Normal  🟡 Warning  🔴 Critical\n")
        self.text_box.configure(state="disabled")


class CompletePatientView:
    """Displays full, read-only profile information for a patient."""

    def __init__(self, parent_text_box, database_manager):
        self.text_box = parent_text_box
        self.db = database_manager

    def _fmt_date(self, value):
        if value is None:
            return "N/A"
        try:
            return value.strftime("%d-%m-%Y")
        except Exception:
            return str(value)

    def _fmt_datetime(self, value):
        if value is None:
            return "N/A"
        try:
            return value.strftime("%d-%m-%Y %H:%M")
        except Exception:
            return str(value)

    def show_complete_patient_profile(self, patient_id):
        data = self.db.get_complete_patient_profile_data(patient_id)

        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")

        if not data:
            self.text_box.insert("end", f"❌ Patient with ID {patient_id} not found.\n")
            self.text_box.configure(state="disabled")
            return

        patient = data["patient"]
        full_name = f"{patient[1]} {patient[2]}"
        self.text_box.insert("end", "╔" + "═" * 118 + "╗\n")
        self.text_box.insert("end", f"║ {'COMPLETE PATIENT PROFILE'.center(118)} ║\n")
        self.text_box.insert("end", "╠" + "═" * 118 + "╣\n")
        self.text_box.insert("end", f"║ Patient ID: {patient[0]:<10} Name: {full_name:<40} Username Access: {session['username']:<20} ║\n")
        self.text_box.insert("end", "╚" + "═" * 118 + "╝\n\n")

        self.text_box.insert("end", "📌 PERSONAL INFORMATION\n")
        self.text_box.insert("end", "─" * 120 + "\n")
        self.text_box.insert("end", f"Name: {full_name}\n")
        self.text_box.insert("end", f"DOB: {self._fmt_date(patient[3])}\n")
        self.text_box.insert("end", f"Gender: {patient[4]}\n")
        self.text_box.insert("end", f"Phone: {patient[5]}\n")
        self.text_box.insert("end", f"Address: {patient[6]}\n")
        self.text_box.insert("end", f"Emergency Contact: {patient[7]}\n")
        self.text_box.insert("end", f"Blood Type: {data['blood_type']}\n")
        self.text_box.insert("end", f"Medical History: {data['medical_history']}\n\n")

        self.text_box.insert("end", "🏥 ACTIVE ADMISSIONS\n")
        self.text_box.insert("end", "─" * 120 + "\n")
        if data["active_admissions"]:
            self.text_box.insert("end", "┌────────────┬────────────┬──────────────┬────────────┬──────────────┬────────────┐\n")
            self.text_box.insert("end", "│ AdmissionID │ Admit Date  │ Ward         │ Ward Type  │ Bed          │ Status     │\n")
            self.text_box.insert("end", "├────────────┼────────────┼──────────────┼────────────┼──────────────┼────────────┤\n")
            for admission in data["active_admissions"]:
                adm_id, admit_date, _, bed_id, ward_name, ward_type = admission
                self.text_box.insert(
                    "end",
                    f"│ {str(adm_id):<10} │ {self._fmt_date(admit_date):<10} │ {str(ward_name or 'N/A')[:12]:<12} │ {str(ward_type or 'N/A')[:10]:<10} │ {str(bed_id or 'N/A'):<12} │ {'🟢 Admitted':<10} │\n",
                )
            self.text_box.insert("end", "└────────────┴────────────┴──────────────┴────────────┴──────────────┴────────────┘\n\n")
        else:
            self.text_box.insert("end", "ℹ️ No active admissions.\n\n")

        self.text_box.insert("end", "🕘 ADMISSION HISTORY\n")
        self.text_box.insert("end", "─" * 120 + "\n")
        if data["admission_history"]:
            self.text_box.insert("end", "┌────────────┬────────────┬────────────┬──────────────┬──────────────┬──────────────┐\n")
            self.text_box.insert("end", "│ AdmissionID │ Admit Date  │ Discharge  │ Ward         │ Bed          │ Status       │\n")
            self.text_box.insert("end", "├────────────┼────────────┼────────────┼──────────────┼──────────────┼──────────────┤\n")
            for admission in data["admission_history"]:
                adm_id, admit_date, discharge_date, bed_id, ward_name, _ = admission
                status = "🟢 Admitted" if discharge_date is None else "🔴 Discharged"
                self.text_box.insert(
                    "end",
                    f"│ {str(adm_id):<10} │ {self._fmt_date(admit_date):<10} │ {self._fmt_date(discharge_date):<10} │ {str(ward_name or 'N/A')[:12]:<12} │ {str(bed_id or 'N/A'):<12} │ {status:<12} │\n",
                )
            self.text_box.insert("end", "└────────────┴────────────┴────────────┴──────────────┴──────────────┴──────────────┘\n\n")
        else:
            self.text_box.insert("end", "ℹ️ No admission history.\n\n")

        self.text_box.insert("end", "🩺 VITAL SIGNS\n")
        self.text_box.insert("end", "─" * 120 + "\n")
        latest = data["latest_vitals"]
        if latest:
            self.text_box.insert(
                "end",
                f"Latest → BP: {latest[2]}/{latest[3]} mmHg | HR: {latest[4]} bpm | Sugar: {latest[5]} mg/dL | Recorded: {self._fmt_datetime(latest[6])}\n",
            )
        else:
            self.text_box.insert("end", "Latest → N/A\n")

        if data["vitals_history"]:
            self.text_box.insert("end", "┌─────────┬────────────┬───────────────┬───────────────┬──────────────┬──────────────┐\n")
            self.text_box.insert("end", "│ Vital ID │ Admission  │ BP Sys / Dia  │ Heart Rate    │ Sugar Level  │ Recorded At   │\n")
            self.text_box.insert("end", "├─────────┼────────────┼───────────────┼───────────────┼──────────────┼──────────────┤\n")
            for row in data["vitals_history"][:20]:
                self.text_box.insert(
                    "end",
                    f"│ {str(row[0]):<7} │ {str(row[1]):<10} │ {str(row[2])+'/'+str(row[3]):<13} │ {str(row[4]):<13} │ {str(row[5]):<12} │ {self._fmt_datetime(row[6])[:12]:<12} │\n",
                )
            self.text_box.insert("end", "└─────────┴────────────┴───────────────┴───────────────┴──────────────┴──────────────┘\n\n")
        else:
            self.text_box.insert("end", "ℹ️ No vitals history.\n\n")

        self.text_box.insert("end", "💊 PRESCRIPTIONS\n")
        self.text_box.insert("end", "─" * 120 + "\n")
        if data["prescriptions"]:
            self.text_box.insert("end", "┌──────────────┬──────────────────────┬──────────────────────┬──────────────┬──────────────┬──────────────┐\n")
            self.text_box.insert("end", "│ Presc ID      │ Medicine             │ Doctor               │ Dosage       │ Duration     │ Date         │\n")
            self.text_box.insert("end", "├──────────────┼──────────────────────┼──────────────────────┼──────────────┼──────────────┼──────────────┤\n")
            for row in data["prescriptions"]:
                self.text_box.insert(
                    "end",
                    f"│ {str(row[0]):<12} │ {str(row[1] or 'N/A')[:20]:<20} │ {str(row[2] or 'N/A')[:20]:<20} │ {str(row[3] or 'N/A')[:12]:<12} │ {str(row[4] or 'N/A')[:12]:<12} │ {self._fmt_date(row[5]):<12} │\n",
                )
            self.text_box.insert("end", "└──────────────┴──────────────────────┴──────────────────────┴──────────────┴──────────────┴──────────────┘\n\n")
        else:
            self.text_box.insert("end", "ℹ️ No prescriptions found.\n\n")

        self.text_box.insert("end", "💵 BILLS\n")
        self.text_box.insert("end", "─" * 120 + "\n")
        if data["bills"]:
            self.text_box.insert("end", "┌──────────┬──────────────┬──────────────┬──────────────┬──────────────┐\n")
            self.text_box.insert("end", "│ Bill ID   │ Amount       │ Status       │ Issue Date   │ Due Date     │\n")
            self.text_box.insert("end", "├──────────┼──────────────┼──────────────┼──────────────┼──────────────┤\n")
            for row in data["bills"]:
                self.text_box.insert(
                    "end",
                    f"│ {str(row[0]):<8} │ {str(row[1]):<12} │ {str(row[2] or 'N/A')[:12]:<12} │ {self._fmt_date(row[3]):<12} │ {self._fmt_date(row[4]):<12} │\n",
                )
            self.text_box.insert("end", "└──────────┴──────────────┴──────────────┴──────────────┴──────────────┘\n")
        else:
            self.text_box.insert("end", "ℹ️ No bills found.\n")

        self.text_box.configure(state="disabled")


# --- 2. DEFINE BUTTON ACTIONS ---

def show_doctors():
    textbox.delete("1.0", "end")
    doctor_list = db.get_all_doctors()
    
    if doctor_list:
        for doc in doctor_list:
            formatted_text = f"Dr. {doc[ 0 ]} {doc[ 1 ]} | Specialist: {doc[ 2 ]} | Ward: {doc[ 3 ]}\n"
            textbox.insert("end", formatted_text)
    else:
        textbox.insert("end", "No doctors found or database connection failed.")

def show_patient_list():
    """Handler for 'View All Patients' button."""
    patient_view = PatientListView(textbox, db)
    patient_view.display_all_patients()


def require_admin_access(feature_name):
    """Checks if current session is authenticated admin."""
    if session["is_authenticated"]:
        return True
    messagebox.showwarning("Login Required", f"Please login as admin to access: {feature_name}")
    return False


def show_complete_patient_profile(patient_id):
    """Shows full patient profile in read-only mode."""
    if not require_admin_access("View Complete Patient Profile"):
        return
    complete_view = CompletePatientView(textbox, db)
    complete_view.show_complete_patient_profile(patient_id)


def open_complete_profile_window():
    """Open dialog to collect patient ID for complete profile."""
    if not require_admin_access("View Complete Patient Profile"):
        return

    profile_window = ctk.CTkToplevel(app)
    profile_window.title("View Complete Patient Profile")
    profile_window.geometry("450x220")
    profile_window.transient(app)
    profile_window.grab_set()

    ctk.CTkLabel(profile_window, text="Enter Patient ID:", font=("Arial", 12, "bold")).pack(pady=10)
    patient_id_entry = ctk.CTkEntry(profile_window, placeholder_text="e.g., 1", width=380)
    patient_id_entry.pack(pady=10, padx=30)
    patient_id_entry.focus()
    error_label = ctk.CTkLabel(profile_window, text="", font=("Arial", 10), text_color="#FF6B6B")
    error_label.pack(pady=2)

    def execute_view():
        try:
            patient_id = int(patient_id_entry.get().strip())
        except ValueError:
            error_label.configure(text="❌ Patient ID must be a number.")
            return
        show_complete_patient_profile(patient_id)
        profile_window.destroy()

    ctk.CTkButton(
        profile_window,
        text="View Complete Profile",
        command=execute_view,
        fg_color="#673AB7",
        hover_color="#512DA8",
    ).pack(pady=10)


def open_delete_patient_window():
    """Opens confirmation flow to delete a patient with cascade warning."""
    if not require_admin_access("Delete Patient"):
        return

    delete_window = ctk.CTkToplevel(app)
    delete_window.title("Delete Patient")
    delete_window.geometry("500x260")
    delete_window.transient(app)
    delete_window.grab_set()

    ctk.CTkLabel(delete_window, text="Delete Patient Record", font=("Arial", 14, "bold"), text_color="#F44336").pack(pady=10)
    ctk.CTkLabel(
        delete_window,
        text="⚠️ This will delete all patient records including admissions, vitals, and prescriptions",
        wraplength=440,
        justify="center",
        text_color="#F44336"
    ).pack(pady=5)
    ctk.CTkLabel(delete_window, text="Patient ID:", anchor="w").pack(fill="x", padx=40, pady=(10, 0))
    patient_id_entry = ctk.CTkEntry(delete_window, placeholder_text="e.g., 1", width=400)
    patient_id_entry.pack(padx=40, pady=8)
    patient_id_entry.focus()

    result_label = ctk.CTkLabel(delete_window, text="", font=("Arial", 10))
    result_label.pack(pady=5)

    def execute_delete():
        try:
            patient_id = int(patient_id_entry.get().strip())
        except ValueError:
            result_label.configure(text="❌ Patient ID must be a number.", text_color="#FF6B6B")
            return

        success, message, dependency_counts = db.delete_patient(patient_id, confirm_cascade=False)
        if not success and dependency_counts:
            confirm_message = (
                "This will delete all patient records including admissions, vitals, and prescriptions.\n\n"
                f"Patient ID: {patient_id}\n"
                f"Admissions: {dependency_counts['admissions']}\n"
                f"Vitals: {dependency_counts['vitals']}\n"
                f"Prescriptions: {dependency_counts['prescriptions']}\n\n"
                "Do you want to continue?"
            )
            confirmed = messagebox.askyesno("Confirm Cascade Delete", confirm_message)
            if not confirmed:
                result_label.configure(text="ℹ️ Deletion cancelled.", text_color="#FF9800")
                return
            success, message, _ = db.delete_patient(patient_id, confirm_cascade=True)

        if success:
            result_label.configure(text=message, text_color="#4CAF50")
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("end", message + "\n")
            textbox.configure(state="disabled")
            delete_window.after(1200, delete_window.destroy)
        else:
            result_label.configure(text=message, text_color="#FF6B6B")

    ctk.CTkButton(
        delete_window,
        text="Delete Patient",
        command=execute_delete,
        fg_color="#F44336",
        hover_color="#d32f2f",
    ).pack(pady=8)
    patient_id_entry.bind("<Return>", lambda e: execute_delete())

def open_search_patient_window():
    """Opens a popup to search for a specific patient."""
    search_window = ctk.CTkToplevel(app)
    search_window.title("Search Patient")
    search_window.geometry("450x200")
    search_window.transient(app)
    search_window.grab_set()
    
    label = ctk.CTkLabel(
        search_window,
        text="Enter Patient Name or Phone Number:",
        font=("Arial", 12, "bold")
    )
    label.pack(pady=10)
    
    search_entry = ctk.CTkEntry(
        search_window,
        placeholder_text="e.g., 'Ahmed Khan' or '+923001234567'",
        width=400
    )
    search_entry.pack(pady=10, padx=20)
    search_entry.focus()
    
    def execute_search():
        search_term = search_entry.get().strip()
        if search_term:
            patient_view = PatientListView(textbox, db)
            patient_view.search_patients_ui(search_term)
            search_window.destroy()
    
    search_button = ctk.CTkButton(
        search_window,
        text="Search",
        command=execute_search,
        fg_color="#4CAF50",
        hover_color="#45a049"
    )
    search_button.pack(pady=10)
    
    # Allow Enter key to trigger search
    search_entry.bind("<Return>", lambda e: execute_search())

def open_patient_details_window():
    """Opens a popup to view detailed information for a specific patient."""
    details_window = ctk.CTkToplevel(app)
    details_window.title("View Patient Details")
    details_window.geometry("450x200")
    details_window.transient(app)
    details_window.grab_set()
    
    label = ctk.CTkLabel(
        details_window,
        text="Enter Patient ID:",
        font=("Arial", 12, "bold")
    )
    label.pack(pady=10)
    
    id_entry = ctk.CTkEntry(
        details_window,
        placeholder_text="e.g., 1",
        width=400
    )
    id_entry.pack(pady=10, padx=20)
    id_entry.focus()
    
    def load_details():
        try:
            patient_id = int(id_entry.get().strip())
            patient_view = PatientListView(textbox, db)
            patient_view.display_patient_details(patient_id)
            details_window.destroy()
        except ValueError:
            error_label.configure(text="❌ Please enter a valid Patient ID (number)")
    
    error_label = ctk.CTkLabel(
        details_window,
        text="",
        font=("Arial", 10),
        text_color="#FF6B6B"
    )
    error_label.pack(pady=5)
    
    view_button = ctk.CTkButton(
        details_window,
        text="View Details",
        command=load_details,
        fg_color="#2196F3",
        hover_color="#0b7dda"
    )
    view_button.pack(pady=10)
    
    # Allow Enter key to trigger view
    id_entry.bind("<Return>", lambda e: load_details())

def open_registration_window():
    """Opens a new popup window for registering a patient."""
    reg_window = ctk.CTkToplevel(app)
    reg_window.geometry("400x550")
    reg_window.title("Register New Patient")
    # Bring the popup to the front
    reg_window.attributes("-topmost", True)
    
    ctk.CTkLabel(reg_window, text="Patient Registration", font=("Arial", 20, "bold")).pack(pady=15)
    
    # Input Fields
    entry_first = ctk.CTkEntry(reg_window, placeholder_text="First Name", width=250)
    entry_first.pack(pady=5)
    
    entry_last = ctk.CTkEntry(reg_window, placeholder_text="Last Name", width=250)
    entry_last.pack(pady=5)
    
    entry_dob = ctk.CTkEntry(reg_window, placeholder_text="DOB (YYYY-MM-DD)", width=250)
    entry_dob.pack(pady=5)
    
    entry_gender = ctk.CTkEntry(reg_window, placeholder_text="Gender (Male/Female)", width=250)
    entry_gender.pack(pady=5)
    
    entry_phone = ctk.CTkEntry(reg_window, placeholder_text="Phone (e.g. 0300-XXXXXXX)", width=250)
    entry_phone.pack(pady=5)
    
    entry_address = ctk.CTkEntry(reg_window, placeholder_text="Address", width=250)
    entry_address.pack(pady=5)
    
    entry_emergency = ctk.CTkEntry(reg_window, placeholder_text="Emergency Contact", width=250)
    entry_emergency.pack(pady=5)
    
    def submit_patient():
        # Grab all the text from the entry boxes
        db.insert_new_patient(
            first_name=entry_first.get(),
            last_name=entry_last.get(),
            dob=entry_dob.get(),
            gender=entry_gender.get(),
            phone=entry_phone.get(),
            address=entry_address.get(),
            emergency_contact=entry_emergency.get()
        )
        # Update the main dashboard text box with a success message
        textbox.delete("1.0", "end")
        textbox.insert("end", f"✅ Successfully registered {entry_first.get()} {entry_last.get()} to the database!\nCheck your VS Code terminal for the Patient ID.")
        reg_window.destroy() # Close the popup window

    # Submit Button
    ctk.CTkButton(reg_window, text="Submit Registration", command=submit_patient, fg_color="green", hover_color="dark green").pack(pady=20)

def show_ward_summary():
    """Handler for 'View Ward Summary' button."""
    room_view = RoomAllocationView(textbox, db)
    room_view.show_ward_summary()


def open_view_ward_beds_window():
    """Opens a popup to select a ward and view its beds."""
    wards = db.get_all_wards()

    ward_window = ctk.CTkToplevel(app)
    ward_window.title("View Ward Beds")
    ward_window.geometry("450x250")
    ward_window.transient(app)
    ward_window.grab_set()

    ctk.CTkLabel(
        ward_window,
        text="Select a Ward to View Beds:",
        font=("Arial", 12, "bold")
    ).pack(pady=10)

    if not wards:
        ctk.CTkLabel(ward_window, text="❌ No wards found.", text_color="#FF6B6B").pack(pady=10)
        return

    ward_options = [f"{w[0]} - {w[1]} ({w[2]})" for w in wards]
    ward_map = {f"{w[0]} - {w[1]} ({w[2]})": (w[0], w[1]) for w in wards}

    ward_dropdown = ctk.CTkComboBox(ward_window, values=ward_options, width=380)
    ward_dropdown.set(ward_options[0])
    ward_dropdown.pack(pady=10, padx=20)

    error_label = ctk.CTkLabel(ward_window, text="", font=("Arial", 10), text_color="#FF6B6B")
    error_label.pack(pady=2)

    def load_beds():
        selection = ward_dropdown.get()
        if selection in ward_map:
            ward_id, ward_name = ward_map[selection]
            room_view = RoomAllocationView(textbox, db)
            room_view.show_ward_beds(ward_id, ward_name)
            ward_window.destroy()
        else:
            error_label.configure(text="⚠️ Please select a valid ward.")

    ctk.CTkButton(
        ward_window,
        text="View Beds",
        command=load_beds,
        fg_color="#2196F3",
        hover_color="#0b7dda",
        height=38
    ).pack(pady=10)


def show_active_admissions():
    """Handler for 'View Active Admissions' button."""
    room_view = RoomAllocationView(textbox, db)
    room_view.show_active_admissions()


def open_admit_patient_window():
    """Opens a popup to admit a patient to a specific bed."""
    wards = db.get_all_wards()

    admit_window = ctk.CTkToplevel(app)
    admit_window.title("Admit Patient")
    admit_window.geometry("480x420")
    admit_window.transient(app)
    admit_window.grab_set()

    ctk.CTkLabel(admit_window, text="Admit Patient to Bed", font=("Arial", 14, "bold")).pack(pady=10)

    # Patient ID
    ctk.CTkLabel(admit_window, text="Patient ID:", anchor="w").pack(fill="x", padx=30)
    patient_id_entry = ctk.CTkEntry(admit_window, placeholder_text="e.g., 1", width=400)
    patient_id_entry.pack(pady=5, padx=30)
    patient_id_entry.focus()

    # Ward selection
    ctk.CTkLabel(admit_window, text="Select Ward:", anchor="w").pack(fill="x", padx=30)

    if wards:
        ward_options = [f"{w[0]} - {w[1]} ({w[2]})" for w in wards]
        ward_map = {f"{w[0]} - {w[1]} ({w[2]})": w[0] for w in wards}
    else:
        ward_options = ["No wards available"]
        ward_map = {}

    ward_dropdown = ctk.CTkComboBox(admit_window, values=ward_options, width=400)
    ward_dropdown.set(ward_options[0])
    ward_dropdown.pack(pady=5, padx=30)

    # Available Bed ID
    ctk.CTkLabel(admit_window, text="Bed ID (Available Beds shown below):", anchor="w").pack(fill="x", padx=30)
    bed_id_entry = ctk.CTkEntry(admit_window, placeholder_text="e.g., 5", width=400)
    bed_id_entry.pack(pady=5, padx=30)

    # Available beds info label
    beds_info_label = ctk.CTkLabel(admit_window, text="", font=("Courier", 10), justify="left")
    beds_info_label.pack(pady=2, padx=30)

    def refresh_beds(event=None):
        selection = ward_dropdown.get()
        if selection in ward_map:
            ward_id = ward_map[selection]
            available = db.get_available_beds(ward_id)
            if available:
                ids = ", ".join(str(b[0]) for b in available)
                beds_info_label.configure(text=f"Available Bed IDs: {ids}")
            else:
                beds_info_label.configure(text="No available beds in this ward.")

    ward_dropdown.configure(command=refresh_beds)
    refresh_beds()

    # Admission Date
    import datetime
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    ctk.CTkLabel(admit_window, text="Admission Date (YYYY-MM-DD):", anchor="w").pack(fill="x", padx=30)
    date_entry = ctk.CTkEntry(admit_window, placeholder_text=f"e.g., {today_str}", width=400)
    date_entry.insert(0, today_str)
    date_entry.pack(pady=5, padx=30)

    result_label = ctk.CTkLabel(admit_window, text="", font=("Arial", 10))
    result_label.pack(pady=5)

    def execute_admit():
        try:
            patient_id = int(patient_id_entry.get().strip())
        except ValueError:
            result_label.configure(text="❌ Patient ID must be a number.", text_color="#FF6B6B")
            return
        try:
            bed_id = int(bed_id_entry.get().strip())
        except ValueError:
            result_label.configure(text="❌ Bed ID must be a number.", text_color="#FF6B6B")
            return

        admission_date = date_entry.get().strip()
        if not admission_date:
            result_label.configure(text="❌ Please enter an admission date.", text_color="#FF6B6B")
            return

        success, message = db.admit_patient(patient_id, bed_id, admission_date)
        if success:
            result_label.configure(text=message, text_color="#4CAF50")
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("end", message + "\n")
            textbox.configure(state="disabled")
            admit_window.after(1500, admit_window.destroy)
        else:
            result_label.configure(text=message, text_color="#FF6B6B")

    ctk.CTkButton(
        admit_window,
        text="Admit Patient",
        command=execute_admit,
        fg_color="#4CAF50",
        hover_color="#45a049",
        height=38
    ).pack(pady=10)


def open_discharge_patient_window():
    """Opens a popup to discharge a patient by closing their active admission."""
    discharge_window = ctk.CTkToplevel(app)
    discharge_window.title("Discharge Patient")
    discharge_window.geometry("480x300")
    discharge_window.transient(app)
    discharge_window.grab_set()

    ctk.CTkLabel(discharge_window, text="Discharge Patient", font=("Arial", 14, "bold")).pack(pady=10)
    ctk.CTkLabel(
        discharge_window,
        text="Enter the Admission ID to discharge the patient.\n(Use 'View Active Admissions' to find the Admission ID)",
        font=("Arial", 11),
        justify="center"
    ).pack(pady=5)

    ctk.CTkLabel(discharge_window, text="Admission ID:", anchor="w").pack(fill="x", padx=40)
    admission_id_entry = ctk.CTkEntry(discharge_window, placeholder_text="e.g., 3", width=380)
    admission_id_entry.pack(pady=8, padx=40)
    admission_id_entry.focus()

    result_label = ctk.CTkLabel(discharge_window, text="", font=("Arial", 10))
    result_label.pack(pady=5)

    def execute_discharge():
        try:
            admission_id = int(admission_id_entry.get().strip())
        except ValueError:
            result_label.configure(text="❌ Admission ID must be a number.", text_color="#FF6B6B")
            return

        success, message = db.discharge_patient(admission_id)
        if success:
            result_label.configure(text=message, text_color="#4CAF50")
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("end", message + "\n")
            textbox.configure(state="disabled")
            discharge_window.after(1500, discharge_window.destroy)
        else:
            result_label.configure(text=message, text_color="#FF6B6B")

    ctk.CTkButton(
        discharge_window,
        text="Discharge Patient",
        command=execute_discharge,
        fg_color="#F44336",
        hover_color="#d32f2f",
        height=38
    ).pack(pady=10)

    admission_id_entry.bind("<Return>", lambda e: execute_discharge())


def open_record_vitals_window():
    """Opens a popup to record new vital signs for an active admission."""
    vitals_window = ctk.CTkToplevel(app)
    vitals_window.title("Record New Vitals")
    vitals_window.geometry("480x480")
    vitals_window.transient(app)
    vitals_window.grab_set()

    ctk.CTkLabel(vitals_window, text="Record Patient Vital Signs", font=("Arial", 14, "bold")).pack(pady=10)
    ctk.CTkLabel(
        vitals_window,
        text="Enter the Admission ID and current vital readings:",
        font=("Arial", 11),
        justify="center"
    ).pack(pady=3)

    ranges = db.get_vital_ranges()

    def _make_field(parent, label_text, placeholder):
        ctk.CTkLabel(parent, text=label_text, anchor="w").pack(fill="x", padx=30, pady=(6, 0))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=400)
        entry.pack(padx=30)
        return entry

    admission_entry = _make_field(vitals_window, "Admission ID:", "e.g., 1")
    admission_entry.focus()

    bp_sys_entry = _make_field(
        vitals_window,
        f"Blood Pressure Systolic ({ranges['bp_systolic']['min']}–{ranges['bp_systolic']['max']} mmHg):",
        f"e.g., 120"
    )
    bp_dia_entry = _make_field(
        vitals_window,
        f"Blood Pressure Diastolic ({ranges['bp_diastolic']['min']}–{ranges['bp_diastolic']['max']} mmHg):",
        f"e.g., 80"
    )
    hr_entry = _make_field(
        vitals_window,
        f"Heart Rate ({ranges['heart_rate']['min']}–{ranges['heart_rate']['max']} bpm):",
        f"e.g., 72"
    )
    sugar_entry = _make_field(
        vitals_window,
        f"Sugar Level ({ranges['sugar_level']['min']}–{ranges['sugar_level']['max']} mg/dL):",
        f"e.g., 100"
    )

    result_label = ctk.CTkLabel(vitals_window, text="", font=("Arial", 10))
    result_label.pack(pady=5)

    def execute_record():
        try:
            admission_id = int(admission_entry.get().strip())
        except ValueError:
            result_label.configure(text="❌ Admission ID must be a number.", text_color="#FF6B6B")
            return
        try:
            bp_sys = float(bp_sys_entry.get().strip())
            bp_dia = float(bp_dia_entry.get().strip())
            hr     = float(hr_entry.get().strip())
            sugar  = float(sugar_entry.get().strip())
        except ValueError:
            result_label.configure(text="❌ All vital values must be numeric.", text_color="#FF6B6B")
            return

        success, message = db.insert_vital_record(admission_id, bp_sys, bp_dia, hr, sugar)
        if success:
            result_label.configure(text=message, text_color="#4CAF50")
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("end", message + "\n")
            textbox.configure(state="disabled")
            vitals_window.after(1500, vitals_window.destroy)
        else:
            result_label.configure(text=message, text_color="#FF6B6B")

    ctk.CTkButton(
        vitals_window,
        text="Save Vitals",
        command=execute_record,
        fg_color="#4CAF50",
        hover_color="#45a049",
        height=38
    ).pack(pady=10)

    admission_entry.bind("<Return>", lambda e: execute_record())


def show_patient_vitals():
    """Opens a popup to select an admission, then shows its full vitals history."""
    hist_window = ctk.CTkToplevel(app)
    hist_window.title("View Patient Vitals History")
    hist_window.geometry("450x200")
    hist_window.transient(app)
    hist_window.grab_set()

    ctk.CTkLabel(hist_window, text="Enter Admission ID:", font=("Arial", 12, "bold")).pack(pady=10)

    adm_entry = ctk.CTkEntry(hist_window, placeholder_text="e.g., 1", width=380)
    adm_entry.pack(pady=10, padx=30)
    adm_entry.focus()

    error_label = ctk.CTkLabel(hist_window, text="", font=("Arial", 10), text_color="#FF6B6B")
    error_label.pack(pady=2)

    def load_history():
        try:
            admission_id = int(adm_entry.get().strip())
        except ValueError:
            error_label.configure(text="❌ Admission ID must be a number.")
            return
        vitals_view = DiagnosticVitalsView(textbox, db)
        vitals_view.show_vitals_history(admission_id)
        hist_window.destroy()

    ctk.CTkButton(
        hist_window,
        text="View History",
        command=load_history,
        fg_color="#2196F3",
        hover_color="#0b7dda",
        height=38
    ).pack(pady=10)

    adm_entry.bind("<Return>", lambda e: load_history())


def show_vitals_summary():
    """Opens a popup to select an admission, then shows vitals statistics."""
    summary_window = ctk.CTkToplevel(app)
    summary_window.title("View Vitals Summary")
    summary_window.geometry("450x200")
    summary_window.transient(app)
    summary_window.grab_set()

    ctk.CTkLabel(summary_window, text="Enter Admission ID:", font=("Arial", 12, "bold")).pack(pady=10)

    adm_entry = ctk.CTkEntry(summary_window, placeholder_text="e.g., 1", width=380)
    adm_entry.pack(pady=10, padx=30)
    adm_entry.focus()

    error_label = ctk.CTkLabel(summary_window, text="", font=("Arial", 10), text_color="#FF6B6B")
    error_label.pack(pady=2)

    def load_summary():
        try:
            admission_id = int(adm_entry.get().strip())
        except ValueError:
            error_label.configure(text="❌ Admission ID must be a number.")
            return
        vitals_view = DiagnosticVitalsView(textbox, db)
        vitals_view.show_vitals_summary(admission_id)
        summary_window.destroy()

    ctk.CTkButton(
        summary_window,
        text="View Summary",
        command=load_summary,
        fg_color="#9C27B0",
        hover_color="#7b1fa2",
        height=38
    ).pack(pady=10)

    adm_entry.bind("<Return>", lambda e: load_summary())


def open_vitals_search_window():
    """Opens a popup to search vitals for an admission by date range."""
    import datetime

    search_window = ctk.CTkToplevel(app)
    search_window.title("Search Vitals by Date")
    search_window.geometry("480x320")
    search_window.transient(app)
    search_window.grab_set()

    ctk.CTkLabel(search_window, text="Search Vitals by Date Range", font=("Arial", 14, "bold")).pack(pady=10)

    ctk.CTkLabel(search_window, text="Admission ID:", anchor="w").pack(fill="x", padx=30, pady=(6, 0))
    adm_entry = ctk.CTkEntry(search_window, placeholder_text="e.g., 1", width=400)
    adm_entry.pack(padx=30)
    adm_entry.focus()

    today_str = datetime.date.today().strftime("%Y-%m-%d")

    ctk.CTkLabel(search_window, text="Start Date (YYYY-MM-DD):", anchor="w").pack(fill="x", padx=30, pady=(6, 0))
    start_entry = ctk.CTkEntry(search_window, placeholder_text=f"e.g., {today_str}", width=400)
    start_entry.pack(padx=30)

    ctk.CTkLabel(search_window, text="End Date (YYYY-MM-DD):", anchor="w").pack(fill="x", padx=30, pady=(6, 0))
    end_entry = ctk.CTkEntry(search_window, placeholder_text=f"e.g., {today_str}", width=400)
    end_entry.insert(0, today_str)
    end_entry.pack(padx=30)

    error_label = ctk.CTkLabel(search_window, text="", font=("Arial", 10), text_color="#FF6B6B")
    error_label.pack(pady=4)

    def execute_search():
        try:
            admission_id = int(adm_entry.get().strip())
        except ValueError:
            error_label.configure(text="❌ Admission ID must be a number.")
            return
        start_date = start_entry.get().strip()
        end_date   = end_entry.get().strip()
        if not start_date or not end_date:
            error_label.configure(text="❌ Please enter both start and end dates.")
            return
        vitals_view = DiagnosticVitalsView(textbox, db)
        vitals_view.show_search_results(admission_id, start_date, end_date)
        search_window.destroy()

    ctk.CTkButton(
        search_window,
        text="Search",
        command=execute_search,
        fg_color="#FF9800",
        hover_color="#e68900",
        height=38
    ).pack(pady=10)


def update_auth_ui():
    """Updates UI controls based on current authentication state."""
    if login_status_label is not None:
        role = "Admin" if session["is_authenticated"] else "Guest"
        login_status_label.configure(text=f"User: {session['username']} ({role})")

    if btn_delete_patient is not None:
        if session["is_authenticated"]:
            if not btn_delete_patient.winfo_ismapped():
                btn_delete_patient.pack(side="left", padx=5)
        else:
            if btn_delete_patient.winfo_ismapped():
                btn_delete_patient.pack_forget()


def logout_user():
    """Logs out current user and returns to login screen."""
    session["is_authenticated"] = False
    session["username"] = "Guest"
    textbox.configure(state="normal")
    textbox.delete("1.0", "end")
    textbox.insert("end", "🔒 Logged out successfully.\n")
    textbox.configure(state="disabled")
    update_auth_ui()
    app.withdraw()
    show_login_window()


def show_login_window():
    """Shows modal login window before allowing dashboard access."""
    login_window = ctk.CTkToplevel(app)
    login_window.title("Admin Login")
    login_window.geometry("400x280")
    login_window.transient(app)
    login_window.grab_set()
    login_window.protocol("WM_DELETE_WINDOW", app.destroy)

    ctk.CTkLabel(login_window, text="Hospital Management Login", font=("Arial", 16, "bold")).pack(pady=15)
    ctk.CTkLabel(login_window, text="Username:", anchor="w").pack(fill="x", padx=30)
    username_entry = ctk.CTkEntry(login_window, width=320)
    username_entry.pack(pady=6, padx=30)
    username_entry.focus()
    ctk.CTkLabel(login_window, text="Password:", anchor="w").pack(fill="x", padx=30)
    password_entry = ctk.CTkEntry(login_window, width=320, show="*")
    password_entry.pack(pady=6, padx=30)

    status_label = ctk.CTkLabel(login_window, text="", font=("Arial", 10), text_color="#FF6B6B")
    status_label.pack(pady=5)

    def login_as_admin():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_authenticated"] = True
            session["username"] = ADMIN_USERNAME
            update_auth_ui()
            login_window.destroy()
            app.deiconify()
            app.lift()
        else:
            status_label.configure(text="❌ Invalid admin credentials.")

    def continue_as_guest():
        session["is_authenticated"] = False
        session["username"] = "Guest"
        update_auth_ui()
        login_window.destroy()
        app.deiconify()
        app.lift()

    ctk.CTkButton(
        login_window,
        text="Login as Admin",
        command=login_as_admin,
        fg_color="#4CAF50",
        hover_color="#45a049",
    ).pack(pady=(8, 6))
    ctk.CTkButton(
        login_window,
        text="Continue as Guest",
        command=continue_as_guest,
        fg_color="#607D8B",
        hover_color="#455A64",
    ).pack()

    password_entry.bind("<Return>", lambda e: login_as_admin())


# --- 3. CREATE THE VISUAL ELEMENTS FOR MAIN WINDOW ---
title_label = ctk.CTkLabel(app, text="Hospital Management Dashboard", font=("Arial", 24, "bold"))
title_label.pack(pady=20)

auth_frame = ctk.CTkFrame(app)
auth_frame.pack(pady=5, padx=20, fill="x")
login_status_label = ctk.CTkLabel(auth_frame, text="User: Guest (Guest)", font=("Arial", 11, "bold"))
login_status_label.pack(side="left", padx=8)
btn_logout = ctk.CTkButton(auth_frame, text="Logout", command=logout_user, width=100, fg_color="#FF5722", hover_color="#E64A19")
btn_logout.pack(side="right", padx=8)

# --- DOCTOR MANAGEMENT ---
doctors_frame = ctk.CTkFrame(app)
doctors_frame.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(doctors_frame, text="👨‍⚕️ DOCTORS", font=("Arial", 12, "bold")).pack(side="left", padx=5)
btn_view_doctors = ctk.CTkButton(doctors_frame, text="View All Doctors", command=show_doctors, height=40, font=("Arial", 12), width=150)
btn_view_doctors.pack(side="left", padx=5)

# --- PATIENT MANAGEMENT ---
patient_frame = ctk.CTkFrame(app)
patient_frame.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(patient_frame, text="🏥 PATIENTS", font=("Arial", 12, "bold")).pack(side="left", padx=5)
btn_view_patients = ctk.CTkButton(patient_frame, text="View All Patients", command=show_patient_list, height=40, font=("Arial", 12), width=150, fg_color="#2196F3", hover_color="#0b7dda")
btn_view_patients.pack(side="left", padx=5)

btn_search_patient = ctk.CTkButton(patient_frame, text="Search Patient", command=open_search_patient_window, height=40, font=("Arial", 12), width=150, fg_color="#FF9800", hover_color="#e68900")
btn_search_patient.pack(side="left", padx=5)

btn_patient_details = ctk.CTkButton(patient_frame, text="Patient Details", command=open_patient_details_window, height=40, font=("Arial", 12), width=150, fg_color="#9C27B0", hover_color="#7b1fa2")
btn_patient_details.pack(side="left", padx=5)

btn_register_patient = ctk.CTkButton(patient_frame, text="Register New", command=open_registration_window, height=40, font=("Arial", 12), width=150, fg_color="#4CAF50", hover_color="#45a049")
btn_register_patient.pack(side="left", padx=5)

btn_complete_profile = ctk.CTkButton(patient_frame, text="View Complete Patient Profile", command=open_complete_profile_window, height=40, font=("Arial", 12), width=220, fg_color="#673AB7", hover_color="#512DA8")
btn_complete_profile.pack(side="left", padx=5)

btn_delete_patient = ctk.CTkButton(patient_frame, text="Delete Patient", command=open_delete_patient_window, height=40, font=("Arial", 12), width=150, fg_color="#F44336", hover_color="#d32f2f")
btn_delete_patient.pack(side="left", padx=5)

# --- ROOM ALLOCATION ---
room_frame = ctk.CTkFrame(app)
room_frame.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(room_frame, text="🛏️ ROOMS", font=("Arial", 12, "bold")).pack(side="left", padx=5)

btn_ward_summary = ctk.CTkButton(room_frame, text="Ward Summary", command=show_ward_summary, height=40, font=("Arial", 12), width=150, fg_color="#607D8B", hover_color="#455A64")
btn_ward_summary.pack(side="left", padx=5)

btn_view_ward_beds = ctk.CTkButton(room_frame, text="View Ward Beds", command=open_view_ward_beds_window, height=40, font=("Arial", 12), width=150, fg_color="#00BCD4", hover_color="#0097A7")
btn_view_ward_beds.pack(side="left", padx=5)

btn_active_admissions = ctk.CTkButton(room_frame, text="Active Admissions", command=show_active_admissions, height=40, font=("Arial", 12), width=160, fg_color="#FF9800", hover_color="#e68900")
btn_active_admissions.pack(side="left", padx=5)

btn_admit_patient = ctk.CTkButton(room_frame, text="Admit Patient", command=open_admit_patient_window, height=40, font=("Arial", 12), width=140, fg_color="#4CAF50", hover_color="#45a049")
btn_admit_patient.pack(side="left", padx=5)

btn_discharge_patient = ctk.CTkButton(room_frame, text="Discharge Patient", command=open_discharge_patient_window, height=40, font=("Arial", 12), width=160, fg_color="#F44336", hover_color="#d32f2f")
btn_discharge_patient.pack(side="left", padx=5)

# --- DIAGNOSTIC TESTS & VITALS MANAGEMENT ---
vitals_frame = ctk.CTkFrame(app)
vitals_frame.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(vitals_frame, text="🩺 VITALS", font=("Arial", 12, "bold")).pack(side="left", padx=5)

btn_record_vitals = ctk.CTkButton(vitals_frame, text="Record New Vitals", command=open_record_vitals_window, height=40, font=("Arial", 12), width=160, fg_color="#4CAF50", hover_color="#45a049")
btn_record_vitals.pack(side="left", padx=5)

btn_vitals_history = ctk.CTkButton(vitals_frame, text="Vitals History", command=show_patient_vitals, height=40, font=("Arial", 12), width=150, fg_color="#2196F3", hover_color="#0b7dda")
btn_vitals_history.pack(side="left", padx=5)

btn_vitals_summary = ctk.CTkButton(vitals_frame, text="Vitals Summary", command=show_vitals_summary, height=40, font=("Arial", 12), width=150, fg_color="#9C27B0", hover_color="#7b1fa2")
btn_vitals_summary.pack(side="left", padx=5)

btn_vitals_search = ctk.CTkButton(vitals_frame, text="Search by Date", command=open_vitals_search_window, height=40, font=("Arial", 12), width=150, fg_color="#FF9800", hover_color="#e68900")
btn_vitals_search.pack(side="left", padx=5)

# --- OUTPUT TEXTBOX ---
textbox = ctk.CTkTextbox(app, width=600, height=300, font=("Courier", 11))
textbox.pack(pady=20, padx=20, fill="both", expand=True)

update_auth_ui()
show_login_window()

# --- 4. RUN THE APP ---
if __name__ == "__main__":
    app.mainloop()
