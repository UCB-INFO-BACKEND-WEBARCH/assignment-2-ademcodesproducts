from flask import Blueprint, jsonify, request
from datetime import datetime, timezone, timedelta
from marshmallow import ValidationError
from rq import Queue
from app.jobs import send_notification
from app.schemas import TaskSchema
from redis import Redis
from app.models import TaskModel, db
import os

tasks = Blueprint('tasks', __name__)

redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

@tasks.route('/tasks', methods=['GET'])
def list_tasks():
    completed = request.args.get('completed')

    query = TaskModel.query
    if completed is not None:
        status = completed.lower() == 'true'
        query = query.filter_by(completed=status)
    tasks = query.all()

    return jsonify({'tasks': [t.to_dict() for t in tasks]}), 200

@tasks.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = TaskModel.query.get(task_id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task.to_dict()), 200

@tasks.route('/tasks', methods=['POST'])
def create_task():
    schema = TaskSchema()

    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    if data.get('category_id'):
        from app.models import CategoryModel
        if not CategoryModel.query.get(data['category_id']):
            return jsonify({'errors': {'category_id': ['Category not found.']}}), 400

    task = TaskModel(**data)
    db.session.add(task)
    db.session.commit()
    notification_queued = False

    if (
        task.due_date
        and task.due_date > datetime.now(timezone.utc)
        and task.due_date <= datetime.now(timezone.utc) + timedelta(hours=24)
    ):
        q = Queue('notifications', connection=redis_conn)
        q.enqueue(send_notification, task.title)
        notification_queued = True
    return jsonify({'task': task.to_dict(), 'notification_queued': notification_queued}), 201

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
    task = TaskModel.query.get(task_id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted'}), 200
