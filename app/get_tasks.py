from app.db import db
from app.models import Task
from app import create_app

# Создаем приложение Flask
app = create_app()

# Работаем с базой данных в контексте приложения
with app.app_context():
    tasks = db.session.query(Task).all()
    for task in tasks:
        print(f"ID: {task.id}, Title: {task.title}, Description: {task.description}, Done: {task.done}")

