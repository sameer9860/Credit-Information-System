## Credit Information System – Phase-Based Implementation Plan

This plan follows a phase-based structure (PHASE 1 → PHASE 15) that matches how you’ll actually build and grow the system.

---

## 🚀 PHASE 1: Project Planning & Architecture

- **Architecture**
  - Centralized Django web application.
  - Database: SQLite (development), PostgreSQL (production).
- **Multi‑cooperative design**
  - One central system.
  - Multiple cooperatives (`Cooperative` model).
  - Each cooperative has its own Admin and Staff users.
  - Super Admin oversees all cooperatives and global settings.

---

## 🏗 PHASE 2: Django Project Setup

1. **Create virtual environment and install Django**
   - Install Python 3 and `virtualenv` / `venv`.
   - Create and activate a virtual environment.
   - Install Django: `pip install django`.

2. **Create project and apps**
   - Create project:
     - `django-admin startproject credit_system`
     - `cd credit_system`
   - Create apps:
     - `python manage.py startapp accounts`
     - `python manage.py startapp cooperatives`
     - `python manage.py startapp members`
     - `python manage.py startapp loans`

3. **Configure settings**
   - Add apps to `INSTALLED_APPS`: `accounts`, `cooperatives`, `members`, `loans`.
   - Configure database as SQLite.
   - Set `LANGUAGE_CODE`, `TIME_ZONE` (Nepal), `STATIC_URL`, `STATICFILES_DIRS`.
   - Set up project `urls.py` and include each app’s `urls.py`.

4. **Base templates and CSS**
   - Create `templates/base.html` with navbar, sidebar, and content block.
   - Add Bootstrap 5 for responsive design.

---

## 👥 PHASE 3: User & Role System (RBAC)

### Step 1: Custom User Model

- **Location**: `accounts/models.py`.
- **Base class**: `AbstractUser`.
- **Fields**:
  - `username`
  - `email`
  - `role` (choices: `superadmin`, `admin`, `staff`)
  - `cooperative` (`ForeignKey` to `Cooperative`, `null=True` for Super Admin)
  - `is_active`
- **Role choices**:

```python
ROLE_CHOICES = (
    ('superadmin', 'Super Admin'),
    ('admin', 'Admin'),
    ('staff', 'Staff'),
)
```

- **Settings**:
  - Set `AUTH_USER_MODEL = 'accounts.User'` in `settings.py`.

### Step 2: RBAC rules

- **Super Admin**
  - Full system control.
  - Create/edit cooperatives.
  - Create Admin users and assign them to cooperatives.
  - Can blacklist/un-blacklist members.
  - Can see data across all cooperatives.
- **Admin (Cooperative level)**
  - Tied to one `Cooperative`.
  - Can manage members and loans of their cooperative.
  - Cannot change system‑wide settings.
- **Staff**
  - Tied to one `Cooperative`.
  - Can create loan applications and view limited history.
  - Cannot blacklist or delete critical data.

### Step 3: Access control helpers

- Use decorators and mixins:
  - `@login_required`.
  - `@user_passes_test(is_superadmin)` / `is_admin` / `is_staff_user`.
  - For class‑based views, create mixins like `SuperAdminRequiredMixin`, `CooperativeAdminRequiredMixin`.
- Always filter data by `request.user.cooperative` for Admin and Staff.

---

## 🏢 PHASE 4: Cooperative Management Module

### App: `cooperatives`

**Model: `Cooperative`**

- Fields:
  - `name`
  - `code` (unique)
  - `address`
  - `contact` (phone/email)
  - `status` (choices: Active/Inactive)
  - `created_at` (auto `DateTimeField`)

**Features**

- Super Admin:
  - Create, edit, activate/deactivate cooperatives.
  - Assign Admin users to a cooperative.
- Admin/Staff:
  - Read‑only visibility of their own cooperative info.

---

## 👤 PHASE 5: Member Management

### App: `members`

**Model: `Member`**

- Fields:
  - `full_name`
  - `citizenship_number` (unique)
  - `unique_system_id` (auto‑generated string)
  - `address`
  - `phone`
  - `blacklist_status` (`BooleanField`)
  - `cooperative` (`ForeignKey` to `Cooperative`)

**Important logic**

- `citizenship_number` must be globally unique:

```python
citizenship_number = models.CharField(max_length=50, unique=True)
```

- `unique_system_id`:
  - Auto‑generate in `save()` or via a utility function (e.g. prefix + incremental or UUID).
- Blacklisting:
  - Only Super Admin can set `blacklist_status = True` (enforced in views/permissions).

---

## 💰 PHASE 6: Loan Management

### App: `loans`

**Model: `Loan`**

- Fields:
  - `loan_id` (auto or custom unique code)
  - `member` (FK to `Member`)
  - `cooperative` (FK to `Cooperative`)
  - `loan_amount`
  - `interest_rate`
  - `loan_date`
  - `due_date`
  - `status` (choices: Active, Cleared, Overdue)
  - `remaining_balance`
  - `created_by` (FK to `User`)

**Rules**

- `due_date` must be \>= `loan_date` (validated in `clean()` or form).
- `remaining_balance` initialized to `loan_amount` and reduced on payments.

---

## 👨‍💼 PHASE 7: Guarantor Management

**Model: `Guarantor`**

- Fields:
  - `name`
  - `citizenship_number`
  - `loan` (FK to `Loan`)
  - `contact_number`
  - `status` (e.g. Active, Released)

**Optional**

- If guarantors can also be members, add optional FK to `Member` and keep citizenship as backup.

---

## 🧠 PHASE 8: Loan Eligibility Engine (Core Logic)

Where to implement:

- In `LoanForm.clean()` (if using forms), or
- In `LoanSerializer.validate()` (if using DRF), or
- In a dedicated service function called before saving a loan.

**Pseudocode**

```python
def validate_loan_eligibility(member):
    if member.blacklist_status:
        raise ValidationError("Member is blacklisted.")

    if Loan.objects.filter(member=member, status='Active').exists():
        raise ValidationError("Member has unpaid loans.")

    if Guarantor.objects.filter(
        citizenship_number=member.citizenship_number,
        loan__status='Active'
    ).exists():
        raise ValidationError("Member is guarantor of an unpaid loan.")
```

- Call this logic before creating/approving a `Loan`.
- Only if all checks pass, allow the loan to be approved with status `Active`.

---

## 🔐 PHASE 9: Security Implementation

1. **Role‑based view protection**
   - Use:
     - `@login_required`
     - `@user_passes_test(lambda u: u.role == 'admin')` etc.
   - For Admin/Staff, always filter by `u.cooperative`.

2. **CSRF**
   - Ensure `CsrfViewMiddleware` is enabled (default).
   - Include `{% csrf_token %}` in all POST forms.

3. **Unique constraints**
   - `citizenship_number` with `unique=True`.
   - `Cooperative.code` with `unique=True`.
   - Any other uniqueness at DB level to prevent duplicates.

4. **Duplicate prevention**
   - Validate in `clean()` / forms and handle `IntegrityError` gracefully.

---

## 📊 PHASE 10: Dashboard System

- **For Cooperative Admin**
  - Total members (their cooperative).
  - Active loans.
  - Overdue loans.
  - Blacklisted members.
- **For Super Admin**
  - Total cooperatives.
  - Total loans.
  - System‑wide overdue loans.

Use Django ORM:

- `annotate()`, `aggregate()`, `Count()`, `Sum()` in dashboard views.

---

## 🔎 PHASE 11: Search & Filter System

- Search by:
  - Citizenship number.
  - Unique system ID.
  - Loan status.
  - Cooperative (for Super Admin).
- Implementation:
  - Simple filters with `request.GET` + ORM `filter()`.
  - Optionally integrate `django-filter` for cleaner filter classes.

---

## 🎨 PHASE 12: Frontend Design

- Use **Bootstrap 5** for:
  - Responsive layout.
  - Navbar + sidebar navigation.
  - Cards for dashboard metrics.
- Templates:
  - `base.html` – shared layout.
  - `dashboard.html`.
  - `member_list.html`.
  - `loan_list.html`.
- Add breadcrumbs and clear action buttons (Add Member, Add Loan, etc.).

---

## 📱 PHASE 13: Mobile Friendly Design

- Use Bootstrap grid and responsive utilities.
- For tables:
  - Use `.table-responsive` wrappers.
  - Avoid too many columns on small screens.

---

## 🧪 PHASE 14: Testing Phase

- Test cases:
  - Loan request for blacklisted member (must fail).
  - Duplicate citizenship number (must fail).
  - Member as guarantor of active loan (must fail).
  - Role‑based access:
    - Staff cannot blacklist.
    - Admin cannot manage cooperatives.
    - Unauthenticated users cannot access any protected view.

- Implement unit tests for:
  - Models (constraints).
  - Eligibility logic.
  - Key views with correct permissions.

---

## 🚀 PHASE 15: Production Preparation

- Database:
  - Switch from SQLite to PostgreSQL.
  - Update `DATABASES` in `settings.py` using environment variables.
- Deployment stack:
  - Use Gunicorn + Nginx on a Linux server or a PaaS.
  - Configure static files with `collectstatic`.
  - Enable HTTPS (Let’s Encrypt or cloud provider).
- Environment:
  - Use `.env` file or environment variables for secrets (SECRET_KEY, DB credentials).
- Monitoring & backups:
  - Set up logging and error tracking.
  - Plan regular database backups.

---

You can now follow these phases one by one: start with PHASE 2 (project + apps), then PHASE 3 (custom user + RBAC), then cooperatives, members, loans, guarantors, and finally the eligibility engine, dashboards, and deployment.

