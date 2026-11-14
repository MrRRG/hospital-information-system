HIS prototype (Django) - quick commands (run inside the his_project folder, with (venv) active)

  python manage.py migrate        create/update the database
  python manage.py seed_all       fake users, patients, appointments, visits (safe to run again)
  python manage.py runserver      start the system at http://127.0.0.1:8000
  python manage.py test           run the automatic tests (21 should pass)

Demo accounts (password for all: Demo@12345)
  admin_demo, doctor_demo, doctor2_demo, nurse_demo, reception_demo
All data is FAKE. This is a training prototype, not for real patient data.
