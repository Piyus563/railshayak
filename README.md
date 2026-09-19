<<<<<<< HEAD
# RailShayak

RailShayak is a Django-based railway assistance and management platform designed to support passengers, station staff, coolies, and administrators. The project includes booking management, complaints, lost and found tracking, notifications, station information, account management, and admin analytics.

## Features

- Passenger account registration and login
- Railway station listing and detail pages
- Booking and booking history management
- Coolie booking support
- Complaint submission and tracking
- Lost and found item management
- Admin dashboard and analytics views
- Notification center
- Review and support modules

## Tech Stack

- Python
- Django
- SQLite (default development database)
- HTML, CSS, and JavaScript templates
- Django ORM and migrations

## Project Structure

- accounts/ — user accounts and profile logic
- bookings/ — reservation and booking workflows
- stations/ — station data and map pages
- complaints/ — grievance handling
- lost_found/ — item recovery management
- notifications/ — user notifications
- reviews/ — user feedback and reviews
- assistance/ — support request handling
- coolies/ — coolie-related services
- analytics/ — reporting and dashboard stats
- templates/ — HTML templates
- static/ — frontend assets
- config/ — Django settings and routing

## Requirements

- Python 3.10+
- pip
- virtual environment recommended

## Setup Instructions

1. Clone the repository
   ```bash
   git clone https://github.com/Piyus563/railshayak.git
   cd railshayak
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate       # Windows
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations
   ```bash
   python manage.py migrate
   ```

5. Start the development server
   ```bash
   python manage.py runserver
   ```

6. Open the app in your browser
   ```text
   http://127.0.0.1:8000/
   ```

## Deploy on Render

This repository includes a `render.yaml` blueprint for a Django web service and a PostgreSQL database.

1. Push the repository to GitHub.
2. In Render, choose **New > Blueprint** and select the repository.
3. Render will install dependencies, collect static files, run migrations, seed demo data, and start Gunicorn.
4. The generated `DJANGO_SECRET_KEY` and `DATABASE_URL` are configured by the blueprint.

For a manual Render web service, use:

```text
Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed_data
Start Command: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `DATABASE_URL` in the Render environment. Add the Render public URL to `CSRF_TRUSTED_ORIGINS` only when using a custom security configuration; the app automatically trusts its `RENDER_EXTERNAL_HOSTNAME`.

## Admin Setup

Create a superuser if needed:

```bash
python manage.py createsuperuser
```

Then log in from the admin panel or the application dashboard.

## Default Database

The project currently uses SQLite for development and local testing.

## Notes

This repository is intended as a railway service management app and may be expanded with additional APIs, authentication improvements, production deployment settings, and deployment configuration.

## License

This project is for educational and project demonstration purposes unless a separate license is added by the repository owner.
=======
# RailSaathi

RailSaathi is a Django + Django REST Framework platform for railway station assistance: verified coolie booking, live booking status, station maps and facilities, passenger assistance, lost and found, complaints, role-based dashboards, analytics, and a local AI station assistant.

## Quick start

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Open http://127.0.0.1:8000/. The seed command is idempotent and creates NJP demo data, a small HWH directory entry, platforms, facilities, bookings, reviews, and notifications.

SQLite is the default for local development. To use PostgreSQL, set `DB_ENGINE=postgres` and the `POSTGRES_*` values from `.env.example` before running migrations.

## Razorpay TEST MODE payments

Payments use Razorpay Checkout with UPI, QR, cards, and net banking enabled by the gateway. The server creates the order and verifies the Razorpay signature, order, amount, and captured status before a paid booking is sent to the coolie queue. Card numbers, UPI PINs, and other payment credentials are never stored by this application.

1. Create a Razorpay account and switch the Dashboard to **Test Mode**.
2. Copy the Test Key ID and Test Key Secret from **Account & Settings > API Keys**.
3. Copy `.env.example` to `.env` and set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`. Never commit `.env`.
4. Install dependencies and apply the existing database migrations:

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

5. Log in as a passenger, create a coolie booking, select the service date/time, and click **Pay Now**. In Razorpay Test Mode select UPI and use the test payment details shown in the Razorpay Checkout test documentation. A QR option is displayed when enabled for the account.

To test failures, close the checkout or use Razorpay's failed-payment test option. The booking remains unpaid and can be retried. Refreshing a success URL does not create a second payment, and invalid order IDs, signatures, amounts, or uncaptured payments are rejected.

## Demo accounts

- Passenger: `priya_singh` / `pass123`
- Coolie: `ramesh_kumar` / `coolie123`
- Admin: `admin` / `admin123`

Change these credentials before using the application outside a demo environment.

## Main routes

- `/` passenger landing page
- `/accounts/dashboard/` role-aware dashboard redirect
- `/bookings/book/` coolie booking wizard
- `/stations/map/NJP/` Leaflet station map
- `/portal/` admin analytics portal
- `/api/v1/` REST API root
- `/accounts/assistant/chat/` authenticated station-help chatbot POST endpoint
- `/accounts/assistant/recommendations/?station=NJP&bags=3&assistance=true` live coolie recommendations

## Development checks

```powershell
python manage.py check
python manage.py test
```

The recommendation engine is intentionally explainable and local: it ranks verified online coolies by rating, experience, current platform, luggage fit, and accessibility. The `scikit-learn` dependency is included for extending this baseline with trained station-demand models without requiring an external AI provider for the demo.
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
