from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# -----------------------------
# APP SETUP
# -----------------------------
app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- CRITICAL FIX: Run db.create_all() at startup for Render ---
# Yeh code Gunicorn ke load hote hi chalega aur tables bana dega.
with app.app_context():
    db.create_all()
# -------------------------------------------------------------

# -----------------------------
# DATABASE MODEL
# -----------------------------
class Todo(db.Model):
    # Dhyan dein, yeh saari lines class ke andar 4 spaces indent honi chahiye
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.title}"

# -----------------------------
# ROUTES
# -----------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')

        new_todo = Todo(title=title, desc=desc)
        db.session.add(new_todo)
        db.session.commit()

        return redirect(url_for('index'))

    allTodo = Todo.query.all()
    return render_template('index.html', allTodo=allTodo)


@app.route('/show')
def show():
    allTodo = Todo.query.all()
    print(allTodo)
    return "This is products page"


@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.get_or_404(sno)

    if request.method == 'POST':
        todo.title = request.form['title']
        todo.desc = request.form['desc']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('update.html', todo=todo)


@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.get_or_404(sno)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))


# -----------------------------
# RUN APP (Local testing only)
# -----------------------------
if __name__ == "__main__":
    # db.create_all() yahan se hata diya gaya hai, kyunki woh upar run hoga.
    app.run(debug=True, port=8000)