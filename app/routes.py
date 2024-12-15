from flask_restx import Api, Resource, fields, Namespace
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .db import db
from .models import Task, User

# Инициализация API
api = Api(
    title="Task Manager API",
    description="API для управления списком задач с поддержкой JWT авторизации",
    version="1.0"
)

# Пространства имен для эндпоинтов
tasks_ns = Namespace('tasks', description="Эндпоинты для работы с задачами")
auth_ns = Namespace('auth', description="Эндпоинты для регистрации и авторизации")

# Модель задачи
task_model = tasks_ns.model('Task', {
    'id': fields.Integer(readOnly=True, description="ID задачи"),
    'title': fields.String(required=True, description="Название задачи"),
    'description': fields.String(description="Описание задачи"),
    'done': fields.Boolean(description="Статус выполнения задачи")
})

# Модель пользователя для авторизации
user_model = auth_ns.model('User', {
    'username': fields.String(required=True, description="Имя пользователя"),
    'password': fields.String(required=True, description="Пароль пользователя")
})

# Эндпоинты задач
@tasks_ns.route('/')
class TaskList(Resource):
    @jwt_required()
    @tasks_ns.marshal_list_with(task_model)
    def get(self):
        """Получение всех задач текущего пользователя"""
        user_id = get_jwt_identity()
        tasks = Task.query.filter_by(user_id=user_id).all()
        return tasks

    @jwt_required()
    @tasks_ns.expect(task_model, validate=True)
    @tasks_ns.marshal_with(task_model, code=201)
    def post(self):
        """Создание новой задачи для текущего пользователя"""
        user_id = get_jwt_identity()
        data = request.json
        new_task = Task(title=data['title'], description=data.get('description', ''), user_id=user_id)
        db.session.add(new_task)
        db.session.commit()
        return new_task, 201

@tasks_ns.route('/<int:task_id>')
class TaskDetail(Resource):
    @jwt_required()
    @tasks_ns.marshal_with(task_model)
    def get(self, task_id):
        """Получение задачи по ID"""
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
        return task

    @jwt_required()
    @tasks_ns.expect(task_model, validate=True)
    @tasks_ns.marshal_with(task_model)
    def put(self, task_id):
        """Обновление задачи по ID"""
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
        data = request.json
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.done = data.get('done', task.done)
        db.session.commit()
        return task

    @jwt_required()
    def delete(self, task_id):
        """Удаление задачи по ID"""
        user_id = get_jwt_identity()
        task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
        db.session.delete(task)
        db.session.commit()
        return '', 204

# Эндпоинты авторизации
@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model, validate=True)
    def post(self):
        """Регистрация нового пользователя"""
        data = request.json
        if User.query.filter_by(username=data['username']).first():
            return {"message": "Пользователь уже существует"}, 400

        new_user = User(username=data['username'])
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return {"message": "Пользователь успешно зарегистрирован"}, 201


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_model, validate=True)
    def post(self):
        """Авторизация пользователя и получение JWT-токена"""
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.check_password(data['password']):
            return {"message": "Неверное имя пользователя или пароль"}, 401

        access_token = create_access_token(identity=user.id)
        return {"access_token": access_token}, 200

# Добавление имен в API
api.add_namespace(tasks_ns, path='/tasks')
api.add_namespace(auth_ns, path='/auth')
