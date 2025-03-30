from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import subprocess
import sys
from io import StringIO
import database as db
import time
import os
from dotenv import load_dotenv
import ast  # For safely parsing Python literals
from flask import Flask #USED FOR GITHUB PAGES
from flask_frozen import Freezer #USED FOR GITHUB PAGES

# Load environment variables
load_dotenv()

app = Flask(__name__)
freezer = Freezer(app) #USED FOR GITHUB PAGES
app.secret_key = os.getenv('SECRET_KEY') or 'dev-secret-key'

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
        'topics': [],
        'GOOGLE_CLIENT_ID': '',
        'GOOGLE_CLIENT_SECRET': '',
        'GTM_ID': ''
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
                elif line.startswith('GOOGLE_CLIENT_ID ='):
                    config['GOOGLE_CLIENT_ID'] = line.split('=')[1].strip().strip('"\'')
                elif line.startswith('GOOGLE_CLIENT_SECRET ='):
                    config['GOOGLE_CLIENT_SECRET'] = line.split('=')[1].strip().strip('"\'')
                elif line.startswith('GTM_ID ='):
                    config['GTM_ID'] = line.split('=')[1].strip().strip('"\'')
                
    except FileNotFoundError:
        # Create empty config if it doesn't exist
        with open('config.py', 'w') as f:
            f.write('OCCUPATION = ""\n')
            f.write('API_KEY = ""\n')
            f.write('ADMIN_USERNAME = ""\n')
            f.write('CATEGORIES = {}\n')
            f.write('topics = []\n')
            f.write('GOOGLE_CLIENT_ID = ""\n')
            f.write('GOOGLE_CLIENT_SECRET = ""\n')
            f.write('GTM_ID = ""\n')
    
    # Parse categories and topics safely
    try:
        namespace = {'OCCUPATION': '', 'CATEGORIES': {}, 'topics': []}
        exec(content, namespace)
        config['CATEGORIES'] = namespace.get('CATEGORIES', {})
        config['topics'] = namespace.get('topics', [])
    except Exception as e:
        print(f"Error parsing config: {e}")
        
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

def validate_google_credentials(client_id, client_secret):
    """Basic validation for Google credentials"""
    if not client_id or not client_secret:
        return False
    # Google Client IDs typically end with .apps.googleusercontent.com
    if not client_id.endswith('.apps.googleusercontent.com'):
        flash('Invalid Google Client ID format', 'danger')
        return False
    return True

@app.route('/configure', methods=['GET', 'POST'])
@login_required
def configure():
    if request.method == 'POST':
        # Validate Google credentials first
        google_client_id = request.form.get('google_client_id', '').strip()
        google_client_secret = request.form.get('google_client_secret', '').strip()
        gtm_id = request.form.get('gtm_id', '').strip()
        
        if not validate_google_credentials(google_client_id, google_client_secret):
            return redirect(url_for('configure'))
        
        # Validate GTM ID format if provided
        if gtm_id and not gtm_id.startswith('GTM-'):
            flash('GTM ID must start with "GTM-"', 'warning')
            return redirect(url_for('configure'))
        
        # Save configuration to config.py
        with open('config.py', 'w') as f:
            # Core configuration
            f.write(f"OCCUPATION = \"{request.form['occupation']}\"\n")
            f.write(f"API_KEY = \"{request.form['api_key']}\"\n")
            f.write(f"ADMIN_USERNAME = \"{request.form['admin_username']}\"\n")
            
            # Google configuration
            f.write(f"GOOGLE_CLIENT_ID = \"{google_client_id}\"\n")
            f.write(f"GOOGLE_CLIENT_SECRET = \"{google_client_secret}\"\n")
            f.write(f"GTM_ID = \"{gtm_id}\"\n")
            
            # Process categories
            f.write("CATEGORIES = {\n")
            if request.form.get('categories_raw'):
                try:
                    # Safely evaluate the dictionary input
                    categories = ast.literal_eval(request.form['categories_raw'])
                    if isinstance(categories, dict):
                        for name, desc in categories.items():
                            f.write(f"    \"{name}\": \"{desc}\",\n")
                except (ValueError, SyntaxError) as e:
                    flash(f'Error parsing categories: {str(e)}', 'danger')
            else:
                category_names = request.form.getlist('category_name[]')
                category_descs = request.form.getlist('category_desc[]')
                for name, desc in zip(category_names, category_descs):
                    if name.strip():
                        f.write(f"    \"{name}\": \"{desc}\",\n")
            f.write("}\n\n")
            
            # Process topics
            f.write("topics = [\n")
            if request.form.get('topics_raw'):
                try:
                    topics = ast.literal_eval(request.form['topics_raw'])
                    if isinstance(topics, list):
                        for topic in topics:
                            if len(topic) == 3:
                                f.write(f"    (\"{topic[0]}\", \"{topic[1]}\", \"{topic[2]}\"),\n")
                except (ValueError, SyntaxError) as e:
                    flash(f'Error parsing topics: {str(e)}', 'danger')
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
                         google_client_id=config['GOOGLE_CLIENT_ID'],
                         google_client_secret=config['GOOGLE_CLIENT_SECRET'],
                         gtm_id=config['GTM_ID'],
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
    app.run(host='0.0.0.0', port=5000, debug=True)



# ...ADDED FOR GITHUB PAGES_)
# Freezer configuration
@freezer.register_generator
def url_generator():
    # Add all dynamic routes here if needed
    yield "/"
    yield "/login"
    yield "/dashboard"
    yield "/logout"
    yield "/configure"
    yield "/run_script/<script_name>"
    yield "/execute_script/<script_name>"

if __name__ == "freeze":
    freezer.freeze()