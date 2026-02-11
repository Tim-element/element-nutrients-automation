"""
Daily Morning Briefing Generator
Creates and sends a personalized family briefing each morning
"""

from datetime import datetime, timedelta
from typing import List, Dict
import random

from config import (
    FAMILY, FAITH_SCHEDULE, KIDS_SCHEDULE, ACTIVITIES,
    RECURRING_REMINDERS, DAILY_ROUTINE, MEALS
)


def get_day_name(date: datetime = None) -> str:
    """Get lowercase day name."""
    if date is None:
        date = datetime.now()
    return date.strftime('%A').lower()


def get_faith_status(day: str) -> str:
    """Get Faith's work status for the day."""
    schedule = FAITH_SCHEDULE.get(day, 'off')
    if schedule == 'commute':
        return "🚗 Faith commutes to office"
    elif schedule == 'wfh':
        return "🏠 Faith works from home (Friday!)"
    else:
        return "☕ Faith is off today"


def get_kids_schedule(day: str) -> List[str]:
    """Get where each kid is today."""
    lines = []
    for kid, info in KIDS_SCHEDULE.items():
        location = info.get(day, 'home')
        name = FAMILY[kid]['name']
        if location == 'school':
            lines.append(f"📚 {name}: School, home at 4:00 PM")
        elif location == 'daycare':
            lines.append(f"🧸 {name}: Daycare, home at 6:00 PM")
        elif location == 'grandmother':
            lines.append(f"👵 {name}: Grandmother's house")
        else:
            lines.append(f"🏠 {name}: Home")
    return lines


def get_activities(day: str) -> List[Dict]:
    """Get all activities for the day."""
    return [a for a in ACTIVITIES if a['day'] == day]


def format_activity(activity: Dict) -> str:
    """Format an activity for display."""
    kids = ', '.join(activity['kids'])
    time_str = activity['time'].strftime('%I:%M %p').lstrip('0')
    return f"  • {kids}: {activity['name']} at {time_str}"


def get_busy_night_rating(activities: List[Dict]) -> str:
    """Determine how busy the evening is."""
    count = len(activities)
    if count == 0:
        return "🟢 Chill evening - no activities"
    elif count <= 2:
        return "🟡 Moderate evening"
    else:
        return "🔥 Busy night! Multiple activities"


def suggest_dinner(day: str, activities: List[Dict]) -> Dict:
    """Suggest a dinner based on schedule."""
    # Check if it's a busy night (Mon/Wed with early activities)
    busy_night = day in ['monday', 'wednesday'] and any(
        a['time'].hour < 18 for a in activities
    )
    
    if busy_night:
        meal = random.choice(MEALS['quick'])
        notes = f"Quick meal tonight - {meal['name']} ({meal['prep_time']} min)"
    elif day in ['saturday', 'sunday']:
        meal = random.choice(MEALS['weekend'])
        notes = f"Weekend meal idea: {meal['name']}"
    else:
        meal = random.choice(MEALS['normal'])
        notes = f"Tonight: {meal['name']} ({meal['prep_time']} min)"
    
    return {'name': meal['name'], 'notes': notes, 'prep': meal.get('notes', '')}


def get_tomorrow_preview() -> str:
    """Get a quick preview of tomorrow."""
    tomorrow = datetime.now() + timedelta(days=1)
    day_name = get_day_name(tomorrow)
    activities = get_activities(day_name)
    
    if activities:
        activity_list = [f"{a['name']} ({', '.join(a['kids'])})" for a in activities]
        return f"Tomorrow: {', '.join(activity_list[:2])}"
    else:
        return "Tomorrow: No scheduled activities"


def generate_briefing(date: datetime = None) -> str:
    """Generate the full morning briefing."""
    if date is None:
        date = datetime.now()
    
    day_name = get_day_name(date)
    day_display = date.strftime('%A, %B %d')
    
    # Header
    lines = [
        f"🏠 Good morning! Here's your {day_display} briefing:",
        "",
        "═══ TODAY'S SCHEDULE ═══",
        "",
    ]
    
    # Faith's schedule
    lines.append(get_faith_status(day_name))
    lines.append("")
    
    # Kids schedule
    lines.append("👶 Kids:")
    for kid_line in get_kids_schedule(day_name):
        lines.append(f"  {kid_line}")
    lines.append("")
    
    # Activities
    activities = get_activities(day_name)
    if activities:
        lines.append("🎯 ACTIVITIES TODAY:")
        lines.append(get_busy_night_rating(activities))
        for activity in activities:
            lines.append(format_activity(activity))
        lines.append("")
    else:
        lines.append("🎯 No activities today - enjoy the break!")
        lines.append("")
    
    # Dinner suggestion
    dinner = suggest_dinner(day_name, activities)
    lines.append("🍽️ DINNER:")
    lines.append(f"  {dinner['notes']}")
    if dinner['prep']:
        lines.append(f"  💡 {dinner['prep']}")
    lines.append("")
    
    # Reminders
    reminders = [r for r in RECURRING_REMINDERS if r['day'] == day_name]
    if reminders:
        lines.append("⏰ REMINDERS:")
        for r in reminders:
            lines.append(f"  {r['message']}")
        lines.append("")
    
    # Tomorrow preview
    lines.append("═══ COMING UP ═══")
    lines.append(get_tomorrow_preview())
    lines.append("")
    
    # Motivational/personal note
    lines.append("═══ NOTE ═══")
    lines.append("💕 Remember: Quality time with Faith matters. Even 15 minutes of focused conversation after bedtime routines makes a difference.")
    lines.append("")
    
    # Sign off
    lines.append("Have a great day! 🌟")
    
    return '\n'.join(lines)


def send_briefing():
    """Generate and send the briefing via iMessage."""
    briefing = generate_briefing()
    
    # Print for now - integrate with iMessage later
    print(briefing)
    print("\n" + "="*50)
    print("To send via iMessage:")
    print(f"  imsg send --to '{CONTACTS.get('ryan')}' --text \"{briefing[:500]}...\"")
    
    return briefing


if __name__ == "__main__":
    import sys
    
    # Allow testing different days
    if len(sys.argv) > 1:
        test_day = sys.argv[1].lower()
        # Map day names to next occurrence
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if test_day in days:
            today_idx = datetime.now().weekday()
            test_idx = days.index(test_day)
            days_ahead = (test_idx - today_idx) % 7
            test_date = datetime.now() + timedelta(days=days_ahead)
            print(f"\n🧪 TEST MODE: Showing briefing for {test_day.upper()}\n")
            print(generate_briefing(test_date))
        else:
            print(f"Unknown day: {test_day}")
    else:
        send_briefing()
