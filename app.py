from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import speech_recognition as sr

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# Themes configuration
themes = {
    'theme1': 'main.css',
    'theme2': 'theme2.css',
    'theme3': 'theme3.css',
    'theme4': 'theme4.css'
}

# Default theme
default_theme = 'theme1'

# Initialize speech recognition
r = sr.Recognizer()

# Global variable for speech mode
speech_mode = False

# Set the energy threshold for speech recognition
r.energy_threshold = 500

# Define Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300))
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<Task %r>' % self.id

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "Error while adding task"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks, theme=themes.get(default_theme))


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "Error deleting task"


@app.route('/completed/<int:id>')
def complete(id):
    task_completed = Todo.query.get_or_404(id)
    task_completed.completed = True
    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Error completing task"


@app.route('/not-completed/<int:id>')
def not_complete(id):
    task_not_completed = Todo.query.get_or_404(id)
    task_not_completed.completed = False
    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Error marking task as not completed"


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        task.completed = False  # Resetting completion status when updating
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Error updating task"
    else:
        return render_template('update.html', task=task, theme=themes.get(default_theme))


@app.route('/mic_on/', methods=['GET', 'POST'])
def mic_on():
    global speech_mode
    if not speech_mode:
        speech_mode = True
        return render_template('speechmode.html', instruction="Speak a command...", theme=themes.get(default_theme))
    else:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=4,phrase_time_limit=7)  # Timeout after 4 seconds of silence
                print("Processing...")

            text = r.recognize_google(audio)
            print("Recognized:", text)

            if "quit" in text.lower():
                speech_mode = False
                return redirect('/mic_off')

            elif "create" in text.lower():
                # Extract task content from speech
                task_content = extract_task_content(text)
                new_task = Todo(content=task_content)
                try:
                    db.session.add(new_task)
                    db.session.commit()
                    return redirect('/mic_off')
                except Exception as e:
                    return f"Error while adding task: {str(e)}"

            elif "update" in text.lower():
                task,updated_text = find_task_to_update(text)
                if request.method == 'POST':
                    task.content = updated_text
                    task.completed = False  # Resetting completion status when updating
                    try:
                        db.session.commit()
                        return redirect('/')
                    except:
                        return "Error updating task"
                else:
                    return redirect('/')

            elif "delete" in text.lower():
                task_to_delete = find_task_to_delete(text)
                if task_to_delete:
                    try:
                        db.session.delete(task_to_delete)
                        db.session.commit()
                        return redirect('/mic_off')
                    except Exception as e:
                        return f"Error deleting task: {str(e)}"
                else:
                    speech_mode=False
                    return "Task not found."

            elif "complete" in text.lower():
                if "not complete" in text.lower():
                    print("never here")
                    task_to_not_complete = find_task_to_not_complete(text)

                    if task_to_not_complete:
                        print("here is problme")
                        task_to_not_complete.completed = False
                        try:
                            print("i came so what")
                            db.session.commit()
                            return redirect('/mic_off')
                        except Exception as e:
                            return f"Error marking task as not completed: {str(e)}"
                    else:
                        speech_mode = False
                        return "Task not found."

                task_to_complete = find_task_to_complete(text)
                if task_to_complete:
                    task_to_complete.completed = True
                    try:
                        db.session.commit()
                        return redirect('/mic_off')
                    except Exception as e:
                        return f"Error completing task: {str(e)}"
                else:
                    speech_mode = False
                    return "Task not found."



            elif "change theme" in text.lower():
                index = text.lower().find("change theme") + len("change theme")
                theme_no = text[index:].strip().split()[1]
                return redirect('/set-theme/theme'+theme_no)

            else:
                return render_template('speechmode.html', speech="Command not recognized.", action="Listening")

        except sr.WaitTimeoutError:
            print("No speech detected. Turning off speech mode...")
            speech_mode = False
            return redirect('/mic_off')

        except sr.UnknownValueError:
            return render_template('speechmode.html', speech="Could not understand audio.", action="Listening")

        except sr.RequestError as e:
            return render_template('speechmode.html', speech=f"Could not request results: {str(e)}", action="Listening")


@app.route('/mic_off/')
def mic_off():
    global speech_mode
    print("Speech mode turned off")
    speech_mode = False
    return redirect('/')


@app.route('/set-theme/<theme>', methods=['GET','POST'])
def set_theme_particular(theme):
    if theme in themes:
        global default_theme
        default_theme = theme
        return redirect('/')
    else:
        return "Invalid theme selection"


@app.route('/set_theme/', methods=['GET'])
def set_theme():
    return render_template('set_theme.html')


# Helper functions for speech recognition
def extract_task_content(text):
    keyword = "create a task"
    index = text.lower().find(keyword) + len(keyword)
    return text[index:].strip()


def find_task_to_update(text):
    try:
        keyword = "update task"
        index = text.lower().find(keyword) + len(keyword)
        task_num = int(text[index:].strip().split()[0])
        updated_text = text[index + 2:].strip()

        # Retrieve tasks ordered by date_created
        tasks = Todo.query.order_by(Todo.date_created).all()

        if 0 < task_num <= len(tasks):
            return tasks[task_num - 1],updated_text  # Adjust index to start from 1

        return None

    except Exception as e:
        print(f"Error finding task: {str(e)}")
        return None


def find_task_to_delete(text):
    try:
        keyword = "delete task"
        index = text.lower().find(keyword) + len(keyword)
        task_num = int(text[index:].strip().split()[0])

        # Retrieve tasks ordered by date_created
        tasks = Todo.query.order_by(Todo.date_created).all()

        if 0 < task_num <= len(tasks):
            return tasks[task_num - 1]  # Adjust index to start from 1

        return None

    except Exception as e:
        print(f"Error finding task: {str(e)}")
        return None


def find_task_to_complete(text):
    try:
        keyword = "complete task"
        index = text.lower().find(keyword) + len(keyword)
        task_num = int(text[index:].strip().split()[0])

        # Retrieve tasks ordered by date_created
        tasks = Todo.query.order_by(Todo.date_created).all()

        if 0 < task_num <= len(tasks):
            return tasks[task_num - 1]  # Adjust index to start from 1

        return None

    except Exception as e:
        print(f"Error finding task: {str(e)}")
        return None


def find_task_to_not_complete(text):
    try:
        keyword = "not complete task"
        index = text.lower().find(keyword) + len(keyword)
        task_num = int(text[index:].strip().split()[0])

        # Retrieve tasks ordered by date_created
        tasks = Todo.query.order_by(Todo.date_created).all()

        if 0 < task_num <= len(tasks):
            return tasks[task_num - 1]  # Adjust index to start from 1
        print("here i am returning none")
        return None

    except Exception as e:
        print(f"Error finding task: {str(e)}")
        return None


if __name__ == "__main__":
    app.run(debug=True)
