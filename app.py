from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


# themes
themes = {
    'theme1': 'main.css',
    'theme2': 'theme2.css',
    'theme3': 'theme3.css',
    'theme4': 'theme4.css'
}

# Default theme
default_theme = 'theme1'

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300))
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "error while adding"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks,theme=themes.get(default_theme))


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "error in deleting"


@app.route('/completed/<int:id>')
def completion(id):
    task_completed = Todo.query.get_or_404(id)
    task_completed.completed = 1
    try:
        db.session.commit()
        return redirect('/')
    except:
        return "error while checking off"


@app.route('/not-completed/<int:id>')
def undocompletion(id):
    task_completed = Todo.query.get_or_404(id)
    task_completed.completed = 0
    try:
        db.session.commit()
        return redirect('/')
    except:
        return "error removing check"


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task_to_update = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task_to_update.content = request.form['content']
        task_to_update.completed = 0
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "error while updating"
    else:
        return render_template('update.html', task=task_to_update,theme=themes.get(default_theme))

@app.route('/themes', methods=['GET', 'POST'])
def theme_select():
    return render_template('themes.html')

@app.route('/set-theme/<selected_theme>', methods=['GET', 'POST'])
def set_theme(selected_theme):
    global default_theme
    default_theme = selected_theme
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
