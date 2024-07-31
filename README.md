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
3. Install deps using `poetry install --no-root --with dev`
4. Run `poetry shell` to activate the virtual environment
5. Run `pre-commit install` to install the pre-commit hooks 
6. Rename `/hackathons_canada/local_settings.py.example` to `/hackathons_canada/local_settings.py` and update the settings accordingly
7. Create the database using `python3 manage.py migrate`
8. Run the server using `python3 manage.py runserver`
9. Visit `http://localhost:8000` in your browser
10. You're all set!
