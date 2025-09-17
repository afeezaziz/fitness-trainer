from flask import Flask, render_template, redirect, url_for, session, request, flash
from authlib.integrations.flask_client import OAuth
import os
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Simple in-memory storage for demo (will be replaced with database)
users_db = {}
food_logs_db = {}
calorie_entries_db = {}
exercise_logs_db = {}

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to access this page.', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_current_user():
    if 'user_id' not in session:
        return None
    return users_db.get(session['user_id'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    if not user_info:
        resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo')
        user_info = resp.json()

    user_id = user_info['sub']
    if user_id not in users_db:
        users_db[user_id] = {
            'id': user_id,
            'email': user_info['email'],
            'name': user_info.get('name', ''),
            'picture': user_info.get('picture')
        }
        flash('Account created successfully!', 'success')
    else:
        users_db[user_id].update({
            'name': user_info.get('name', ''),
            'picture': user_info.get('picture')
        })

    session['user_id'] = user_id
    session['email'] = user_info['email']
    session['name'] = users_db[user_id]['name']
    session['user'] = user_info

    flash(f'Welcome back, {users_db[user_id]["name"]}!', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/food')
@login_required
def food():
    user = get_current_user()
    user_food = food_logs_db.get(user['id'], [])
    return render_template('food.html', food_logs=user_food)

@app.route('/add_food', methods=['POST'])
@login_required
def add_food():
    user = get_current_user()
    meal_type = request.form.get('meal-type')
    food_name = request.form.get('food-name')
    portion_size = request.form.get('portion-size')
    meal_time_str = request.form.get('meal-time')

    if not all([meal_type, food_name, portion_size, meal_time_str]):
        flash('All fields are required.', 'error')
        return redirect(url_for('food'))

    try:
        meal_time = datetime.fromisoformat(meal_time_str.replace('T', ' '))
    except ValueError:
        meal_time = datetime.now()

    if user['id'] not in food_logs_db:
        food_logs_db[user['id']] = []

    food_log = {
        'id': len(food_logs_db[user['id']]) + 1,
        'meal_type': meal_type,
        'food_name': food_name,
        'portion_size': portion_size,
        'meal_time': meal_time,
        'notes': request.form.get('notes', '')
    }

    food_logs_db[user['id']].append(food_log)
    flash('Food logged successfully!', 'success')
    return redirect(url_for('food'))

@app.route('/calories')
@login_required
def calories():
    user = get_current_user()
    user_calories = calorie_entries_db.get(user['id'], [])
    total_calories = sum(entry['calories'] for entry in user_calories)
    daily_goal = 2000

    return render_template('calories.html',
                         calorie_entries=user_calories,
                         total_calories=total_calories,
                         daily_goal=daily_goal)

@app.route('/add_calories', methods=['POST'])
@login_required
def add_calories():
    user = get_current_user()
    food_item = request.form.get('food-item')
    calories = request.form.get('calories')
    quantity = request.form.get('quantity')

    if not all([food_item, calories, quantity]):
        flash('All fields are required.', 'error')
        return redirect(url_for('calories'))

    try:
        calories = int(calories)
    except ValueError:
        flash('Calories must be a number.', 'error')
        return redirect(url_for('calories'))

    if user['id'] not in calorie_entries_db:
        calorie_entries_db[user['id']] = []

    calorie_entry = {
        'id': len(calorie_entries_db[user['id']]) + 1,
        'food_item': food_item,
        'calories': calories,
        'quantity': quantity,
        'entry_time': datetime.now(),
        'notes': request.form.get('notes', '')
    }

    calorie_entries_db[user['id']].append(calorie_entry)
    flash('Calories logged successfully!', 'success')
    return redirect(url_for('calories'))

@app.route('/exercise')
@login_required
def exercise():
    user = get_current_user()
    user_exercises = exercise_logs_db.get(user['id'], [])

    # Calculate simple stats
    total_sets = sum(ex['sets'] for ex in user_exercises)
    total_reps = sum(ex['reps'] for ex in user_exercises)
    max_weight = max((ex['weight'] for ex in user_exercises if ex.get('weight')), default=0)

    return render_template('exercise.html',
                         exercise_logs=user_exercises,
                         stats={
                             'workouts': len(set(ex['workout_time'].date() for ex in user_exercises)),
                             'sets': total_sets,
                             'reps': total_reps,
                             'max_weight': max_weight
                         })

@app.route('/add_exercise', methods=['POST'])
@login_required
def add_exercise():
    user = get_current_user()
    exercise_name = request.form.get('exercise-name')
    exercise_type = request.form.get('exercise-type')
    sets = request.form.get('sets')
    reps = request.form.get('reps')
    weight = request.form.get('weight')
    workout_time_str = request.form.get('workout-time')

    if not all([exercise_name, exercise_type, sets, reps, workout_time_str]):
        flash('All fields except weight are required.', 'error')
        return redirect(url_for('exercise'))

    try:
        sets = int(sets)
        reps = int(reps)
        weight = float(weight) if weight else None
        workout_time = datetime.fromisoformat(workout_time_str.replace('T', ' '))
    except ValueError as e:
        flash(f'Invalid input: {str(e)}', 'error')
        return redirect(url_for('exercise'))

    if user['id'] not in exercise_logs_db:
        exercise_logs_db[user['id']] = []

    exercise_log = {
        'id': len(exercise_logs_db[user['id']]) + 1,
        'exercise_name': exercise_name,
        'exercise_type': exercise_type,
        'sets': sets,
        'reps': reps,
        'weight': weight,
        'workout_time': workout_time,
        'notes': request.form.get('notes', '')
    }

    exercise_logs_db[user['id']].append(exercise_log)
    flash('Exercise logged successfully!', 'success')
    return redirect(url_for('exercise'))

if __name__ == '__main__':
    app.run(debug=True, port=8081)