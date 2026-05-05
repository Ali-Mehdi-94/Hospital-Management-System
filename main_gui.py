import customtkinter as ctk
import database_manager as db

# --- 1. SET UP THE MAIN WINDOW ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("700x700")
app.title("Hospital Management System")

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


# --- 3. CREATE THE VISUAL ELEMENTS FOR MAIN WINDOW ---
title_label = ctk.CTkLabel(app, text="Hospital Management Dashboard", font=("Arial", 24, "bold"))
title_label.pack(pady=20)

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

# --- OUTPUT TEXTBOX ---
textbox = ctk.CTkTextbox(app, width=600, height=300, font=("Courier", 11))
textbox.pack(pady=20, padx=20, fill="both", expand=True)

# --- 4. RUN THE APP ---
if __name__ == "__main__":
    app.mainloop()
