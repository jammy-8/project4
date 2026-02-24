release: cd booking/hBooking && python manage.py migrate
web: cd booking && gunicorn hBooking.hBooking.wsgi --log-file=-