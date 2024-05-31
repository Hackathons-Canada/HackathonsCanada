# Canada Hackers
> A platform to connect hackers across Canada & Beyond
 



## Development

### Docs URLs
- Django (https://www.djangoproject.com/)
- All Auth (https://docs.allauth.org) 


### Prerequisites
- Python 3.10+ (https://www.python.org/downloads/)

### Setup
1. Clone the repo 
2. Install deps using `pip install -r requirements.txt`
3. Rename `/canadahackers/local_settings.py.example` to `/canadahackers/local_settings.py` and update the settings accordingly
4. Create the database using `python manage.py migrate`
4. Run the server using `python manage.py runserver`
5. Visit `http://localhost:8000` in your browser
6. You're all set!
