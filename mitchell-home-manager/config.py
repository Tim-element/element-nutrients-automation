"""
Mitchell Family Configuration
All family schedules, activities, and preferences
"""

from datetime import time

# Family Members
FAMILY = {
    'ryan': {'name': 'Ryan', 'role': 'dad'},
    'faith': {'name': 'Faith', 'role': 'mom'},
    'reagan': {'name': 'Reagan', 'age': 6, 'school': 'elementary'},
    'rory': {'name': 'Rory', 'age': 5, 'school': 'daycare'},
    'owen': {'name': 'Owen', 'age': 2, 'school': 'daycare'}
}

# Daily Schedule Template
DAILY_ROUTINE = {
    'wake_time': time(8, 0),
    'dinner_time': time(18, 30),
    'bedtime': {
        'owen': time(20, 0),
        'older_kids': time(21, 0)
    }
}

# Faith's Work Schedule
FAITH_SCHEDULE = {
    'monday': 'commute',
    'tuesday': 'commute',
    'wednesday': 'commute',
    'thursday': 'commute',
    'friday': 'wfh',
    'saturday': 'off',
    'sunday': 'off'
}

# Kids' School/Childcare Schedule
KIDS_SCHEDULE = {
    'reagan': {
        'monday': 'school',
        'tuesday': 'school',
        'wednesday': 'school',
        'thursday': 'school',
        'friday': 'school',
        'home_time': time(16, 0)
    },
    'rory': {
        'monday': 'grandmother',
        'tuesday': 'daycare',
        'wednesday': 'grandmother',
        'thursday': 'daycare',
        'friday': 'daycare',
        'home_time': time(18, 0)
    },
    'owen': {
        'monday': 'grandmother',
        'tuesday': 'daycare',
        'wednesday': 'grandmother',
        'thursday': 'daycare',
        'friday': 'daycare',
        'home_time': time(18, 0)
    }
}

# Weekly Activities
ACTIVITIES = [
    # Kumon - Reagan & Rory
    {'name': 'Kumon', 'kids': ['Reagan', 'Rory'], 'day': 'monday', 'time': time(17, 0), 'duration': 60},
    {'name': 'Kumon', 'kids': ['Reagan', 'Rory'], 'day': 'wednesday', 'time': time(17, 0), 'duration': 60},
    
    # Reagan's activities
    {'name': 'Gymnastics', 'kids': ['Reagan'], 'day': 'monday', 'time': time(19, 0), 'duration': 60},
    {'name': 'Cheer', 'kids': ['Reagan'], 'day': 'wednesday', 'time': time(18, 30), 'duration': 60},
    {'name': 'Tumbling', 'kids': ['Reagan'], 'day': 'thursday', 'time': time(17, 0), 'duration': 60},
    
    # Rory's activities
    {'name': 'Gymnastics', 'kids': ['Rory'], 'day': 'wednesday', 'time': time(18, 30), 'duration': 60},
    
    # Owen's activities
    {'name': 'Gymnastics', 'kids': ['Owen'], 'day': 'saturday', 'time': time(11, 30), 'duration': 45}
]

# Recurring Reminders
RECURRING_REMINDERS = [
    {'name': 'Trash Night', 'day': 'tuesday', 'time': time(19, 0), 'message': '🗑️ Trash goes out tonight!'},
    {'name': 'Trash Morning', 'day': 'wednesday', 'time': time(7, 30), 'message': '🗑️ Trash pickup today - take bins to curb'},
    {'name': 'Sunday Prep', 'day': 'sunday', 'time': time(19, 0), 'message': '📅 Review the week ahead. Any schedule changes?'},
]

# Activity Prep Reminders (minutes before)
PREP_REMINDERS = {
    'Kumon': {'time_before': 30, 'message': '📚 Kumon in 30 min - grab folders!'},
    'Gymnastics': {'time_before': 45, 'message': '🤸 Gymnastics soon - pack leotard/bag!'},
    'Cheer': {'time_before': 45, 'message': '📣 Cheer practice soon - pack uniform!'},
    'Tumbling': {'time_before': 45, 'message': '🤸 Tumbling soon - pack gear!'},
}

# Meal Planning Database
MEALS = {
    'quick': [  # For busy nights (Mon/Wed with Kumon at 5pm)
        {'name': 'Tacos', 'prep_time': 15, 'notes': 'Pre-cooked chicken or ground beef'},
        {'name': 'Pasta with jar sauce', 'prep_time': 15, 'notes': 'Add frozen meatballs'},
        {'name': 'Quesadillas', 'prep_time': 10, 'notes': 'Beans, cheese, salsa'},
        {'name': 'Chicken nuggets & veggies', 'prep_time': 15, 'notes': 'Air fryer + frozen veggies'},
        {'name': 'Breakfast for dinner', 'prep_time': 15, 'notes': 'Pancakes, eggs, bacon'},
    ],
    'normal': [  # Standard weeknight meals
        {'name': 'Sheet pan chicken & veggies', 'prep_time': 35, 'notes': 'Bake together at 400°'},
        {'name': 'Stir fry', 'prep_time': 25, 'notes': 'Rice + frozen stir-fry mix + protein'},
        {'name': 'Slow cooker chicken', 'prep_time': 15, 'notes': 'Start at 3pm, ready at 6'},
        {'name': 'Spaghetti & meatballs', 'prep_time': 20, 'notes': 'Frozen meatballs + jar sauce'},
        {'name': 'Grilled cheese & tomato soup', 'prep_time': 15, 'notes': 'Easy comfort food'},
        {'name': 'Pizza night', 'prep_time': 20, 'notes': 'Frozen or homemade'},
        {'name': 'Burgers & fries', 'prep_time': 25, 'notes': 'Air fryer fries'},
        {'name': 'Chicken soup', 'prep_time': 30, 'notes': 'Rotisserie chicken shortcut'},
    ],
    'weekend': [  # More elaborate meals
        {'name': 'Homemade pizza', 'prep_time': 45, 'notes': 'Fun family activity'},
        {'name': 'Grilled salmon & veggies', 'prep_time': 30, 'notes': 'Healthy weekend meal'},
        {'name': 'Slow cooker pot roast', 'prep_time': 15, 'notes': 'Start early, feast at dinner'},
        {'name': 'Pancake brunch', 'prep_time': 30, 'notes': 'Weekend breakfast for dinner'},
    ]
}

# Contact Info for iMessage
CONTACTS = {
    'ryan': '+14253618792',
    'faith': None  # To be filled in
}

# Preferences
PREFERENCES = {
    'briefing_time': time(7, 30),
    'evening_prep_time': time(20, 0),
    'reminder_style': 'friendly',  # friendly, brief, detailed
    'meal_complexity': 'adaptive',  # adapts to schedule
}
