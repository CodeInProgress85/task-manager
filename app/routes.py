from app import app, db
from .forms import LoginForm, RegistrationForm, EditProfileForm, NewTaskForm, EditTaskForm
from .models import User, Task, TaskPriority, TaskStatus
from flask import render_template, flash, redirect, url_for, request, make_response
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.exceptions import NotFound

@app.route("/", methods=["get", "post"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user)
        if user.username == "admin":
            return redirect(url_for("admin"))
        else:
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for("dashboard"))
        
    response = make_response(render_template("login.html", title="Sign In", form=form))
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/register", methods=["get", "post"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash("Congratulations, you are now a registered user!")
        
        return redirect(url_for("login"))
    
    response = make_response(render_template("register.html", title="Sign Up", form=form))
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/logout", methods=["get", "post"])
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", title="Dashboard", tasks=tasks)

@app.route("/add-a-task", methods=["get", "post"])
@login_required
def add_task():
    form = NewTaskForm()
    if form.validate_on_submit():
        new_task = Task(
            name=form.name.data,
            description=form.description.data,
            priority=form.priority.data,
            user_id = current_user.id
        )
        
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for("dashboard"))
    
    return render_template("add_task.html", title="Add Task", form=form)

@app.route("/edit-task/<int:task_id>", methods=["get", "post"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = EditTaskForm()

    if request.method == "POST" and form.validate_on_submit():
        task.name = form.name.data
        task.description = form.description.data
        task.status = TaskStatus[form.status.data.upper()]
        task.priority = TaskPriority[form.priority.data.upper()]
        task.due_date = form.due_date.data

        db.session.commit()

        return redirect(url_for("dashboard"))

    # Pre-fill the form with the current task data
    form.name.data = task.name
    form.description.data = task.description
    form.status.data = task.status.name
    form.priority.data = task.priority.name
    form.due_date.data = task.due_date

    return render_template("edit_task.html", title="Edit Task", form=form, task=task)

@app.route("/delete-task/<int:task_id>", methods=["get", "post"])
def delete_task(task_id):
    delete_task = Task.query.get_or_404(task_id)
    
    db.session.delete(delete_task)
    db.session.commit()
    
    return redirect(url_for("dashboard"))


@app.route("/profile")
@login_required
def profile():
    pending_tasks = Task.query.filter_by(user_id=current_user.id, status=TaskStatus.PENDING).all()
    completed_tasks = Task.query.filter_by(user_id=current_user.id, status=TaskStatus.COMPLETED).all()

    filter_priority = request.args.get('priority-filter', 'all')
    
    if filter_priority == "low":
        pending_tasks = Task.query.filter_by(user_id=current_user.id, status=TaskStatus.PENDING, priority=TaskPriority.LOW).all()
        completed_tasks = Task.query.filter_by(user_id=current_user.id, status=TaskStatus.COMPLETED, priority=TaskPriority.LOW).all()
    elif filter_priority == "medium":
        pending_tasks = Task.query.filter_by(user_id=current_user.id, status=TaskStatus.PENDING, priority=TaskPriority.MEDIUM).all()
        completed_tasks = Task.query.filter_by(user_id=current_user.id, status=TaskStatus.COMPLETED, priority=TaskPriority.MEDIUM).all()
    elif filter_priority == "high":
        pending_tasks = Task.query.filter_by(user_id=current_user.id, status=TaskStatus.PENDING, priority=TaskPriority.HIGH).all()
        completed_tasks = Task.query.filter_by(user_id=current_user.id, status=TaskStatus.COMPLETED, priority=TaskPriority.HIGH).all()

    else:
        pending_tasks = Task.query.filter_by(user_id=current_user.id, status=TaskStatus.PENDING).all()
        completed_tasks = Task.query.filter_by(user_id=current_user.id, status=TaskStatus.COMPLETED).all()

    return render_template("profile.html", title="Profile", user=current_user, pending_tasks=pending_tasks, completed_tasks=completed_tasks, filter_priority=filter_priority)

@app.route("/edit_profile", methods=["get", "post"])
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        db.session.commit()

        return redirect(url_for("admin"))
    
    response = make_response(render_template("edit_profile.html", title = "Edit Profile", form=form))
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/delete-user", methods=["post"])
@login_required
def delete_account():
    user = current_user

    Task.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    logout_user()

    flash("Your account has been deleted successfully.")

    return redirect(url_for("login"))

@app.route("/admin")
@login_required
def admin():
    if current_user.username != "admin":
        flash("You do not have permission to access this page.")

        return redirect(url_for("dashboard"))

    users = User.query.all()

    return render_template("admin.html", title = "Admin Dashboard", users=users)

@app.route("/admin/delete_user/<int:user_id>", methods=["post"])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if not user:
        flash("User not found.")
        return redirect(url_for("admin"))
    
    Task.query.filter_by(user_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    flash("User deleted successfully.")
        
    return redirect(url_for("admin"))