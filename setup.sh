#!/bin/bash

# Clone the repository
git clone https://github.com/rushikesh-shinde-pyd/TradingProject.git .

# Create and activate virtual environment
virtualenv -p python3.9 venv
source venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Create media directory
mkdir media

# Run Django management commands
python manage.py check
python manage.py makemigrations

# Run the ASGI application using uvicorn
uvicorn TradingProject.asgi:application --reload
