CREATE DATABASE IF NOT EXISTS clinic_db;
USE clinic_db;

CREATE TABLE patient_queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    queue_number INT NOT NULL,
    status ENUM('waiting', 'in_clinic', 'completed') DEFAULT 'waiting',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);