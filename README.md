# Smart Clinic Queue Management System 🏥

A complete, high-end automated queue management system built for modern clinics. 

## Core Features:
* **Automated WhatsApp Notifications:** Integrates with n8n and Docker to send patient alerts (at entry and when their turn is approaching).
* **Premium TV Display UI:** High-contrast, ultra-modern HTML/CSS interfaces rendered seamlessly via PyQt5 WebEngine for the waiting room.
* **One-Click Execution:** Automated `.bat` script to spin up Docker containers (n8n, WhatsApp server, MySQL) and the Python GUI simultaneously.
* **Real-time Sync:** Synchronizes the receptionist dashboard with the waiting room display instantly using JSON and embedded JavaScript.

## Tech Stack:
* **Backend:** Python (PyQt5)
* **Database:** MySQL
* **Automation:** n8n, Docker
* **Frontend:** HTML, CSS, JavaScript (Embedded via QWebEngineView)
