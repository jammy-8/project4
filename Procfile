release: cd booking/hBooking && python manage.py migrate
web: gunicorn --chdir booking hBooking.hBooking.wsgi:application