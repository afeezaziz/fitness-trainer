from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    food_logs = db.relationship('FoodLog', backref='user', lazy=True, cascade='all, delete-orphan')
    calorie_entries = db.relationship('CalorieEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    exercise_logs = db.relationship('ExerciseLog', backref='user', lazy=True, cascade='all, delete-orphan')
    exercise_targets = db.relationship('UserExerciseTarget', backref='user', lazy=True, cascade='all, delete-orphan')
    energy_burns = db.relationship('EnergyBurnEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    profile = db.relationship('UserProfile', backref='user', uselist=False, lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_type = db.Column(db.String(50), nullable=False)  # breakfast, lunch, dinner, snack
    food_name = db.Column(db.String(200), nullable=False)
    portion_size = db.Column(db.String(100), nullable=False)
    meal_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<FoodLog {self.food_name} - {self.meal_type}>'

class CalorieEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_item = db.Column(db.String(200), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.String(100), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<CalorieEntry {self.food_item} - {self.calories} cal>'

class EnergyBurnEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source = db.Column(db.String(20), nullable=False, default='neat')  # neat, cardio, exercise, other
    activity_name = db.Column(db.String(200), nullable=False)
    calories_burned = db.Column(db.Integer, nullable=False)
    duration_minutes = db.Column(db.Float, nullable=True)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<EnergyBurnEntry {self.activity_name} - {self.calories_burned} cal>'

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    sex = db.Column(db.String(10), nullable=True)  # male, female, other
    age = db.Column(db.Integer, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    height_cm = db.Column(db.Float, nullable=True)
    activity_level = db.Column(db.String(20), nullable=True)  # sedentary, light, moderate, active, very_active
    daily_calorie_goal = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserProfile user={self.user_id} goal={self.daily_calorie_goal}>'

class ExerciseLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_name = db.Column(db.String(200), nullable=False)
    exercise_type = db.Column(db.String(50), nullable=False)  # strength, cardio, flexibility, sports
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=True)  # in lbs or kg
    # Scoring fields
    form_score = db.Column(db.Integer, nullable=True)     # 1-5 form quality
    effort_score = db.Column(db.Integer, nullable=True)   # 1-10 effort/RPE
    workout_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ExerciseLog {self.exercise_name} - {self.sets}x{self.reps}>'

    # Per-set details relationship
    sets_detail = db.relationship('ExerciseSetLog', backref='exercise_log', lazy=True, cascade='all, delete-orphan')


class ExerciseSetLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_log_id = db.Column(db.Integer, db.ForeignKey('exercise_log.id'), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=True)
    form_score = db.Column(db.Integer, nullable=True)   # 1-5
    effort_score = db.Column(db.Integer, nullable=True) # 1-10
    quality_score = db.Column(db.Float, nullable=True)  # computed: form_score * (effort_score/10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ExerciseSetLog ex={self.exercise_log_id} set={self.set_number} reps={self.reps}>'


class UserExerciseTarget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_name = db.Column(db.String(200), nullable=False)
    min_form_score = db.Column(db.Integer, nullable=True)     # 1-5
    effort_min = db.Column(db.Integer, nullable=True)         # 1-10
    effort_max = db.Column(db.Integer, nullable=True)         # 1-10
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserExerciseTarget {self.exercise_name} user={self.user_id}>'

class ChatRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    messages = db.relationship('ChatMessage', backref='room', lazy=True, cascade='all, delete-orphan')
    participants = db.relationship('ChatParticipant', backref='room', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ChatRoom {self.name}>'

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, system, join, leave
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', backref='chat_messages')

    def __repr__(self):
        return f'<ChatMessage {self.user.name}: {self.message[:50]}>'

class ChatParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('chat_room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    is_online = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship('User', backref='chat_participations')

    def __repr__(self):
        return f'<ChatParticipant {self.user.name} in {self.room.name}>'

def init_db():
    """Initialize the database with all tables"""
    db.create_all()

    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(os.path.abspath('fitness.db'))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)