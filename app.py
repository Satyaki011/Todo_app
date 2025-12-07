from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import sys
from sqlalchemy.exc import OperationalError

# -----------------------------
# APP SETUP
# -----------------------------
app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
# IMPORTANT: This ensures we connect to the Render PostgreSQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------
# DATABASE MODEL
# -----------------------------
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.title}"

# -----------------------------
# DATABASE INITIALIZATION CHECK (CRITICAL FIX)
# -----------------------------
# This function checks if the required table exists. If not, it creates them.
def ensure_db_tables_exist():
    with app.app_context():
        try:
            # Try to query the table. If it doesn't exist, an exception is raised.
            # We use `session.query` to force a quick check.
            db.session.query(Todo).first()
        except OperationalError:
            print("--- Database table 'todo' not found. Creating tables now... ---")
            db.create_all()
            db.session.commit()
        except Exception as e:
            # Handle other connection issues gracefully
            print(f"--- Database error during startup: {e} ---")
            # If the database URL is missing, exit the app to prevent silent crashes
            if 'DATABASE_URL' not in os.environ and 'gunicorn' in sys.argv[0]:
                 print("FATAL: DATABASE_URL not set in production.")
                 sys.exit(1)


# -----------------------------
# ROUTES
# -----------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    # Call the initialization check *before* running any database query
    ensure_db_tables_exist()

    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')

        new_todo = Todo(title=title, desc=desc)
        db.session.add(new_todo)
        db.session.commit()

        return redirect(url_for('index'))

    # This query runs only after we ensure the table exists
    allTodo = Todo.query.all()
    return render_template('index.html', allTodo=allTodo)


@app.route('/show')
def show():
    ensure_db_tables_exist()
    allTodo = Todo.query.all()
    print(allTodo)
    return "This is products page"


@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    ensure_db_tables_exist()
    todo = Todo.query.get_or_404(sno)
    
    # ... (rest of the update route logic)

    if request.method == 'POST':
        todo.title = request.form['title']
        todo.desc = request.form['desc']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('update.html', todo=todo)


@app.route('/delete/<int:sno>')
def delete(sno):
    ensure_db_tables_exist()
    todo = Todo.query.get_or_404(sno)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))


# -----------------------------
# RUN APP (Local testing only)
# -----------------------------
if __name__ == "__main__":
    # We call the function here just in case you run locally
    ensure_db_tables_exist() 
    app.run(debug=True, port=8000)
    #alik