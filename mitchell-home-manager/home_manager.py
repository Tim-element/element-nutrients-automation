"""
Natural Language Home Manager Interface
Process plain text commands and implement them
"""

from datetime import datetime, timedelta
from typing import Optional
import re

from reminders import SmartReminderSystem
from morning_briefing import generate_briefing


class HomeManager:
    """Process natural language commands for home management."""
    
    def __init__(self):
        self.reminders = SmartReminderSystem()
    
    def process_command(self, text: str) -> str:
        """Process a natural language command and return response."""
        text = text.lower().strip()
        
        # Briefing commands
        if any(word in text for word in ['briefing', 'schedule today', 'what\'s today']):
            return self._get_briefing()
        
        if any(word in text for word in ['tomorrow', 'next day']):
            return self._get_tomorrow()
        
        # Reminder commands
        if any(phrase in text for phrase in ['remind me', 'remind us', 'set reminder']):
            return self._parse_reminder(text)
        
        # Dinner commands
        if any(word in text for word in ['dinner', 'meal', 'what to cook', 'eat tonight']):
            return self._suggest_dinner()
        
        # Activity queries
        if any(word in text for word in ['activities', 'busy tonight', 'schedule']):
            return self._get_activities()
        
        # Help
        if any(word in text for word in ['help', 'what can you do', 'commands']):
            return self._get_help()
        
        # Default
        return "I'm not sure what you're asking. Try: 'briefing', 'remind me to...', 'dinner ideas', or 'help'"
    
    def _get_briefing(self) -> str:
        """Generate and return today's briefing."""
        briefing = generate_briefing()
        # Return summary since full briefing is long
        lines = briefing.split('\n')[:15]
        return '\n'.join(lines) + '\n\n(Reply "full briefing" for complete version)'
    
    def _get_tomorrow(self) -> str:
        """Get tomorrow's schedule."""
        tomorrow = datetime.now() + timedelta(days=1)
        from config import get_day_name, get_activities
        
        day = tomorrow.strftime('%A').lower()
        activities = get_activities(day)
        
        lines = [f"📅 TOMORROW ({tomorrow.strftime('%A, %B %d')}):\n"]
        
        if activities:
            lines.append("Activities:")
            for a in activities:
                time_str = a['time'].strftime('%I:%M %p').lstrip('0')
                kids = ', '.join(a['kids'])
                lines.append(f"  • {kids}: {a['name']} at {time_str}")
        else:
            lines.append("No scheduled activities - enjoy the free time!")
        
        return '\n'.join(lines)
    
    def _parse_reminder(self, text: str) -> str:
        """Parse reminder command and set reminder."""
        # Extract reminder message
        patterns = [
            r'remind (?:me|us) (?:to )?(.+?)(?: at| on| every|$)',
            r'set reminder (?:to )?(.+?)(?: at| on| every|$)',
        ]
        
        message = None
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                message = match.group(1).strip()
                break
        
        if not message:
            return "❓ I didn't understand. Try: 'Remind me to take out trash at 7pm'"
        
        # Parse time/day
        when = self._parse_time(text)
        
        if when:
            result = self.reminders.add_custom_reminder(message, when)
            return f"✅ {result}"
        else:
            # Default to tonight at 7pm if no time specified
            when = datetime.now().replace(hour=19, minute=0, second=0)
            if when < datetime.now():
                when += timedelta(days=1)
            
            result = self.reminders.add_custom_reminder(message, when)
            return f"✅ {result} (set for 7pm - you can specify a different time next time)"
    
    def _parse_time(self, text: str) -> Optional[datetime]:
        """Extract time from text."""
        now = datetime.now()
        
        # Check for specific times
        time_patterns = [
            (r'at (\d+):(\d+)\s*(am|pm)?', 'specific'),
            (r'at (\d+)\s*(am|pm)', 'hour'),
            (r'(\d+)\s*(am|pm)', 'hour'),
        ]
        
        for pattern, pattern_type in time_patterns:
            match = re.search(pattern, text)
            if match:
                if pattern_type == 'specific':
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    ampm = match.group(3)
                else:
                    hour = int(match.group(1))
                    minute = 0
                    ampm = match.group(2)
                
                # Handle AM/PM
                if ampm == 'pm' and hour != 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
                
                when = now.replace(hour=hour, minute=minute, second=0)
                
                # Check for "tomorrow"
                if 'tomorrow' in text:
                    when += timedelta(days=1)
                elif when < now and 'today' not in text:
                    # Assume tomorrow if time passed
                    when += timedelta(days=1)
                
                return when
        
        # Check for relative times
        if 'in an hour' in text or 'in 1 hour' in text:
            return now + timedelta(hours=1)
        if 'in 30 minutes' in text or 'in half an hour' in text:
            return now + timedelta(minutes=30)
        if 'tonight' in text:
            return now.replace(hour=19, minute=0)
        
        return None
    
    def _suggest_dinner(self) -> str:
        """Suggest dinner ideas."""
        from config import MEALS
        import random
        
        now = datetime.now()
        day = now.strftime('%A').lower()
        
        # Determine meal type based on schedule
        from config import ACTIVITIES
        activities_today = [a for a in ACTIVITIES if a['day'] == day]
        busy_night = day in ['monday', 'wednesday'] and any(
            a['time'].hour < 18 for a in activities_today
        )
        
        if busy_night:
            suggestions = random.sample(MEALS['quick'], min(3, len(MEALS['quick'])))
            lines = ["🍽️ QUICK DINNER IDEAS (busy night!):\n"]
        else:
            suggestions = random.sample(MEALS['normal'], min(3, len(MEALS['normal'])))
            lines = ["🍽️ DINNER SUGGESTIONS:\n"]
        
        for i, meal in enumerate(suggestions, 1):
            lines.append(f"{i}. {meal['name']} ({meal['prep_time']} min)")
            lines.append(f"   💡 {meal['notes']}\n")
        
        return '\n'.join(lines)
    
    def _get_activities(self) -> str:
        """Get today's activities."""
        day = datetime.now().strftime('%A').lower()
        from config import ACTIVITIES
        
        activities = [a for a in ACTIVITIES if a['day'] == day]
        
        if not activities:
            return "🎯 No activities scheduled today!"
        
        lines = [f"🎯 TODAY'S ACTIVITIES ({len(activities)}):\n"]
        
        for a in sorted(activities, key=lambda x: x['time']):
            time_str = a['time'].strftime('%I:%M %p').lstrip('0')
            kids = ', '.join(a['kids'])
            lines.append(f"  {time_str}: {a['name']} ({kids})")
        
        return '\n'.join(lines)
    
    def _get_help(self) -> str:
        """Return help text."""
        return """🏠 HOME MANAGER COMMANDS:

📅 SCHEDULE:
  • "Briefing" - Today's full schedule
  • "Tomorrow" - See tomorrow's plan
  • "Activities" - Today's activities only

⏰ REMINDERS:
  • "Remind me to... at [time]"
  • "Remind us about... tomorrow at 7pm"
  • "Remind me in an hour to..."

🍽️ MEALS:
  • "Dinner ideas" - Get suggestions
  • "What should we eat?" - Meal planning

I'll learn your preferences over time and get smarter about suggestions!
"""


def handle_message(text: str) -> str:
    """Main entry point - process a message and return response."""
    manager = HomeManager()
    return manager.process_command(text)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        print(f"👤 You: {command}")
        print(f"🤖 Me: {handle_message(command)}")
    else:
        # Interactive mode
        print("🏠 Mitchell Home Manager")
        print("Type 'exit' to quit\n")
        
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                response = handle_message(user_input)
                print(f"\n🤖 {response}\n")
            except (KeyboardInterrupt, EOFError):
                break
        
        print("\nGoodbye! 👋")
