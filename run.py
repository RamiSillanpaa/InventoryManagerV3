# File: run.py
"""
Development server runner.
Do not use in production - use proper WSGI server instead.
"""
from app import create_app

app = create_app('development')

if __name__ == '__main__':
    app.run()