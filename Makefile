start:
	cd mysite && python manage.py runserver

mm:
	cd mysite && python manage.py makemigrations

m:
	cd mysite && python manage.py migrate

freeze:
	pip freeze > requirements.txt

user:
	cd mysite && python manage.py createsuperuser

# wagtail start (name project)