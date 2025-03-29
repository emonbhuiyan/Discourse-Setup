from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
#from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import subprocess
import sys
from io import StringIO
import database as db
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'dev-secret-key'

# # Web application admin credentials
# WEBAPP_ADMIN_USERNAME = os.getenv('WEBAPP_ADMIN_USERNAME', 'admin')
# WEBAPP_ADMIN_PASSWORD_HASH = os.getenv('WEBAPP_ADMIN_PASSWORD_HASH')
# if not WEBAPP_ADMIN_PASSWORD_HASH:
#     WEBAPP_ADMIN_PASSWORD_HASH = generate_password_hash('Kashem420')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_config():
    """Read current config.py and parse into a dictionary"""
    config = {
        'OCCUPATION': '',
        'API_KEY': '',
        'ADMIN_USERNAME': '',
        'CATEGORIES': {},
        'topics': []
    }
    
    try:
        with open('config.py', 'r') as f:
            content = f.read()
            
            # Simple parsing of config.py
            for line in content.split('\n'):
                if line.startswith('OCCUPATION ='):
                    config['OCCUPATION'] = line.split('=')[1].strip().strip('"\'')
                elif line.startswith('API_KEY ='):
                    config['API_KEY'] = line.split('=')[1].strip().strip('"\'')
                elif line.startswith('ADMIN_USERNAME ='):
                    config['ADMIN_USERNAME'] = line.split('=')[1].strip().strip('"\'')
                elif line.startswith('CATEGORIES ='):
                    # This is simplified - actual parsing would need to handle the dictionary
                    pass
                elif line.strip().startswith('("') and 'topics =' in content:
                    # Simple topic parsing
                    parts = line.strip().strip('(),').split('", "')
                    if len(parts) == 3:
                        config['topics'].append([
                            parts[0].strip('"'),
                            parts[1].strip('"'),
                            parts[2].strip('"')
                        ])
    except FileNotFoundError:
        # Create empty config if it doesn't exist
        with open('config.py', 'w') as f:
            f.write('OCCUPATION = ""\n')
            f.write('API_KEY = ""\n')
            f.write('ADMIN_USERNAME = ""\n')
            f.write('CATEGORIES = {}\n')
            f.write('topics = []\n')
    
    # Parse categories more thoroughly
    try:
        namespace = {}
        exec(content, namespace)
        config['CATEGORIES'] = namespace.get('CATEGORIES', {})
    except:
        pass
        
    return config

@app.route('/')
@login_required
def dashboard():
    history = db.get_execution_history()
    config = get_current_config()
    return render_template('dashboard.html', history=history, config=config)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if (username == os.getenv('WEBAPP_ADMIN_USERNAME') and 
            password == os.getenv('WEBAPP_ADMIN_PASSWORD')):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/configure', methods=['GET', 'POST'])
@login_required
def configure():
    if request.method == 'POST':
        # Save configuration to config.py
        with open('config.py', 'w') as f:
            f.write(f"OCCUPATION = \"{request.form['occupation']}\"\n")
            f.write(f"API_KEY = \"{request.form['api_key']}\"\n")
            f.write(f"ADMIN_USERNAME = \"{request.form['admin_username']}\"\n")
            
            # Process categories (from either individual fields or raw input)
            f.write("CATEGORIES = {\n")
            if request.form.get('categories_raw'):
                try:
                    categories = eval(request.form['categories_raw'])
                    for name, desc in categories.items():
                        f.write(f"    \"{name}\": \"{desc}\",\n")
                except:
                    pass  # Fall back to individual fields
            else:
                category_names = request.form.getlist('category_name[]')
                category_descs = request.form.getlist('category_desc[]')
                for name, desc in zip(category_names, category_descs):
                    if name.strip():
                        f.write(f"    \"{name}\": \"{desc}\",\n")
            
            f.write("}\n\n")
            
            # Process topics (from either individual fields or raw input)
            f.write("topics = [\n")
            if request.form.get('topics_raw'):
                try:
                    topics = eval(request.form['topics_raw'])
                    for cat, title, content in topics:
                        f.write(f"    (\"{cat}\", \"{title}\", \"{content}\"),\n")
                except:
                    pass  # Fall back to individual fields
            else:
                topic_categories = request.form.getlist('topic_category[]')
                topic_titles = request.form.getlist('topic_title[]')
                topic_contents = request.form.getlist('topic_content[]')
                for cat, title, content in zip(topic_categories, topic_titles, topic_contents):
                    if title.strip():
                        f.write(f"    (\"{cat}\", \"{title}\", \"{content}\"),\n")
            f.write("]\n")
            
        flash('Configuration saved successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Read current configuration
    config = get_current_config()
    return render_template('configure.html', 
                         occupation=config['OCCUPATION'],
                         api_key=config['API_KEY'],
                         admin_username=config['ADMIN_USERNAME'],
                         categories=config['CATEGORIES'],
                         topics=config['topics'])

@app.route('/run_script/<script_name>')
@login_required
def run_script(script_name):
    return render_template('run_script.html', script_name=script_name)

@app.route('/execute_script/<script_name>')
@login_required
def execute_script(script_name):
    # Get current occupation from config
    config = get_current_config()
    occupation = config['OCCUPATION']
    
    # Determine which script to run
    if script_name == 'setup':
        script_path = 'setup.py'
    elif script_name == 'category':
        script_path = 'category.py'
    elif script_name == 'bulk_post':
        script_path = 'bulk_post.py'
    else:
        return jsonify({'error': 'Invalid script name'})
    
    try:
        # Execute the script and capture output
        process = subprocess.Popen(['python', script_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Stream the output
        def generate():
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    yield output
            yield "\nScript execution completed!"
            
            # Log successful execution
            db.log_execution(script_name, occupation, "completed")
        
        return app.response_class(generate(), mimetype='text/plain')
        
    except Exception as e:
        db.log_execution(script_name, occupation, "failed")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    db.init_db()
    # Ensure config.py exists
    get_current_config()
    app.run(debug=True)