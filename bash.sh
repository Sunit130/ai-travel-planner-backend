#!/usr/bin/env bash
# exit on error
set -o errexit
echo "Bash | Install requirements"
pip install -r requirements.txt

echo "Bash | Migrate"
python manage.py migrate

if [ "$CREATE_SUPERUSER" = "1"]; then
  echo "Bash | Creating Super User"
  python manage.py createsuperuser --no-input --email "$DJANGO_SUPERUSER_EMAIL"
fi
echo "Bash | Complete"