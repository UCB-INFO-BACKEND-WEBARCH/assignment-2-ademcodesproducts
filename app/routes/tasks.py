from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.schemas import TaskSchema
from redis import Redis
from app.models import TaskModel, db
import os

tasks = Blueprint('tasks', __name__)

redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

@tasks.route('/tasks', methods=['GET'])
def list_tasks():
    tasks = TaskModel.query.all()
    return jsonify({'tasks': [t.to_dict() for t in tasks]}), 200

@tasks.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = TaskModel.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@tasks.route('/tasks', methods=['POST'])
def create_task():
    schema = TaskSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    task = TaskModel(**data)
    db.session.add(task)
    db.session.commit()
    return jsonify({'task': task.to_dict(), 'notification_queued': True}), 201

@tasks.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = TaskModel.query.get_or_404(task_id)
    schema = TaskSchema(partial=True)
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    for key, value in data.items():
        setattr(task, key, value)
    db.session.commit()
    return jsonify({'task': task.to_dict()}), 200

@tasks.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = TaskModel.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted'}), 200
