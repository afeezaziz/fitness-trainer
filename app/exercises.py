"""
Exercise database with structured templates for workout plans
"""

EXERCISE_DATABASE = {
    "workout_a": {
        "name": "Workout A - Full Body (Horizontal Focus)",
        "description": "Balanced full-body session with horizontal pushing/pulling and squat pattern",
        "exercises": [
            {
                "category": "Lower Body (Squat Pattern)",
                "primary": "Barbell Back Squat",
                "sets": 4,
                "reps": "6-10",
                "alternatives": [
                    {"name": "Goblet Squats", "note": "Best for learning form"},
                    {"name": "Dumbbell Front Squats", "note": "Excellent core engagement"},
                    {"name": "Leg Press", "note": "Good for isolating legs if back is tired"}
                ],
                "target_muscles": ["quads", "glutes", "hamstrings", "core"],
                "type": "strength"
            },
            {
                "category": "Upper Body (Horizontal Push)",
                "primary": "Bench Press (Barbell)",
                "sets": 4,
                "reps": "6-10",
                "alternatives": [
                    {"name": "Dumbbell Bench Press", "note": "Better range of motion, easier on shoulders"},
                    {"name": "Incline Dumbbell Press", "note": "Emphasizes the upper chest"},
                    {"name": "Machine Chest Press", "note": "Great for stability and safety"}
                ],
                "target_muscles": ["chest", "shoulders", "triceps"],
                "type": "strength"
            },
            {
                "category": "Upper Body (Horizontal Pull)",
                "primary": "Dumbbell Rows",
                "sets": 4,
                "reps": "8-12 per arm",
                "alternatives": [
                    {"name": "Barbell Rows", "note": "More overall back engagement, but more lower back stress"},
                    {"name": "T-Bar Rows", "note": "A great middle-ground option"},
                    {"name": "Seated Cable Rows", "note": "Excellent for isolating the mid-back"}
                ],
                "target_muscles": ["lats", "rhomboids", "biceps", "lower_back"],
                "type": "strength"
            },
            {
                "category": "Shoulders (Lateral Head)",
                "primary": "Dumbbell Lateral Raises",
                "sets": 3,
                "reps": "10-15",
                "alternatives": [
                    {"name": "Cable Lateral Raises", "note": "Provides constant tension"},
                    {"name": "Machine Lateral Raises", "note": "Strict form, good for isolation"}
                ],
                "target_muscles": ["shoulders", "delts"],
                "type": "strength"
            },
            {
                "category": "Core (Anterior Stability)",
                "primary": "Plank",
                "sets": 3,
                "reps": "Hold for Time",
                "alternatives": [
                    {"name": "Ab Wheel Rollouts", "note": "Advanced and highly effective"},
                    {"name": "Hanging Knee Raises", "note": "Targets lower abs"},
                    {"name": "Dead Bugs", "note": "Excellent for core control and stability"}
                ],
                "target_muscles": ["core", "abs"],
                "type": "strength"
            }
        ]
    },
    "workout_b": {
        "name": "Workout B - Full Body (Posterior Chain Focus)",
        "description": "Balanced full-body session with posterior chain, vertical pushing/pulling",
        "exercises": [
            {
                "category": "Posterior Chain (Hinge Pattern)",
                "primary": "45-Degree Back Extension",
                "sets": 4,
                "reps": "10-15",
                "alternatives": [
                    {"name": "Romanian Deadlifts (RDLs)", "note": "The gold standard, but requires perfect form"},
                    {"name": "Good Mornings", "note": "Advanced, requires light weight and strict form"},
                    {"name": "Kettlebell Swings", "note": "More explosive, great for conditioning"}
                ],
                "target_muscles": ["glutes", "hamstrings", "lower_back", "core"],
                "type": "strength"
            },
            {
                "category": "Upper Body (Vertical Push)",
                "primary": "Seated Dumbbell Shoulder Press",
                "sets": 4,
                "reps": "8-12",
                "alternatives": [
                    {"name": "Standing Barbell Overhead Press (OHP)", "note": "The 'king' of shoulder exercises"},
                    {"name": "Arnold Press", "note": "Hits all three heads of the shoulder"},
                    {"name": "Machine Shoulder Press", "note": "Great for stability and safety"}
                ],
                "target_muscles": ["shoulders", "delts", "triceps"],
                "type": "strength"
            },
            {
                "category": "Upper Body (Vertical Pull)",
                "primary": "Lat Pulldowns",
                "sets": 4,
                "reps": "8-12",
                "alternatives": [
                    {"name": "Pull-ups / Chin-ups", "note": "The ultimate goal. Use assistance bands"},
                    {"name": "Close-Grip Pulldowns", "note": "Emphasizes more of the lats and biceps"},
                    {"name": "Machine-Assisted Pull-ups", "note": "Excellent for learning the movement"}
                ],
                "target_muscles": ["lats", "biceps", "upper_back"],
                "type": "strength"
            },
            {
                "category": "Upper Back / Posture",
                "primary": "Seated Cable Rows",
                "sets": 3,
                "reps": "10-15",
                "alternatives": [
                    {"name": "Face Pulls", "note": "The best for shoulder health and posture"},
                    {"name": "Band Pull-Aparts", "note": "Can be done anywhere, great for warm-ups"},
                    {"name": "Reverse Pec-Deck Machine", "note": "Excellent isolation for the rear delts"}
                ],
                "target_muscles": ["rear_delts", "rhomboids", "upper_back"],
                "type": "strength"
            },
            {
                "category": "Lower Body (Accessory)",
                "primary": "Leg Press",
                "sets": 3,
                "reps": "10-15",
                "alternatives": [
                    {"name": "Bulgarian Split Squats", "note": "Brutal but incredibly effective for legs and glutes"},
                    {"name": "Walking Lunges", "note": "Great for overall leg development and stability"},
                    {"name": "Leg Extensions", "note": "Pure quad isolation"}
                ],
                "target_muscles": ["quads", "glutes", "hamstrings"],
                "type": "strength"
            }
        ]
    },
    "cardio": [
        {
            "name": "Running",
            "type": "cardio",
            "target_muscles": ["legs", "cardiovascular"],
            "suggested_reps": "30 minutes",
            "sets": 1
        },
        {
            "name": "Cycling",
            "type": "cardio",
            "target_muscles": ["legs", "cardiovascular"],
            "suggested_reps": "45 minutes",
            "sets": 1
        },
        {
            "name": "Swimming",
            "type": "cardio",
            "target_muscles": ["full_body", "cardiovascular"],
            "suggested_reps": "30 minutes",
            "sets": 1
        }
    ],
    "flexibility": [
        {
            "name": "Yoga",
            "type": "flexibility",
            "target_muscles": ["full_body", "core"],
            "suggested_reps": "45 minutes",
            "sets": 1
        },
        {
            "name": "Stretching",
            "type": "flexibility",
            "target_muscles": ["full_body"],
            "suggested_reps": "30 minutes",
            "sets": 1
        }
    ]
}

def get_exercise_by_name(name):
    """Find an exercise by name in the database"""
    for workout_name, workout_data in EXERCISE_DATABASE.items():
        if workout_name in ["workout_a", "workout_b"]:
            for exercise in workout_data["exercises"]:
                if exercise["primary"] == name:
                    return exercise
                for alt in exercise["alternatives"]:
                    if alt["name"] == name:
                        return {
                            "name": alt["name"],
                            "type": exercise["type"],
                            "target_muscles": exercise["target_muscles"],
                            "category": exercise["category"]
                        }

    # Check cardio and flexibility exercises
    for exercise in EXERCISE_DATABASE.get("cardio", []):
        if exercise["name"] == name:
            return exercise

    for exercise in EXERCISE_DATABASE.get("flexibility", []):
        if exercise["name"] == name:
            return exercise

    return None

def get_workout_plan(workout_name):
    """Get a complete workout plan by name"""
    return EXERCISE_DATABASE.get(workout_name)

def get_all_exercises():
    """Get all exercises from all workout plans"""
    all_exercises = []

    for workout_name, workout_data in EXERCISE_DATABASE.items():
        if workout_name in ["workout_a", "workout_b"]:
            for exercise in workout_data["exercises"]:
                all_exercises.append({
                    "name": exercise["primary"],
                    "type": exercise["type"],
                    "category": exercise["category"],
                    "target_muscles": exercise["target_muscles"],
                    "sets": exercise["sets"],
                    "reps": exercise["reps"]
                })

                # Add alternatives
                for alt in exercise["alternatives"]:
                    all_exercises.append({
                        "name": alt["name"],
                        "type": exercise["type"],
                        "category": exercise["category"],
                        "target_muscles": exercise["target_muscles"],
                        "sets": exercise["sets"],
                        "reps": exercise["reps"]
                    })

    # Add cardio and flexibility exercises
    for exercise in EXERCISE_DATABASE.get("cardio", []):
        all_exercises.append(exercise)

    for exercise in EXERCISE_DATABASE.get("flexibility", []):
        all_exercises.append(exercise)

    return all_exercises