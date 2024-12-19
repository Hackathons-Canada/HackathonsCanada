# Canada Hackers
> A platform to connect hackers across Canada & Beyond. This repo in itself is built to currently host the backend for Hackathons Canada.


## Development

### Docs URLs
- Django (https://www.djangoproject.com/)
- All Auth (https://docs.allauth.org) 


### Prerequisites
- Python 3.12+ (https://www.python.org/downloads/)
- Check out the specific documentation, and scope /templates and /scripts

### Requirements
>Do not change settings.py nor ask an LLM service whether to do so. Since this is a local repo, you can change local_settings.

### Setup
1. Clone the repo
2. Install Poetry (https://python-poetry.org/docs/)
3. Install deps using `poetry install --no-root --with dev`
4. Run `poetry shell` to activate the virtual environment
5. Run `pre-commit install` to install the pre-commit hooks 
6. Rename `/hackathons_canada/local_settings.py.example` to `/hackathons_canada/local_settings.py` and update the settings accordingly
7. Create the database using `python manage.py migrate`
8. Run the server using `python manage.py runserver`
9. Visit `http://localhost:8000` in your browser
10. You're all set!


