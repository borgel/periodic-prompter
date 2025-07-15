# periodic-prompter
A macOS tool to periodically ask you what you're working on

# Features
The main function of this tool is to display a persistant notification every hour (configurable) asking what they plan to do in the next hour, and if they completed what they expected to in the last hour. When they click the notification there will be a text box they can fill out with what they plan to do. When they next notification comes up it will display their plan from the last one. Each hour, if the user interacts with the notification, it will

The main interface of the application is the menu bar (it has no dock icon). When they click on the menu bar icon it will open a menu telling them what they said they would do this hour. In addition there will be options to open a settings screen as well as quit.

The user can configure:
* The interval at which they are asked, in fractional hours. Reject anything shorter than 0.1 hours
* The start and end time of these reminders (IE start reminding every hour starting at 9am, and stop at 6pm, on weekdays)
* If they prompt does the 'what are you doing in the next hour' part or not
* If they want to create a log
* Where to place the log file and what to call if, if they want to use one

# Installation & Usage

## Requirements
- macOS (tested on macOS 15.0+)
- Python 3.8+ 
- Poetry for dependency management

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd periodic-prompter
   ```

2. **Install dependencies with Poetry**
   ```bash
   poetry install
   ```

3. **Run the application in development mode**
   ```bash
   poetry run python -m periodic_prompter.main
   ```

## Building the macOS App

1. **Build the .app bundle**
   ```bash
   poetry run python build_app.py
   ```

2. **The built app will be in the `dist/` directory**
   - Location: `dist/Periodic Prompter.app`
   - A symbolic link `Periodic Prompter.app` will be created in the project root

3. **Install the app**
   ```bash
   # Option 1: Open from current location
   open "dist/Periodic Prompter.app"
   
   # Option 2: Copy to Applications folder
   cp -R "dist/Periodic Prompter.app" /Applications/
   ```

## Usage

1. **Launch the app** - it will appear in your menu bar as a clock icon
2. **Click the menu bar icon** to access:
   - Current Plan: View your current plan
   - Prompt Now: Manually trigger a planning session
   - Schedule Info: View scheduling status and next prompt time
   - Toggle Scheduler: Start/stop automatic prompts
   - Settings: Configure intervals, working hours, and logging
   - Quit: Exit the application

3. **Configure settings** via the Settings menu:
   - Set prompt intervals (minimum 6 minutes)
   - Configure working hours and weekday-only mode
   - Enable/disable logging and choose log file location
   - Export your plans to text or CSV format

## Features Completed
- ✅ Menu bar application with no dock icon
- ✅ Configurable prompt intervals (0.1+ hours)
- ✅ Working hours and weekday scheduling
- ✅ Persistent storage of plans and completion status
- ✅ Automatic and manual prompting
- ✅ Comprehensive settings GUI
- ✅ Text and CSV logging/export
- ✅ macOS .app bundle packaging
- ✅ Background operation and notification support

# Constraints
* Use Python
* We only care about macOS, don't worry about compatability with other platforms
* Prefer to use fewer libraries if possible, but don't let that restrict features
* Make modular git commits as you work
* make sure not to mark a TODO list item as complete unless you are sure it has been finished
