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
   pip install django
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
