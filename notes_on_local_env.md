```bash
# install postgreSQL (at least version ...)
# by following OS-specific instructions
# then create database:
createuser -s <your os username> # needed on Ubuntu 15.10, not sure if needed elsewhere
createdb skill-huddle

git clone https://github.com/skill-huddle/skill-huddle
cd skill-huddle
# create python env (either by using: venv or virtualenv/virtualenvwrapper)
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```
