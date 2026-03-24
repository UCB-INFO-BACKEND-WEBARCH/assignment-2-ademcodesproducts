from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.schemas import CategorySchema
from app.models import CategoryModel, db

categories = Blueprint('categories', __name__)

@categories.route('/categories', methods=['GET'])
def list_categories():
    all_categories = CategoryModel.query.all()
    result = []
    for category in all_categories:
        data = category.to_dict()
        data['task_count'] = len(category.tasks)
        result.append(data)
    return jsonify({'categories': result}), 200

@categories.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = CategoryModel.query.get(category_id)
    if category is None:
        return jsonify({'error': 'Category not found'}), 404
    data = category.to_dict()
    data['tasks'] = [
        {'id': t.id, 'title': t.title, 'completed': t.completed}
        for t in category.tasks
    ]
    return jsonify(data), 200

@categories.route('/categories', methods=['POST'])
def create_category():
    schema = CategorySchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    if CategoryModel.query.filter_by(name=data['name']).first():
        return jsonify({'errors': {'name': ['Category with this name already exists.']}}), 400

    category = CategoryModel(**data)
    db.session.add(category)
    db.session.commit()
    return jsonify({'category': category.to_dict()}), 201

@categories.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = CategoryModel.query.get(category_id)
    if category is None:
        return jsonify({'error': 'Category not found'}), 404

    if category.tasks:
        return jsonify({'error': 'Cannot delete category with existing tasks. Move or delete tasks first.'}), 400

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted'}), 200
