# Hospital Information System (HIS) - Training Prototype

A web-based HIS prototype built during my co-op training at Sheikh Hassan Al-Afaleq Hospital
(Al-Ahsa Health Cluster), KFU College of Computer Sciences & Information Technology.

**All data is fake. Do not enter real patient information.**

## Features
- Role-based access: administrator, doctor, nurse, receptionist
- Patient records with validated National ID and role-restricted medical information
- Appointments with double-booking prevention and status workflow (check-in, complete, cancel, no-show)
- Visits: vital signs (nurse) and diagnosis / treatment plan (doctor)
- Audit log of sign-ins, failed sign-ins, and record views and changes (administrator only)
- Dashboard statistics per role, 24 automated tests
- English and Arabic (RTL) interface with a one-click language switch

## Tech
Python 3, Django, SQLite (local) or PostgreSQL (online), WhiteNoise.

## Run locally (Windows)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_all
python manage.py runserver
```
Open http://127.0.0.1:8000. Run the tests with `python manage.py test`.

## Demo accounts (fake, password for all: `Demo@12345`)
`admin_demo`, `doctor_demo`, `doctor2_demo`, `nurse_demo`, `reception_demo`

## Deploy on Vercel
1. Import this repository in Vercel.
2. Add environment variables: `SECRET_KEY` (a long random string) and, for data that survives restarts, `DATABASE_URL` (a PostgreSQL connection string, for example from Neon).
3. Deploy. The tables and demo data are created automatically on first start.
