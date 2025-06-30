/*******************************************************************************
Create Insurance Providers Table
********************************************************************************/
CREATE TABLE insurance_providers (
    insurance_id INT PRIMARY KEY,
    provider_name VARCHAR(100),
    plan_type VARCHAR(50),
    coverage_percent INT
);

/*******************************************************************************
Create Hospitals Table
********************************************************************************/
CREATE TABLE hospitals (
    hospital_id INT PRIMARY KEY,
    hospital_name VARCHAR(100),
    city VARCHAR(50),
    specialization VARCHAR(150)
);

/*******************************************************************************
Create doctors Table
********************************************************************************/
CREATE TABLE doctors (
    doctor_id INT PRIMARY KEY,
    name VARCHAR(100),
    specialty VARCHAR(50),
    hospital_id INT,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
);


/*******************************************************************************
Create Patients Table
********************************************************************************/
CREATE TABLE patients (
    patient_id INT PRIMARY KEY,
    name VARCHAR(100),
    gender VARCHAR(10),
    date_of_birth DATE,
    phone VARCHAR(20),
    address VARCHAR(150),
    insurance_id INT,
    FOREIGN KEY (insurance_id) REFERENCES insurance_providers(insurance_id)
);

/*******************************************************************************
Create Appointments Table
********************************************************************************/
CREATE TABLE appointments (
    appointment_id INT PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    hospital_id INT,
    appointment_date DATE,
    reason VARCHAR(150),
    status VARCHAR(20),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

/*******************************************************************************
Create Bills Table
********************************************************************************/
CREATE TABLE bills (
    bill_id INT PRIMARY KEY,
    patient_id INT,
    appointment_id INT,
    insurance_id INT,
    bill_date DATE,
    total_amount DECIMAL(10, 2),
    payment_status VARCHAR(20),
    payment_method VARCHAR(20),
    insurance_coverage DECIMAL(10, 2),
    amount_due DECIMAL(10, 2),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
    FOREIGN KEY (insurance_id) REFERENCES insurance_providers(insurance_id)
);


