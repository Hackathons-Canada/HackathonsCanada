# Canada Hackers
> A platform to connect hackers across Canada & Beyond
 



## Development

### Docs URLs
- Django (https://www.djangoproject.com/)
- All Auth (https://docs.allauth.org) 


### Prerequisites
- Python 3.12+ (https://www.python.org/downloads/)

### Setup
1. Clone the repo
2. Install Poetry (https://python-poetry.org/docs/)
3. Install deps using `poetry install --no-root`
4. Run `poetry shell` to activate the virtual environment

[//]: # (3. Run `poetry instalize` to rename local settings & create the db&#41;)
5. Rename `/canadahackers/local_settings.py.example` to `/canadahackers/local_settings.py` and update the settings accordingly
6. Create the database using `python manage.py migrate`
7. Run the server using `python manage.py runserver`
8. Visit `http://localhost:8000` in your browser
9. You're all set!
