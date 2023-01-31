rmdir /s /q user\migrations
rmdir /s /q tournament\migrations
del "db.sqlite3"
python manage.py makemigrations user
python manage.py makemigrations tournament
python manage.py migrate