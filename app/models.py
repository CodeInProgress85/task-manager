from app import db, login
from flask_login import UserMixin
from datetime import datetime
from enum import Enum
from werkzeug.security import check_password_hash, generate_password_hash

# User loader function for Flask-Login
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# User Model
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
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)
    

# Enum for Task Status
class TaskStatus(Enum):
    PENDING = "Pending"
    COMPLETED = "Complete"


# Enum for Task Priority
class TaskPriority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


# Task Model
class Task(db.Model):  # Use Task instead of Tasks (for consistency)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)  # Task name is required
    description = db.Column(db.String(128), nullable=True)  # Description is optional
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)  # Default is 'Pending'
    priority = db.Column(db.Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)  # Default is 'Medium'
    due_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Default is current UTC time

    # Foreign Key: Relates the task to a user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User table

    def __repr__(self):
        return f"<Task {self.name}, Status {self.status}, Priority {self.priority}>"
