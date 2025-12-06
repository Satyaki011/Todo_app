from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os # <-- os module ab zaroori hai

# -----------------------------
# APP SETUP
# -----------------------------
app = Flask(__name__)

# NOTE: Local SQLite setup ko hata diya gaya hai.
# Ab hum Render ke Environment Variable ka use karenge.
# os.environ.get("DATABASE_URL") secure tarika hai.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------
# DATABASE MODEL (Koi change nahi)
# -----------------------------
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.title}"

# -----------------------------
# ROUTES (Koi change nahi)
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
# RUN APP (Local testing ke liye)
# -----------------------------
if __name__ == "__main__":
    with app.app_context():
        # Tables create karne ke liye
        db.create_all()
    # Ye settings sirf local chalaane ke liye hai
    app.run(debug=True, port=8000)