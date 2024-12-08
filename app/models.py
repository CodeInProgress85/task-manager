from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from enum import Enum
from app import db, login

# User loader function for Flask-Login
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))

    # One-to-many relationship between User and Task
    tasks = db.relationship("Task", backref="owner", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        """Set the password after hashing it"""
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        """Verify if the given password matches the stored hashed password"""
        return check_password_hash(self.password, password)


# Enum class for task status
class TaskStatus(Enum):
    PENDING = "Pending"
    COMPLETED = "Complete"


# Enum class for task priority
class TaskPriority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String(128), nullable=True)
    status = db.Column(db.Enum(TaskStatus),
                       default=TaskStatus.PENDING,
                       nullable=False)
    priority = db.Column(db.Enum(TaskPriority),
                         default=TaskPriority.MEDIUM,
                         nullable=False)
    due_date = db.Column(db.DateTime,
                         default=datetime.utcnow,
                         nullable=False)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id'),
                        nullable=False)

    def __repr__(self):
        return (f"<Task {self.name}, "
                f"Status {self.status}, "
                f"Priority {self.priority}>")
