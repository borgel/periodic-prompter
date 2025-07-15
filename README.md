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

# TODO
1. Set up Python project structure with Poetry (pyproject.toml, src/ directory)
2. Install and configure dependencies using Poetry (pystray for menu bar, plyer for notifications, schedule for timing)
3. Create main application entry point and menu bar icon
4. Implement notification system with user input dialogs
5. Create settings configuration system with validation
6. Add persistent storage for user plans and logs
7. Implement scheduling logic with configurable start/end times
8. Create settings GUI interface
9. Add logging functionality with configurable file output
10. Package application as macOS .app bundle using py2app
11. Add build instructions and commands to this README

# Constraints
* Use Python
* We only care about macOS, don't worry about compatability with other platforms
* Prefer to use fewer libraries if possible, but don't let that restrict features
* Make modular git commits as you work
* make sure not to mark a TODO list item as complete unless you are sure it has been finished
