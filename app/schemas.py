from marshmallow import Schema, fields, validate, ValidationError

class CategorySchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    color = fields.Str(load_default=None, validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$', error='Must be a valid hex color (e.g. #FF5733).'))

class TaskSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(load_default=None, validate=validate.Length(max=500))
    due_date = fields.DateTime(load_default=None)
    category_id = fields.Int(load_default=None)
    completed = fields.Bool(load_default=False)