# Hospital-Management-System
4th-semester DBMS project: Desktop-based Hospital Management System for Pakistan using Python, CustomTkinter, and MySQL

## Features

### Phase 1–4: Doctor & Patient Management
- **View All Doctors** – List all doctors with their specialization and department
- **Register New Patient** – Add a new patient to the database
- **View All Patients** – Display all patients in a formatted ASCII table
- **Search Patient** – Search by name or phone number
- **Patient Details** – View full patient profile and admission history

### Phase 5: Room Allocation & Bed Management
- **Ward Summary** – View bed availability summary across all wards (total / available / occupied)
- **View Ward Beds** – Select a ward and see all its beds with status indicators
- **Active Admissions** – List all currently admitted patients with ward and bed details
- **Admit Patient** – Admit a patient to an available bed with date tracking and validation
- **Discharge Patient** – Close an active admission and automatically free the bed

## Tech Stack
- **Python 3.x**
- **CustomTkinter** – Modern GUI framework
- **MySQL** via `mysql-connector-python`

## Database
Requires a MySQL database named `hospital_db` with the following tables:
`Departments`, `Doctors`, `Patients`, `Wards`, `Beds`, `Admissions`

Default connection: `localhost:3306`, user `root`, no password.

## Running the App
```bash
pip install mysql-connector-python customtkinter
python main_gui.py
```
