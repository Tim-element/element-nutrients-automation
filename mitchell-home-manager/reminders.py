"""
Smart Reminder System
Proactive alerts for the Mitchell family
"""

from datetime import datetime, timedelta, time
from typing import List, Dict, Optional
import json

from config import (
    ACTIVITIES, RECURRING_REMINDERS, PREP_REMINDERS,
    CONTACTS, DAILY_ROUTINE
)


class SmartReminderSystem:
    """Manages and sends proactive reminders."""
    
    def __init__(self):
        self.reminders = []
        self.sent_reminders = set()  # Track what we've already sent today
    
    def get_today_activities(self) -> List[Dict]:
        """Get all activities for today."""
        day = datetime.now().strftime('%A').lower()
        return [a for a in ACTIVITIES if a['day'] == day]
    
    def get_activity_prep_reminders(self) -> List[Dict]:
        """Generate prep reminders for today's activities."""
        reminders = []
        activities = self.get_today_activities()
        now = datetime.now()
        
        for activity in activities:
            activity_name = activity['name']
            activity_time = datetime.combine(now.date(), activity['time'])
            
            # Check if this activity has a prep reminder
            if activity_name in PREP_REMINDERS:
                prep = PREP_REMINDERS[activity_name]
                reminder_time = activity_time - timedelta(minutes=prep['time_before'])
                
                # Only add if reminder time is in the future
                if reminder_time > now:
                    reminders.append({
                        'time': reminder_time,
                        'message': f"⏰ {prep['message']} ({activity['kids']})",
                        'type': 'activity_prep'
                    })
        
        return reminders
    
    def get_recurring_reminders(self) -> List[Dict]:
        """Get standard recurring reminders for today."""
        day = datetime.now().strftime('%A').lower()
        now = datetime.now()
        reminders = []
        
        for r in RECURRING_REMINDERS:
            if r['day'] == day:
                reminder_time = datetime.combine(now.date(), r['time'])
                if reminder_time > now:
                    reminders.append({
                        'time': reminder_time,
                        'message': r['message'],
                        'type': 'recurring'
                    })
        
        return reminders
    
    def get_bedtime_reminders(self) -> List[Dict]:
        """Reminders for bedtime routines."""
        now = datetime.now()
        reminders = []
        
        # Owen's bedtime prep (30 min before)
        owen_bedtime = datetime.combine(now.date(), DAILY_ROUTINE['bedtime']['owen'])
        owen_prep = owen_bedtime - timedelta(minutes=30)
        
        if owen_prep > now and owen_prep.date() == now.date():
            reminders.append({
                'time': owen_prep,
                'message': '🌙 Owen bedtime in 30 min - start wind-down routine',
                'type': 'bedtime'
            })
        
        # Older kids bedtime prep (30 min before)
        older_bedtime = datetime.combine(now.date(), DAILY_ROUTINE['bedtime']['older_kids'])
        older_prep = older_bedtime - timedelta(minutes=30)
        
        if older_prep > now and older_prep.date() == now.date():
            reminders.append({
                'time': older_prep,
                'message': '🌙 Reagan & Rory bedtime in 30 min - start routines',
                'type': 'bedtime'
            })
        
        return reminders
    
    def check_custom_reminders(self) -> List[Dict]:
        """Check for user-defined custom reminders."""
        # Load from file if exists
        try:
            with open('custom_reminders.json', 'r') as f:
                custom = json.load(f)
        except FileNotFoundError:
            return []
        
        now = datetime.now()
        reminders = []
        
        for r in custom:
            reminder_time = datetime.fromisoformat(r['time'])
            if reminder_time > now and reminder_time.date() == now.date():
                reminders.append({
                    'time': reminder_time,
                    'message': r['message'],
                    'type': 'custom'
                })
        
        return reminders
    
    def get_upcoming_reminders(self, hours_ahead: int = 12) -> List[Dict]:
        """Get all reminders for the next X hours."""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours_ahead)
        
        all_reminders = (
            self.get_activity_prep_reminders() +
            self.get_recurring_reminders() +
            self.get_bedtime_reminders() +
            self.check_custom_reminders()
        )
        
        # Filter to upcoming only and sort by time
        upcoming = [r for r in all_reminders if r['time'] <= cutoff]
        upcoming.sort(key=lambda x: x['time'])
        
        return upcoming
    
    def format_reminder(self, reminder: Dict) -> str:
        """Format a reminder for display."""
        time_str = reminder['time'].strftime('%I:%M %p').lstrip('0')
        return f"{time_str}: {reminder['message']}"
    
    def send_due_reminders(self):
        """Check and send any reminders that are due now."""
        now = datetime.now()
        upcoming = self.get_upcoming_reminders(hours_ahead=1)
        
        sent = []
        for reminder in upcoming:
            # Send if within 5 minutes of reminder time
            time_diff = abs((reminder['time'] - now).total_seconds())
            if time_diff < 300:  # 5 minutes
                reminder_id = f"{reminder['time'].isoformat()}_{reminder['message'][:20]}"
                
                if reminder_id not in self.sent_reminders:
                    self.sent_reminders.add(reminder_id)
                    self._send_message(reminder['message'])
                    sent.append(reminder)
        
        return sent
    
    def _send_message(self, message: str):
        """Send message via iMessage."""
        # For now, just print - integrate with iMessage later
        print(f"📱 SENDING: {message}")
        # In production:
        # imsg send --to CONTACTS['ryan'] --text message
    
    def add_custom_reminder(self, message: str, when: datetime):
        """Add a one-time custom reminder."""
        try:
            with open('custom_reminders.json', 'r') as f:
                custom = json.load(f)
        except FileNotFoundError:
            custom = []
        
        custom.append({
            'message': message,
            'time': when.isoformat(),
            'created': datetime.now().isoformat()
        })
        
        with open('custom_reminders.json', 'w') as f:
            json.dump(custom, f, indent=2)
        
        return f"✅ Reminder set for {when.strftime('%I:%M %p').lstrip('0')}: {message}"


def show_todays_reminders():
    """Display all reminders for today."""
    system = SmartReminderSystem()
    reminders = system.get_upcoming_reminders(hours_ahead=24)
    
    print("📅 TODAY'S REMINDERS:\n")
    
    if not reminders:
        print("No upcoming reminders for the next 24 hours.")
        return
    
    for r in reminders:
        print(system.format_reminder(r))


def check_and_send():
    """Check for due reminders and send them."""
    system = SmartReminderSystem()
    sent = system.send_due_reminders()
    
    if sent:
        print(f"✅ Sent {len(sent)} reminder(s)")
    else:
        print("No reminders due at this time.")
    
    return sent


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_and_send()
    else:
        show_todays_reminders()
