# ⚡ EVENT4U • Smart College Event Management System

> **A modern, full-stack, enterprise-grade Django web application designed to digitalize and streamline inter-college festival and event management.**

---

## 📌 Project Overview

**Event4u** transforms the entire manual lifecycle of college events into an online, transparent, and automated workflow. From initial faculty event proposals and multi-tier budget approvals to digital holographic entry badges with verifiable QR codes, live gate check-in scanning, and automated ReportLab PDF financial audit reports — **Event4u** provides a unified control center for all institutional stakeholders.

Developed for **Yashwantrao Chavan College Of Arts , Commerce & Science**.
- **Developed by**: `Hemlata`

---

## 👑 Key Features & Modules

### 1. 🔐 Multi-Role Authentication & Smart Dispatcher
- **5 Distinct User Roles**: Principal/Director, Head of Department (HoD), Faculty Coordinator, Student Sub-Coordinator, and Student Attendees.
- **Role-Based Redirects**: Automatically routes authenticated users to their designated command center.
- **Student Profile Management**: Captures Department/Branch, Semester, Roll Number, College ERP, and WhatsApp contact details.

### 2. 🏛️ 3-Tier Institutional Proposal Workflow
- **Stage 1 (Drafting)**: Faculty Coordinator drafts event scope, objectives, student fees, and college budget requirements.
- **Stage 2 (HoD Endorsement)**: Department Head evaluates feasibility, safety, and departmental alignment with 1-click endorsement.
- **Stage 3 (Principal Sanction)**: Principal grants formal financial sanction, automatically activating the Event and publishing campus announcements.

### 3. 🎫 Digital Holographic Passes & Cryptographic QR Engine
- **Futuristic Pass Badge**: Real-time pass badge containing attendee metadata, barcode lines, registration type, and unique UUID.
- **Live Verifiable QR Code**: Streams secure QR code PNG embedding event ID, pass UUID, and ERP number.
- **Print & Download Ready**: Supports 1-click QR PNG asset download and `@media print` optimized ID badge printing.

### 4. 📷 Live Gate QR Scanner & Attendance Verification
- **Camera-Based Scanning**: Real-time camera QR scanning powered by `html5-qrcode` library for gate staff and sub-coordinators.
- **Manual UUID Search Fallback**: Instant search box with AJAX lookup.
- **Anti-Counterfeit & Duplicate Prevention**: Logs admission timestamps, operator ID, and flags duplicate scan attempts.

### 5. 📊 In-Memory ReportLab PDF Audit Reports
- Dynamically compiles formal PDF event audit reports featuring college headers, coordinator credentials, participation counts, sub-event budget utilization vs balance tables, and institutional signature lines.

### 6. 🖼️ Event Photo Memories & Campus Announcements
- **Memories Gallery**: Filterable photo gallery with upload capabilities for coordinators.
- **Notification Broadcaster**: Targeted announcements for students, volunteers, and staff.

---

## 👥 Default Roles & Credentials for Testing

| Role | Username | Password | Dashboard URL | Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Principal / Admin** | `admin` | `admin123` | `/dashboard/principal/` | Executive oversight, proposal sanctions, Chart.js analytics |
| **Head of Dept (HoD)** | `rajendra` | `ltcoe@123` | `/dashboard/hod/` | Departmental approvals, student metrics |
| **Faculty Coordinator** | `advait` | `ltcoe@123` | `/dashboard/coordinator/` | Sub-coordinator appointments, payment verifier, PDF reports |
| **Sub-Coordinator** | `anjali` / `shraddha` | `ltcoe@123` | `/dashboard/subcoordinator/` | Sub-event operations, volunteer roster, Gate QR Scanner |
| **Student Attendee** | `aanchal` (or register) | `ltcoe@123` | `/dashboard/student/` | Event registration, fee payment, digital passes |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, Django 4.2 LTS
- **Database**: SQLite3 (Production ready for PostgreSQL / MySQL)
- **PDF & QR Engines**: ReportLab 3.6+, QRCode, Pillow
- **Frontend & Styling**: Modern CSS with Glassmorphism, Bootstrap 5.3, FontAwesome 6.4, Google Fonts (`Outfit` & `Plus Jakarta Sans`)
- **Interactive UI**: Chart.js (Analytics), HTML5-QRCode (Gate Scanner)

---

## 🚀 Installation & Setup Guide

### 1. Clone & Navigate to the Project
```bash
git clone https://github.com/your-username/Event4u.git
cd Event4u
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
cd event4u
python manage.py migrate
```

### 5. Run the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Automated Tests

To run the complete unit test suite:
```bash
cd event4u
python manage.py test
```

---

## 📂 Project Directory Structure

```text
Event4u/
├── .vscode/                      # IDE extraPaths configuration
├── event4u/                      # Django Project Root
│   ├── event4u/                  # Project Configuration (settings.py, urls.py, wsgi.py)
│   ├── event4u_app/              # Core Event Management Application
│   │   ├── migrations/           # Database Migrations
│   │   ├── templates/            # Modern Glassmorphic Templates
│   │   │   ├── base/             # Base Layout, Sidebar, Navbar, Footer
│   │   │   ├── dashboards/       # Principal, HoD, Coordinator, Sub-coord, Student
│   │   │   ├── event4u/          # Events, Pass, Scanner, Reports, Memories, Payments
│   │   │   ├── home/             # Landing Page
│   │   │   └── register/         # Student Registration
│   │   ├── admin.py              # Django Admin Interface
│   │   ├── context_processors.py # Global Context Processor
│   │   ├── forms.py              # Modern Bootstrap 5 Forms
│   │   ├── models.py             # Database Models & Relationships
│   │   ├── tests.py              # Automated Unit Test Suite
│   │   ├── urls.py               # Application Routing
│   │   └── views.py              # Business Logic & REST Handlers
│   ├── media/                    # Event Banners & Uploaded Media
│   ├── static/                   # Static Assets (CSS, JS, Fonts, Images)
│   ├── db.sqlite3                # SQLite Database
│   └── manage.py                 # Django CLI Utility
├── requirements.txt              # Project Dependencies (gunicorn, whitenoise, etc.)
├── build.sh                      # Render Deployment Automation Script
├── render.yaml                   # Render Blueprint Specification
├── seed_db.py                    # Production Database Seeder
└── README.md                     # Documentation
```

---

## 🚀 Deploying to Render (Step-by-Step)

### Option 1: 1-Click Blueprint Deploy (Recommended)
1. Push this project code to your **GitHub** repository.
2. Log into [Render.com](https://render.com).
3. Click **"New +"** $\rightarrow$ **"Blueprint"**.
4. Connect your GitHub repository. Render will automatically detect `render.yaml` and configure everything!
5. Click **"Apply"** — Your live app will be deployed in 2-3 minutes with SSL enabled!

### Option 2: Manual Web Service Setup
1. On Render Dashboard, click **"New +"** $\rightarrow$ **"Web Service"**.
2. Connect your GitHub repository.
3. Configure the following fields:
   - **Name**: `event4u`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn event4u.wsgi:application --bind 0.0.0.0:$PORT`
4. In **Environment Variables**, add:
   - `DEBUG`: `True` (or `False` for production)
   - `DJANGO_SETTINGS_MODULE`: `event4u.settings`
   - `ALLOWED_HOSTS`: `*`
   - `PYTHON_VERSION`: `3.10.12`
5. Click **"Deploy Web Service"**.

---

## 📄 License & Credits

Developed with ❤️ by **Hemlata** for **Yashwantrao Chavan College Of Arts , Commerce & Science**.
