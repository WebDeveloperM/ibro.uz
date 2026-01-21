# Imlo.uz Clone

A Django-based Uzbek language spelling dictionary website, similar to imlo.uz.

## Features

- Word definitions
- Categories and collections
- Words by letter count
- Most searched words
- Random words

## Setup

1. Install Python 3.8+
2. Clone the repo
3. Create virtual environment: `python -m venv .venv`
4. Activate: `.venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install django`
6. Run migrations: `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Run server: `python manage.py runserver`

## Usage

- Home: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

Add words and categories via admin.