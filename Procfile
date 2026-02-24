release: python booking/hBooking/manage.py migrate
web: gunicorn --chdir booking/hBooking hBooking.wsgi:application --log-file -