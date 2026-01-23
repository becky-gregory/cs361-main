from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database functions
def init_db():
    conn = sqlite3.connect('programs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS programs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL)''')
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

if __name__ == '__main__':
    init_db()
    app.run(host='localhost', port=3000, debug=True)
