from flask import Flask, render_template, redirect, url_for, session, request, flash
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from app.models import db, User, FoodLog, CalorieEntry, ExerciseLog, ChatRoom, ChatMessage, ChatParticipant, ExerciseSetLog, UserExerciseTarget, EnergyBurnEntry, UserProfile, init_db
from app.exercises import EXERCISE_DATABASE, get_workout_plan, get_all_exercises
from app.chat import init_chat
import os
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

def create_app():
    # Resolve template/static directories to work in both Docker (/app) and local dev
    container_tpl = '/app/templates'
    container_static = '/app/static'
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    local_tpl = os.path.join(base_dir, 'templates')
    local_static = os.path.join(base_dir, 'static')

    template_folder = container_tpl if os.path.isdir(container_tpl) else local_tpl
    static_folder = container_static if os.path.isdir(container_static) else local_static

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

    # Configuration
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database configuration - prioritize MariaDB for production
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Default to MariaDB if DATABASE_URL is not set
        database_url = 'mariadb+pymysql://mariadb:Re1QMoc6bQUHAZqN1YmtCWjuHI3pelPyE6GsIr3JrKWb91dKZwt0Y35rp4ZfljbG@104.248.150.75:33005/default'

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    db.init_app(app)

    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    # Fix redirect URI for HTTPS behind reverse proxy
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    # OAuth setup
    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    # Initialize chat handlers
    init_chat(socketio)

    return app, google, socketio

app, google, socketio = create_app()

# Add offline page route
@app.route('/offline')
def offline():
    return render_template('offline.html')

# Add debug route for database connection
@app.route('/debug/db')
def debug_db():
    try:
        # Test database connection
        with db.engine.connect() as conn:
            result = conn.execute(db.text('SELECT 1 as test'))
            test_result = result.fetchone()

        # Count users
        user_count = User.query.count()

        # Get current session info
        session_info = {
            'user_id': session.get('user_id'),
            'email': session.get('email'),
            'name': session.get('name')
        }

        return {
            'database_connection': 'OK',
            'test_query': test_result[0] if test_result else None,
            'user_count': user_count,
            'session': session_info,
            'database_url': app.config['SQLALCHEMY_DATABASE_URI']
        }
    except Exception as e:
        return {
            'database_connection': 'ERROR',
            'error': str(e),
            'database_url': app.config['SQLALCHEMY_DATABASE_URI']
        }

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to access this page.', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Add settings page route
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')


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

    # Energy burned today (NEAT/Cardio/Exercise)
    today_burns = EnergyBurnEntry.query.filter(
        EnergyBurnEntry.user_id == user.id,
        db.func.date(EnergyBurnEntry.entry_time) == date.today()
    ).order_by(EnergyBurnEntry.entry_time.desc()).all()

    total_calories = sum(entry.calories for entry in today_calories)
    burned_calories = sum(b.calories_burned for b in today_burns)

    # Daily goal from profile if available
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    daily_goal = profile.daily_calorie_goal if profile and profile.daily_calorie_goal else 2000
    net_calories = total_calories - burned_calories

    return render_template('calories.html',
                         calorie_entries=today_calories,
                         energy_burns=today_burns,
                         total_calories=total_calories,
                         burned_calories=burned_calories,
                         net_calories=net_calories,
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

# NEAT & Activity logging
@app.route('/neat')
@login_required
def neat():
    user = get_current_user()
    today_burns = EnergyBurnEntry.query.filter(
        EnergyBurnEntry.user_id == user.id,
        db.func.date(EnergyBurnEntry.entry_time) == date.today()
    ).order_by(EnergyBurnEntry.entry_time.desc()).all()
    return render_template('neat.html', energy_burns=today_burns)

@app.route('/add_neat', methods=['POST'])
@login_required
def add_neat():
    user = get_current_user()
    source = request.form.get('source') or 'neat'
    activity_name = request.form.get('activity-name')
    calories_burned = request.form.get('calories-burned')
    duration = request.form.get('duration-minutes')
    entry_time_str = request.form.get('entry-time')
    notes = request.form.get('notes', '')

    if not all([activity_name, calories_burned]):
        flash('Activity and calories burned are required.', 'error')
        return redirect(url_for('neat'))

    try:
        calories_burned = int(calories_burned)
        duration_minutes = float(duration) if duration else None
        if entry_time_str:
            entry_time = datetime.fromisoformat(entry_time_str.replace('T', ' '))
        else:
            entry_time = datetime.now()
    except ValueError:
        flash('Invalid input for calories or duration.', 'error')
        return redirect(url_for('neat'))

    burn = EnergyBurnEntry(
        user_id=user.id,
        source=source,
        activity_name=activity_name,
        calories_burned=calories_burned,
        duration_minutes=duration_minutes,
        entry_time=entry_time,
        notes=notes
    )
    db.session.add(burn)
    db.session.commit()
    flash('Energy burn logged successfully!', 'success')
    return redirect(url_for('neat'))

@app.route('/exercise')
@login_required
def exercise():
    user = get_current_user()
    if user is None:
        flash('Session expired. Please log in again.', 'error')
        return redirect(url_for('login'))

    today_exercise = ExerciseLog.query.filter(
        ExerciseLog.user_id == user.id,
        db.func.date(ExerciseLog.workout_time) == date.today()
    ).order_by(ExerciseLog.workout_time.desc()).all()

    # Get previous exercises for quick copy
    previous_exercises = ExerciseLog.query.filter(
        ExerciseLog.user_id == user.id,
        ExerciseLog.workout_time < datetime.now()
    ).order_by(ExerciseLog.workout_time.desc()).limit(10).all()

    # Calculate monthly stats and trends (from start of current month)
    week_start = date.today().replace(day=1)  # Simple: start of month
    week_exercises = ExerciseLog.query.filter(
        ExerciseLog.user_id == user.id,
        ExerciseLog.workout_time >= week_start
    ).all()

    total_workouts = len(set(ex.workout_time.date() for ex in week_exercises))
    total_sets = sum(ex.sets for ex in week_exercises)
    total_reps = sum(ex.reps for ex in week_exercises)
    max_weight = max((ex.weight for ex in week_exercises if ex.weight), default=0)

    # New quantitative stats (prefer set-level if available)
    set_form_scores = []
    set_effort_scores = []
    set_quality_scores = []
    total_volume = 0
    for ex in week_exercises:
        if ex.sets_detail:
            for s in ex.sets_detail:
                if s.form_score is not None:
                    set_form_scores.append(s.form_score)
                if s.effort_score is not None:
                    set_effort_scores.append(s.effort_score)
                if s.quality_score is not None:
                    set_quality_scores.append(s.quality_score)
                if s.weight is not None:
                    try:
                        total_volume += (s.reps or 0) * float(s.weight)
                    except Exception:
                        pass
        else:
            # Fallback to exercise-level
            if ex.form_score is not None:
                set_form_scores.append(ex.form_score)
            if ex.effort_score is not None:
                set_effort_scores.append(ex.effort_score)
            if ex.form_score is not None and ex.effort_score is not None:
                set_quality_scores.append(ex.form_score * (ex.effort_score / 10.0))
            if ex.weight is not None:
                try:
                    total_volume += (ex.sets or 0) * (ex.reps or 0) * float(ex.weight)
                except Exception:
                    pass

    avg_form = round(sum(set_form_scores) / len(set_form_scores), 1) if set_form_scores else 0
    avg_effort = round(sum(set_effort_scores) / len(set_effort_scores), 1) if set_effort_scores else 0

    # Build trends per day for current month
    from datetime import timedelta
    day = week_start
    today = date.today()
    trend_labels = []
    trend_form = []
    trend_effort = []
    trend_quality = []
    trend_volume = []

    while day <= today:
        # Collect logs for this day
        day_logs = [ex for ex in week_exercises if ex.workout_time.date() == day]
        day_form, day_effort, day_quality, day_volume = [], [], [], 0
        for ex in day_logs:
            if ex.sets_detail:
                for s in ex.sets_detail:
                    if s.form_score is not None:
                        day_form.append(s.form_score)
                    if s.effort_score is not None:
                        day_effort.append(s.effort_score)
                    if s.quality_score is not None:
                        day_quality.append(s.quality_score)
                    if s.weight is not None:
                        try:
                            day_volume += (s.reps or 0) * float(s.weight)
                        except Exception:
                            pass
            else:
                if ex.form_score is not None:
                    day_form.append(ex.form_score)
                if ex.effort_score is not None:
                    day_effort.append(ex.effort_score)
                if ex.form_score is not None and ex.effort_score is not None:
                    day_quality.append(ex.form_score * (ex.effort_score / 10.0))
                if ex.weight is not None:
                    try:
                        day_volume += (ex.sets or 0) * (ex.reps or 0) * float(ex.weight)
                    except Exception:
                        pass
        trend_labels.append(day.strftime('%m/%d'))
        trend_form.append(round(sum(day_form) / len(day_form), 2) if day_form else None)
        trend_effort.append(round(sum(day_effort) / len(day_effort), 2) if day_effort else None)
        trend_quality.append(round(sum(day_quality) / len(day_quality), 2) if day_quality else None)
        trend_volume.append(int(day_volume))
        day += timedelta(days=1)

    # Targets adherence
    targets = UserExerciseTarget.query.filter_by(user_id=user.id).all()
    target_cards = []
    if targets:
        for t in targets:
            total_sets = 0
            meets = 0
            for ex in week_exercises:
                if ex.exercise_name == t.exercise_name:
                    if ex.sets_detail:
                        for s in ex.sets_detail:
                            total_sets += 1
                            ok_form = (t.min_form_score is None) or (s.form_score is not None and s.form_score >= t.min_form_score)
                            ok_effort = True
                            if t.effort_min is not None:
                                ok_effort = ok_effort and (s.effort_score is not None and s.effort_score >= t.effort_min)
                            if t.effort_max is not None:
                                ok_effort = ok_effort and (s.effort_score is not None and s.effort_score <= t.effort_max)
                            if ok_form and ok_effort:
                                meets += 1
                    else:
                        total_sets += ex.sets or 1
                        # Consider the whole exercise as a single check scaled by number of sets
                        ok_form = (t.min_form_score is None) or (ex.form_score is not None and ex.form_score >= t.min_form_score)
                        ok_effort = True
                        if t.effort_min is not None:
                            ok_effort = ok_effort and (ex.effort_score is not None and ex.effort_score >= t.effort_min)
                        if t.effort_max is not None:
                            ok_effort = ok_effort and (ex.effort_score is not None and ex.effort_score <= t.effort_max)
                        if ok_form and ok_effort:
                            meets += (ex.sets or 1)
            adherence = round((meets / total_sets) * 100, 1) if total_sets else 0
            target_cards.append({
                'exercise_name': t.exercise_name,
                'adherence': adherence,
                'min_form_score': t.min_form_score,
                'effort_min': t.effort_min,
                'effort_max': t.effort_max,
            })

    # Derived per-exercise (today) averages for display
    derived = {}
    for ex in today_exercise:
        forms, efforts, qualities = [], [], []
        if ex.sets_detail:
            for s in ex.sets_detail:
                if s.form_score is not None:
                    forms.append(s.form_score)
                if s.effort_score is not None:
                    efforts.append(s.effort_score)
                if s.quality_score is not None:
                    qualities.append(s.quality_score)
        else:
            if ex.form_score is not None:
                forms.append(ex.form_score)
            if ex.effort_score is not None:
                efforts.append(ex.effort_score)
            if ex.form_score is not None and ex.effort_score is not None:
                qualities.append(ex.form_score * (ex.effort_score / 10.0))
        derived[ex.id] = {
            'avg_form': round(sum(forms) / len(forms), 1) if forms else None,
            'avg_effort': round(sum(efforts) / len(efforts), 1) if efforts else None,
            'avg_quality': round(sum(qualities) / len(qualities), 2) if qualities else None,
        }

    return render_template('exercise.html',
                         exercise_logs=today_exercise,
                         previous_exercises=previous_exercises,
                         workout_a=EXERCISE_DATABASE.get('workout_a'),
                         workout_b=EXERCISE_DATABASE.get('workout_b'),
                         all_exercises=get_all_exercises(),
                         stats={
                             'workouts': total_workouts,
                             'sets': total_sets,
                             'reps': total_reps,
                             'max_weight': max_weight,
                             'avg_form': avg_form,
                             'avg_effort': avg_effort,
                             'volume': int(total_volume),
                             'trend_labels': trend_labels,
                             'trend_form': trend_form,
                             'trend_effort': trend_effort,
                             'trend_quality': trend_quality,
                             'trend_volume': trend_volume,
                             'targets': target_cards,
                         },
                         derived=derived)

@app.route('/add_exercise', methods=['POST'])
@login_required
def add_exercise():
    user = get_current_user()
    exercise_name = request.form.get('exercise-name')
    exercise_type = request.form.get('exercise-type')
    sets = request.form.get('sets')
    reps = request.form.get('reps')
    weight = request.form.get('weight')
    form_score = request.form.get('form-score')
    effort_score = request.form.get('effort-score')
    workout_time_str = request.form.get('workout-time')
    duration_minutes = request.form.get('duration-minutes')
    calories_burned = request.form.get('calories-burned')

    if not all([exercise_name, exercise_type, sets, reps, workout_time_str]):
        flash('All fields except weight are required.', 'error')
        return redirect(url_for('exercise'))

    try:
        sets = int(sets)
        reps = int(reps)
        weight = float(weight) if weight else None
        workout_time = datetime.fromisoformat(workout_time_str.replace('T', ' '))

        # Optional scoring fields with validation
        form_score = int(form_score) if form_score else None
        effort_score = int(effort_score) if effort_score else None
        if form_score is not None and not (1 <= form_score <= 5):
            raise ValueError('Form score must be between 1 and 5')
        if effort_score is not None and not (1 <= effort_score <= 10):
            raise ValueError('Effort score must be between 1 and 10')
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
        form_score=form_score,
        effort_score=effort_score,
        workout_time=workout_time,
        notes=request.form.get('notes', '')
    )

    db.session.add(exercise_log)
    db.session.commit()

    # Create per-set entries with defaults using provided reps/weight/form/effort
    # This allows later edit of each set individually if needed
    for i in range(1, (sets or 0) + 1):
        q = None
        if form_score is not None and effort_score is not None:
            q = round(form_score * (effort_score / 10.0), 2)
        set_log = ExerciseSetLog(
            exercise_log_id=exercise_log.id,
            set_number=i,
            reps=reps,
            weight=weight,
            form_score=form_score,
            effort_score=effort_score,
            quality_score=q,
        )
        db.session.add(set_log)
    db.session.commit()
    # Optionally create an energy burn entry when provided
    try:
        if calories_burned:
            cb = int(calories_burned)
            dur = float(duration_minutes) if duration_minutes else None
            if cb > 0:
                eb = EnergyBurnEntry(
                    user_id=user.id,
                    source='exercise',
                    activity_name=exercise_name,
                    calories_burned=cb,
                    duration_minutes=dur,
                    entry_time=workout_time,
                    notes=f'Logged via exercise form ({exercise_type})'
                )
                db.session.add(eb)
                db.session.commit()
    except Exception:
        # Do not block exercise logging due to energy burn issues
        pass
    flash('Exercise logged successfully!', 'success')
    return redirect(url_for('exercise'))

# Calculator page for BMR/TDEE and profile settings
@app.route('/calculator', methods=['GET', 'POST'])
@login_required
def calculator():
    user = get_current_user()
    profile = UserProfile.query.filter_by(user_id=user.id).first()

    result = None
    if request.method == 'POST':
        sex = request.form.get('sex') or (profile.sex if profile else None)
        age = request.form.get('age')
        weight_kg = request.form.get('weight_kg')
        height_cm = request.form.get('height_cm')
        activity_level = request.form.get('activity_level')
        goal = request.form.get('daily_calorie_goal')

        try:
            age_i = int(age) if age else None
            w = float(weight_kg) if weight_kg else None
            h = float(height_cm) if height_cm else None
            goal_i = int(goal) if goal else None
        except ValueError:
            flash('Please provide valid numeric values.', 'error')
            return redirect(url_for('calculator'))

        # Compute BMR (Mifflin-St Jeor)
        bmr = None
        if all(v is not None for v in [w, h, age_i]) and sex in ['male', 'female']:
            if sex == 'male':
                bmr = 10 * w + 6.25 * h - 5 * age_i + 5
            else:
                bmr = 10 * w + 6.25 * h - 5 * age_i - 161

        # Activity multiplier
        mults = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9,
        }
        tdee = bmr * mults.get(activity_level, 1.2) if bmr is not None else None

        # Save profile
        if not profile:
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)
        profile.sex = sex
        profile.age = age_i
        profile.weight_kg = w
        profile.height_cm = h
        profile.activity_level = activity_level
        if goal_i:
            profile.daily_calorie_goal = goal_i
        elif tdee:
            profile.daily_calorie_goal = int(tdee)
        db.session.commit()

        result = {
            'bmr': int(bmr) if bmr is not None else None,
            'tdee': int(tdee) if tdee is not None else None,
            'recommended_goal': profile.daily_calorie_goal,
        }

    return render_template('calculator.html', profile=profile, result=result)

@app.route('/add_target', methods=['POST'])
@login_required
def add_target():
    user = get_current_user()
    exercise_name = request.form.get('target-exercise-name')
    min_form_score = request.form.get('target-min-form')
    effort_min = request.form.get('target-effort-min')
    effort_max = request.form.get('target-effort-max')

    if not exercise_name:
        flash('Exercise name is required for target.', 'error')
        return redirect(url_for('exercise'))

    try:
        min_form_score = int(min_form_score) if min_form_score else None
        effort_min = int(effort_min) if effort_min else None
        effort_max = int(effort_max) if effort_max else None

        if min_form_score is not None and not (1 <= min_form_score <= 5):
            raise ValueError('Min form must be between 1 and 5')
        if effort_min is not None and not (1 <= effort_min <= 10):
            raise ValueError('Effort min must be between 1 and 10')
        if effort_max is not None and not (1 <= effort_max <= 10):
            raise ValueError('Effort max must be between 1 and 10')
        if effort_min is not None and effort_max is not None and effort_min > effort_max:
            raise ValueError('Effort min cannot be greater than effort max')
    except ValueError as e:
        flash(f'Invalid target: {str(e)}', 'error')
        return redirect(url_for('exercise'))

    target = UserExerciseTarget(
        user_id=user.id,
        exercise_name=exercise_name,
        min_form_score=min_form_score,
        effort_min=effort_min,
        effort_max=effort_max
    )
    db.session.add(target)
    db.session.commit()
    flash('Target added successfully!', 'success')
    return redirect(url_for('exercise'))
@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        if not user_info:
            # Fallback to using userinfo endpoint
            resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo')
            user_info = resp.json()

        if not user_info or 'sub' not in user_info or 'email' not in user_info:
            flash('Invalid user information received from Google.', 'error')
            return redirect(url_for('index'))

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

        # Verify user was saved properly
        if not user.id:
            flash('Error saving user account. Please try again.', 'error')
            return redirect(url_for('login'))

        session['user_id'] = user.id
        session['email'] = user.email
        session['name'] = user.name
        session['user'] = user_info

        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f'Authentication error: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# Initialize database on startup
def create_tables():
    with app.app_context():
        init_db()

# Create tables when app is created only if explicitly enabled (Alebmic manages schema by default)
if os.getenv('AUTO_CREATE_TABLES', '').lower() in ('1', 'true', 'yes'):
    create_tables()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8081)