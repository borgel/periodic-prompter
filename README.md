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
* Add a command (and an explanation to this file) about how to build a macOS .app of this tool

# Constraints
* Use Python
* We only care about macOS, don't worry about compatability with other platforms
*
