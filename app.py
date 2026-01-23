from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Needed for flash messages

# Database functions
def init_db():
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS programs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS exercises
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL UNIQUE)''')
    conn.commit()
    conn.close()

def get_all_programs():
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM programs ORDER BY name ASC')
    programs = c.fetchall()
    conn.close()
    return programs

def add_program(name):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('INSERT INTO programs (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def get_all_exercises():
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM exercises ORDER BY name ASC')
    exercises = c.fetchall()
    conn.close()
    return exercises

def exercise_exists(name):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM exercises WHERE LOWER(name) = LOWER(?)', (name.strip(),))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def add_exercise(name):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('INSERT INTO exercises (name) VALUES (?)', (name.strip(),))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    programs = get_all_programs()
    return render_template('index.html', programs=programs)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        program_name = request.form.get('name', '').strip()
        if program_name:
            add_program(program_name)
        return redirect(url_for('index'))
    else:
        return render_template('add_program.html')

@app.route('/exercises')
def exercises():
    exercises_list = get_all_exercises()
    return render_template('exercises.html', exercises=exercises_list)

@app.route('/add_exercise', methods=['GET', 'POST'])
def add_exercise_route():
    if request.method == 'POST':
        exercise_name = request.form.get('name', '').strip()
        
        # Validate length
        if len(exercise_name) > 50:
            flash('Exercise name must be 50 characters or less.', 'error')
            return render_template('add_exercise.html')
        
        # Check if empty
        if not exercise_name:
            flash('Exercise name cannot be empty.', 'error')
            return render_template('add_exercise.html')
        
        # Check for duplicates (case-insensitive)
        if exercise_exists(exercise_name):
            flash('An exercise with this name already exists.', 'error')
            return render_template('add_exercise.html')
        
        # Add exercise
        add_exercise(exercise_name)
        return redirect(url_for('exercises'))
    else:
        return render_template('add_exercise.html')

if __name__ == '__main__':
    init_db()
    app.run(host='localhost', port=3000, debug=True)
