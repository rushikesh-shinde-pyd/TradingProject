#!/bin/bash

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Create media directory
mkdir media

# Run Django management commands
python manage.py makemigrations
python manage.py migrate

# Run the ASGI application using uvicorn
uvicorn TradingProject.asgi:application --reload
