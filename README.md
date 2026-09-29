# Healthcare Booking API

A backend REST API for a healthcare diagnostic booking system. The application provides user authentication, diagnostic centre and test management, appointment booking, simulated payments, payment webhooks, authorization, validation, and automated testing.

## Features

* User registration and authentication
* JWT-based authentication
* Access and refresh tokens
* User profile endpoint
* Diagnostic centre management
* Diagnostic test management
* Centre-specific test pricing
* Appointment booking
* Booking cancellation
* Simulated payment processing
* Payment success/failure handling
* Idempotent payment webhooks
* User-level authorization
* Admin-only management operations
* Request validation and error handling
* PostgreSQL database integration
* Swagger/OpenAPI documentation
* Automated API and business-logic tests

---

## Tech Stack

| Technology                     | Purpose                         |
| ------------------------------ | ------------------------------- |
| Python                         | Backend programming language    |
| Django                         | Web framework                   |
| Django REST Framework          | REST API development            |
| PostgreSQL                     | Relational database             |
| SimpleJWT                      | JWT authentication              |
| drf-spectacular                | OpenAPI/Swagger documentation   |
| pytest / Django Test Framework | Automated testing               |
| python-dotenv                  | Environment variable management |

---

## Project Structure

```text
project-root/
│
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
│
├── diagnostics/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
│
├── bookings/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── payments/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── .env
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

> `.env`, virtual environments, cache files, and other sensitive/local files should not be committed to GitHub.

---

# Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_DIRECTORY>
```

**UPDATE:** Replace:

```text
<YOUR_GITHUB_REPOSITORY_URL>
<YOUR_PROJECT_DIRECTORY>
```

with your actual GitHub repository URL and project directory.

---

## 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

### macOS/Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```

### Important

Do **not** commit `.env` to GitHub.

The `.gitignore` file should contain:

```gitignore
.env
venv/
__pycache__/
*.pyc
db.sqlite3
```

---

# Database Setup

This project uses PostgreSQL.

Create a PostgreSQL database and configure the database credentials in `.env`.

Then run:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create an administrator account:

```bash
python manage.py createsuperuser
```

Follow the prompts to create the admin user.

---

# Run the Application

Start the development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

---

# API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

Swagger provides an interactive interface for testing the available API endpoints.

---

# Authentication APIs

## Signup

```http
POST /api/auth/signup/
```

Example request:

```json
{
    "email": "user@example.com",
    "username": "testuser",
    "password": "StrongPassword123",
    "password2": "StrongPassword123"
}
```

---

## Login

```http
POST /api/auth/login/
```

Example:

```json
{
    "email": "user@example.com",
    "password": "StrongPassword123"
}
```

The response provides an access token and refresh token.

Use the access token for authenticated requests:

```http
Authorization: Bearer <access_token>
```

---

## Refresh Token

```http
POST /api/auth/refresh/
```

Example:

```json
{
    "refresh": "<refresh_token>"
}
```

---

## Current User

```http
GET /api/auth/me/
```

Requires authentication.

---

# Diagnostic Centre APIs

## List Centres

```http
GET /api/centres/
```

Returns active diagnostic centres.

Authentication is required.

---

## Create Centre

```http
POST /api/centres/
```

Admin access is required.

Example:

```json
{
    "name": "Example Diagnostics",
    "address": "Example Address",
    "city": "Noida",
    "state": "Uttar Pradesh",
    "phone": "+91 9876543210"
}
```

---

## View Centre

```http
GET /api/centres/{id}/
```

---

## Update Centre

```http
PUT /api/centres/{id}/
```

or:

```http
PATCH /api/centres/{id}/
```

Admin access is required.

---

## Delete Centre

```http
DELETE /api/centres/{id}/
```

Admin access is required.

---

# Diagnostic Test APIs

## List Tests

```http
GET /api/tests/
```

Returns active diagnostic tests.

---

## Create Test

```http
POST /api/tests/
```

Admin access is required.

Example:

```json
{
    "centre": 1,
    "name": "Complete Blood Count",
    "description": "Basic blood examination",
    "price": "499.00"
}
```

---

## View Test

```http
GET /api/tests/{id}/
```

---

## Update Test

```http
PUT /api/tests/{id}/
```

or:

```http
PATCH /api/tests/{id}/
```

Admin access is required.

---

## Delete Test

```http
DELETE /api/tests/{id}/
```

Admin access is required.

---

# Booking APIs

## Create Booking

```http
POST /api/bookings/
```

Authentication is required.

Example:

```json
{
    "centre": 1,
    "test": 1,
    "appointment_datetime": "2026-10-15T10:30:00Z"
}
```

The authenticated user is automatically associated with the booking.

The booking amount is automatically taken from the selected test price.

The initial booking status is:

```text
PENDING
```

---

## List My Bookings

```http
GET /api/bookings/
```

A user can only see their own bookings.

---

## View Booking

```http
GET /api/bookings/{id}/
```

Users cannot access another user's booking.

---

## Cancel Booking

```http
POST /api/bookings/{id}/cancel/
```

Only bookings with `PENDING` status can be cancelled.

---

# Payment APIs

## Create Payment

```http
POST /api/payments/
```

Authentication is required.

Example:

```json
{
    "booking": 1
}
```

The payment amount is automatically taken from the booking amount.

The client cannot manually modify the payment amount.

The payment system simulates a payment result:

```text
SUCCESS
```

or:

```text
FAILED
```

---

## Process Payment

```http
POST /api/payments/{id}/process/
```

Processes an existing pending payment.

The simulated payment generates a transaction ID and updates the associated booking.

Successful payment:

```text
Payment → SUCCESS
Booking → CONFIRMED
```

Failed payment:

```text
Payment → FAILED
Booking → FAILED
```

---

# Payment Webhook

```http
POST /api/payments/webhook/
```

The webhook simulates a payment gateway sending a payment status update.

Example:

```json
{
    "event_id": "event-12345",
    "transaction_id": "SIM-ABC123456789",
    "status": "SUCCESS"
}
```

Supported statuses:

```text
SUCCESS
FAILED
```

---

# Webhook Idempotency

Webhook processing is designed to be idempotent.

Each webhook contains an `event_id`.

If the same event is received again, the API does not create another payment or corrupt the existing payment state.

Example:

### First request

```text
event_id = event-123
status = SUCCESS
```

Payment is updated successfully.

### Repeated request

```text
event_id = event-123
status = SUCCESS
```

The API recognizes that the event has already been processed and does not apply the event again.

The implementation also prevents the same webhook event ID from being reused for another payment.

---

# Booking and Payment Flow

The main application flow is:

```text
User Signup
     │
     ▼
User Login
     │
     ▼
Receive JWT
     │
     ▼
View Diagnostic Centres
     │
     ▼
Select Diagnostic Test
     │
     ▼
Create Booking
     │
     ▼
Booking = PENDING
     │
     ▼
Create / Process Payment
     │
     ├───────────────┐
     ▼               ▼
SUCCESS           FAILED
     │               │
     ▼               ▼
Booking           Booking
CONFIRMED         FAILED
```

A payment gateway webhook can also update the payment and booking status.

---

# Authorization

The API uses JWT authentication.

### Public endpoints

The following authentication endpoints are accessible without an existing JWT:

```text
POST /api/auth/signup/
POST /api/auth/login/
POST /api/auth/refresh/
```

### Authenticated endpoints

Most application APIs require:

```http
Authorization: Bearer <access_token>
```

### Admin-only operations

Diagnostic centre and diagnostic test creation, modification, and deletion require administrator privileges.

Users cannot modify another user's bookings or payments.

---

# Validation and Edge Cases

The API handles several invalid scenarios, including:

* Missing required fields
* Invalid user credentials
* Duplicate email registration
* Password mismatch
* Short passwords
* Invalid centre IDs
* Invalid test IDs
* Inactive diagnostic centres
* Inactive diagnostic tests
* Test belonging to a different centre
* Missing appointment date/time
* Unauthorized booking access
* Unauthorized payment access
* Payment for cancelled booking
* Attempting to cancel non-pending bookings
* Invalid payment webhook status
* Unknown transaction IDs
* Duplicate webhook events
* Reusing an existing webhook event ID
* Attempting to modify finalized payments

---

# Database Design

The main entities are:

```text
User
 │
 └── Booking
       │
       ├── DiagnosticCentre
       │      │
       │      └── DiagnosticTest
       │
       └── Payment
```

### User

Stores authentication and user information.

### DiagnosticCentre

Stores diagnostic centre information such as:

* Name
* Address
* City
* State
* Phone
* Active status

### DiagnosticTest

Stores:

* Test name
* Description
* Price
* Associated diagnostic centre
* Active status

### Booking

Stores:

* User
* Diagnostic centre
* Diagnostic test
* Appointment date/time
* Amount
* Booking status
* Creation/update timestamps

### Payment

Stores:

* Booking
* Amount
* Payment status
* Transaction ID
* Webhook event ID
* Creation/update timestamps

---

# Design Decisions

## Booking Amount

The booking amount is calculated from the selected diagnostic test price instead of accepting the amount directly from the client.

This prevents a client from submitting an arbitrary payment amount.

---

## User Ownership

Bookings and payments are filtered using the authenticated user.

This prevents one user from accessing another user's booking or payment information.

---

## Payment Status

Payment and booking statuses are kept synchronized:

```text
Payment SUCCESS → Booking CONFIRMED

Payment FAILED → Booking FAILED
```

---

## Webhook Idempotency

Webhook event IDs are stored and uniquely constrained to prevent duplicate event processing.

---

## PostgreSQL

PostgreSQL is used as the relational database for persistent application data.

Database credentials are loaded through environment variables rather than being hard-coded in the source code.

---

# Testing

The project includes automated tests covering authentication, diagnostic centres, diagnostic tests, bookings, payments, authorization, validation, and webhook behavior.

Run the complete test suite with:

```bash
python manage.py test -v 2
```

Current test status:

```text
68 tests passing
```

Example test areas include:

* User signup
* User login
* Invalid credentials
* JWT authentication
* Token refresh
* Duplicate registration
* Centre creation
* Test creation
* Centre/test authorization
* Centre/test retrieval
* Booking creation
* Booking ownership
* Booking validation
* Booking cancellation
* Payment creation
* Payment amount validation
* Payment success
* Payment failure
* Payment authorization
* Webhook success
* Webhook failure
* Duplicate webhook handling
* Webhook event ID reuse
* Finalized payment protection

---

# API Security Considerations

The project includes:

* JWT authentication
* Password hashing through Django authentication
* Permission-based authorization
* User-level object access restrictions
* Admin-only management operations
* Environment-based database credentials
* Input validation
* Payment ownership validation
* Webhook idempotency

Sensitive credentials should never be committed to source control.

---

# Assumptions

The following assumptions were made for the assignment:

1. Payment processing is simulated and does not connect to a real payment provider.
2. Diagnostic centres and tests are managed by administrators.
3. Users can create bookings only for active centres and active tests.
4. A test must belong to the selected diagnostic centre.
5. Booking amounts are derived from the selected test price.
6. A booking initially starts with `PENDING` status.
7. Successful payments confirm bookings.
8. Failed payments mark bookings as failed.
9. Cancelled bookings cannot be paid.
10. Webhook events are identified using unique event IDs.

---

# Future Improvements

Possible production-level improvements include:

* Redis caching
* Celery background tasks
* Real payment gateway integration
* Webhook signature verification
* Rate limiting
* API pagination
* Advanced filtering and searching
* Structured application logging
* Docker and Docker Compose
* CI/CD pipeline
* Production deployment
* Database indexing optimization
* Automated API monitoring
* Role-based access control
* Email/SMS appointment notifications

---

# Useful Commands

Activate virtual environment:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Create migrations:

```bash
python manage.py makemigrations
```

Run development server:

```bash
python manage.py runserver
```

Run tests:

```bash
python manage.py test -v 2
```

Check project configuration:

```bash
python manage.py check
```

Create admin user:

```bash
python manage.py createsuperuser
```

Generate OpenAPI schema:

```bash
python manage.py spectacular --file schema.yml
```


---

# Author

# Name: Kartikay Mittal

GitHub: **<!-- UPDATE: YOUR GITHUB PROFILE URL -->**

Email: **<!-- UPDATE: YOUR EMAIL, OPTIONAL -->**

Repository: **<!-- UPDATE: YOUR GITHUB REPOSITORY URL -->**
