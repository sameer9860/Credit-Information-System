# Credit Information System

A centralized Django-based web application designed for multi-cooperative management. The system facilitates member registration, loan processing, and guarantor tracking, featuring a robust eligibility engine to ensure financial compliance and risk management.

## 🚀 Features

- **Multi-Cooperative Architecture**: Manage multiple cooperatives within a single system.
- **Role-Based Access Control (RBAC)**:
  - **Super Admin**: System-wide control, cooperative management, and global blacklisting.
  - **Admin**: Cooperative-level management of members and loans.
  - **Staff**: Operational tasks like member registration and loan application.
- **Member Management**: Track member details, unique system IDs, and blacklist status.
- **Loan Management**: Comprehensive tracking of loan amounts, interest rates, due dates, and repayment status.
- **Guarantor Tracking**: Manage loan guarantors with automatic eligibility checks.
- **Loan Eligibility Engine**: Automated verification of member eligibility based on:
  - Blacklist status.
  - Existing active or overdue loans.
  - Current guantorship status for other active loans.
- **Modern UI**: Responsive dashboard and forms built with Bootstrap 5 and Django Crispy Forms.

## 🛠 Tech Stack

- **Backend**: [Django 6.0](https://www.djangoproject.com/)
- **API**: [Django Rest Framework](https://www.django-rest-framework.org/)
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Database**: SQLite (Development), PostgreSQL (Production ready)
- **Environment**: Python Dotenv for configuration management

## 📋 Prerequisites

- Python 3.10+
- pip (Python package installer)
- virtualenv or venv

## ⚙️ Installation & Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/sameer9860/Credit-Information-System.git
   cd Credit-Information-System
   ```

2. **Set up Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Copy the example environment file and update your settings (SECRET_KEY, DEBUG, etc.):

   ```bash
   cp .env.example .env
   ```

5. **Database Setup**

   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```
   The application will be available at `http://127.0.0.1:8000/`.

## 🧪 Running Tests

To verify the system logic and eligibility engine, run:

```bash
python manage.py test
```

## 📁 Project Structure

- `accounts/`: User authentication and RBAC logic.
- `cooperatives/`: Cooperative management.
- `members/`: Member profiles and status tracking.
- `loans/`: Loan processing, guarantor management, and eligibility services.
- `templates/`: Global HTML templates.
- `static/`: CSS and JavaScript assets.

---

_Built with ❤️ for financial transparency and cooperative growth._
