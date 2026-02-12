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
    c.execute('''CREATE TABLE IF NOT EXISTS workout_blocks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  program_id INTEGER NOT NULL,
                  FOREIGN KEY (program_id) REFERENCES programs(id))''')
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

def get_program_by_id(program_id):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM programs WHERE id = ?', (program_id,))
    program = c.fetchone()
    conn.close()
    return program

def get_blocks_by_program(program_id):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM workout_blocks WHERE program_id = ? ORDER BY id ASC', (program_id,))
    blocks = c.fetchall()
    conn.close()
    return blocks

def add_workout_block(name, program_id):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('INSERT INTO workout_blocks (name, program_id) VALUES (?, ?)', (name.strip(), program_id))
    conn.commit()
    conn.close()

def delete_program(program_id):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    # First delete all workout blocks associated with this program
    c.execute('DELETE FROM workout_blocks WHERE program_id = ?', (program_id,))
    # Then delete the program
    c.execute('DELETE FROM programs WHERE id = ?', (program_id,))
    conn.commit()
    conn.close()

def delete_exercise(exercise_id):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('DELETE FROM exercises WHERE id = ?', (exercise_id,))
    conn.commit()
    conn.close()

def delete_workout_block(block_id):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('DELETE FROM workout_blocks WHERE id = ?', (block_id,))
    conn.commit()
    conn.close()

def update_program(program_id, new_name):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('UPDATE programs SET name = ? WHERE id = ?', (new_name.strip(), program_id))
    conn.commit()
    conn.close()

def update_exercise(exercise_id, new_name):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('UPDATE exercises SET name = ? WHERE id = ?', (new_name.strip(), exercise_id))
    conn.commit()
    conn.close()

def update_workout_block(block_id, new_name):
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('UPDATE workout_blocks SET name = ? WHERE id = ?', (new_name.strip(), block_id))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/programs')
def programs():
    programs_list = get_all_programs()
    return render_template('programs.html', programs=programs_list)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        program_name = request.form.get('name', '').strip()
        if program_name:
            add_program(program_name)
        return redirect(url_for('programs'))
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

@app.route('/view_program/<int:program_id>')
def view_program(program_id):
    program = get_program_by_id(program_id)
    if not program:
        flash('Program not found.', 'error')
        return redirect(url_for('programs'))
    blocks = get_blocks_by_program(program_id)
    return render_template('view_program.html', program=program, blocks=blocks)

@app.route('/add_block/<int:program_id>', methods=['GET', 'POST'])
def add_block(program_id):
    program = get_program_by_id(program_id)
    if not program:
        flash('Program not found.', 'error')
        return redirect(url_for('programs'))
    
    if request.method == 'POST':
        block_name = request.form.get('name', '').strip()
        if not block_name:
            flash('Block name cannot be empty.', 'error')
            return render_template('add_block.html', program=program)
        
        add_workout_block(block_name, program_id)
        return redirect(url_for('view_program', program_id=program_id))
    else:
        return render_template('add_block.html', program=program)

@app.route('/delete_program/<int:program_id>', methods=['POST'])
def delete_program_route(program_id):
    delete_program(program_id)
    flash('Program deleted successfully.', 'success')
    return redirect(url_for('programs'))

@app.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
def delete_exercise_route(exercise_id):
    delete_exercise(exercise_id)
    flash('Exercise deleted successfully.', 'success')
    return redirect(url_for('exercises'))

@app.route('/delete_block/<int:block_id>', methods=['POST'])
def delete_block_route(block_id):
    # Get program_id before deleting to redirect back
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('SELECT program_id FROM workout_blocks WHERE id = ?', (block_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        program_id = result[0]
        delete_workout_block(block_id)
        flash('Workout block deleted successfully.', 'success')
        return redirect(url_for('view_program', program_id=program_id))
    else:
        flash('Block not found.', 'error')
        return redirect(url_for('programs'))

@app.route('/edit_program/<int:program_id>', methods=['POST'])
def edit_program_route(program_id):
    new_name = request.form.get('name', '').strip()
    if not new_name:
        flash('Program name cannot be empty.', 'error')
        return redirect(url_for('programs'))
    
    update_program(program_id, new_name)
    flash('Program updated successfully.', 'success')
    return redirect(url_for('programs'))

@app.route('/edit_exercise/<int:exercise_id>', methods=['POST'])
def edit_exercise_route(exercise_id):
    new_name = request.form.get('name', '').strip()
    
    if not new_name:
        flash('Exercise name cannot be empty.', 'error')
        return redirect(url_for('exercises'))
    
    if len(new_name) > 50:
        flash('Exercise name must be 50 characters or less.', 'error')
        return redirect(url_for('exercises'))
    
    # Check for duplicates (excluding current exercise)
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM exercises WHERE LOWER(name) = LOWER(?) AND id != ?', (new_name, exercise_id))
    count = c.fetchone()[0]
    conn.close()
    
    if count > 0:
        flash('An exercise with this name already exists.', 'error')
        return redirect(url_for('exercises'))
    
    update_exercise(exercise_id, new_name)
    flash('Exercise updated successfully.', 'success')
    return redirect(url_for('exercises'))

@app.route('/edit_block/<int:block_id>', methods=['POST'])
def edit_block_route(block_id):
    new_name = request.form.get('name', '').strip()
    if not new_name:
        flash('Block name cannot be empty.', 'error')
        # Get program_id to redirect back
        conn = sqlite3.connect('programs.db')
        c = conn.cursor()
        c.execute('SELECT program_id FROM workout_blocks WHERE id = ?', (block_id,))
        result = c.fetchone()
        conn.close()
        if result:
            return redirect(url_for('view_program', program_id=result[0]))
        return redirect(url_for('programs'))
    
    # Get program_id before updating to redirect back
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('SELECT program_id FROM workout_blocks WHERE id = ?', (block_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        program_id = result[0]
        update_workout_block(block_id, new_name)
        flash('Workout block updated successfully.', 'success')
        return redirect(url_for('view_program', program_id=program_id))
    else:
        flash('Block not found.', 'error')
        return redirect(url_for('programs'))

if __name__ == '__main__':
    init_db()
    app.run(host='localhost', port=3000, debug=True)
