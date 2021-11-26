import enum

from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class Status(enum.Enum):
    UPLOADED = 1
    PROCESSED = 2


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(50))
    task = db.relationship(
        'Task', cascade='all, delete, delete-orphan')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    status = db.Column((db.Enum(Status)))
    dateUp = db.Column(db.DateTime())
    datePr = db.Column(db.DateTime())
    nameFormat = db.Column(db.String(200))
    user = db.Column(db.Integer, db.ForeignKey("user.id"))


class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {"llave": value.name, "valor": value.value}


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True


class TaskSchema(SQLAlchemyAutoSchema):
    status = EnumADiccionario(attribute=("status"))

    class Meta:
        model = Task
        include_relationships = True
        load_instance = True
