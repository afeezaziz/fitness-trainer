from flask import Flask, render_template, redirect, url_for, session, request, flash
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from app.models import db, User, FoodLog, CalorieEntry, ExerciseLog, init_db
import os
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='/app/templates', static_folder='/app/static')

# Add offline page route
@app.route('/offline')
def offline():
    return render_template('offline.html')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fitness.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Fix redirect URI for HTTPS behind reverse proxy
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

# Initialize database
db.init_app(app)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

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
    return User.query.get(session['user_id'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/food')
@login_required
def food():
    user = get_current_user()
    today_food = FoodLog.query.filter(
        FoodLog.user_id == user.id,
        db.func.date(FoodLog.meal_time) == date.today()
    ).order_by(FoodLog.meal_time.desc()).all()
    return render_template('food.html', food_logs=today_food)

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

    food_log = FoodLog(
        user_id=user.id,
        meal_type=meal_type,
        food_name=food_name,
        portion_size=portion_size,
        meal_time=meal_time,
        notes=request.form.get('notes', '')
    )

    db.session.add(food_log)
    db.session.commit()
    flash('Food logged successfully!', 'success')
    return redirect(url_for('food'))

@app.route('/calories')
@login_required
def calories():
    user = get_current_user()
    today_calories = CalorieEntry.query.filter(
        CalorieEntry.user_id == user.id,
        db.func.date(CalorieEntry.entry_time) == date.today()
    ).order_by(CalorieEntry.entry_time.desc()).all()

    total_calories = sum(entry.calories for entry in today_calories)
    daily_goal = 2000  # This could be user-configurable later

    return render_template('calories.html',
                         calorie_entries=today_calories,
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

    calorie_entry = CalorieEntry(
        user_id=user.id,
        food_item=food_item,
        calories=calories,
        quantity=quantity,
        notes=request.form.get('notes', '')
    )

    db.session.add(calorie_entry)
    db.session.commit()
    flash('Calories logged successfully!', 'success')
    return redirect(url_for('calories'))

@app.route('/exercise')
@login_required
def exercise():
    user = get_current_user()
    today_exercise = ExerciseLog.query.filter(
        ExerciseLog.user_id == user.id,
        db.func.date(ExerciseLog.workout_time) == date.today()
    ).order_by(ExerciseLog.workout_time.desc()).all()

    # Calculate weekly stats
    week_start = date.today().replace(day=1)  # Simple: start of month
    week_exercises = ExerciseLog.query.filter(
        ExerciseLog.user_id == user.id,
        ExerciseLog.workout_time >= week_start
    ).all()

    total_workouts = len(set(ex.workout_time.date() for ex in week_exercises))
    total_sets = sum(ex.sets for ex in week_exercises)
    total_reps = sum(ex.reps for ex in week_exercises)
    max_weight = max((ex.weight for ex in week_exercises if ex.weight), default=0)

    return render_template('exercise.html',
                         exercise_logs=today_exercise,
                         stats={
                             'workouts': total_workouts,
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

    exercise_log = ExerciseLog(
        user_id=user.id,
        exercise_name=exercise_name,
        exercise_type=exercise_type,
        sets=sets,
        reps=reps,
        weight=weight,
        workout_time=workout_time,
        notes=request.form.get('notes', '')
    )

    db.session.add(exercise_log)
    db.session.commit()
    flash('Exercise logged successfully!', 'success')
    return redirect(url_for('exercise'))

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    if not user_info:
        # Fallback to using userinfo endpoint
        resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo')
        user_info = resp.json()

    # Find or create user in database
    user = User.query.filter_by(google_id=user_info['sub']).first()
    if not user:
        user = User.query.filter_by(email=user_info['email']).first()

    if not user:
        # Create new user
        user = User(
            google_id=user_info['sub'],
            email=user_info['email'],
            name=user_info.get('name', ''),
            profile_picture=user_info.get('picture')
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
    else:
        # Update existing user with new data
        user.google_id = user_info['sub']
        user.name = user_info.get('name', '')
        user.profile_picture = user_info.get('picture')
        db.session.commit()

    session['user_id'] = user.id
    session['email'] = user.email
    session['name'] = user.name
    session['user'] = user_info

    flash(f'Welcome back, {user.name}!', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# Initialize database on startup
def create_tables():
    with app.app_context():
        init_db()

# Create tables when app is created
create_tables()

if __name__ == '__main__':
    app.run(debug=True, port=8081)