# Mitchell Family Home Manager

AI-powered household coordination system for Ryan, Faith, Reagan, Rory, and Owen.

## Features

### 1. Daily Morning Briefing (`morning_briefing.py`)
Automatically generates and texts a daily summary each morning at 7:30 AM including:
- Today's schedule for all family members
- Activity reminders with prep times
- Trash/recycling collection alerts
- Weather-appropriate clothing suggestions
- Dinner suggestion based on tonight's schedule

### 2. Smart Reminder System (`reminders.py`)
- **Proactive alerts** 15-30 minutes before events
- **Weekly prep reminders** (Sunday night prep for week ahead)
- **Trash day alerts** (night before and morning of)
- **Activity prep reminders** (gymnastics bags, Kumon folders)

### 3. Schedule Manager (`schedule.py`)
Master family calendar with:
- All 6+ weekly activities for the kids
- Transportation coordination
- Grandmother childcare days (Mon/Wed)
- Faith's WFH Friday schedule

### 4. Meal Planner (`meal_planner.py`)
- Suggests dinners based on time constraints
- Quick meals for busy nights (Mon/Wed with Kumon at 5pm)
- Crockpot/early prep suggestions when needed

### 5. Natural Language Interface (`home_manager.py`)
Text commands like:
- "Remind us about trash on Wednesday nights"
- "Add Reagan's birthday party to the calendar"
- "What's our schedule this weekend?"
- "Suggest easy dinners for busy nights"

## Configuration

Edit `config.py` to customize:
- Wake time (default: 8:00 AM)
- Bedtimes
- Activity times
- Reminder preferences

## Usage

### Automated (via cron)
- Daily briefing: 7:30 AM
- Evening prep: 8:00 PM
- Weekly prep: Sunday 7:00 PM

### Manual
```bash
# Generate today's briefing
python morning_briefing.py

# Check tomorrow's schedule
python schedule.py --date tomorrow

# Get dinner suggestion
python meal_planner.py --tonight
```

## iMessage Integration

Text me (your AI assistant) commands:
- "Briefing" - Get today's summary
- "Tomorrow" - See tomorrow's schedule
- "Remind me to..." - Set custom reminders
- "Dinner ideas" - Get meal suggestions

---
*Built to give Ryan and Faith more time together* ❤️
