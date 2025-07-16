"""Scheduling logic for Periodic Prompter."""

import schedule
import time
import threading
from datetime import datetime, time as dt_time
from typing import Callable


class PromptScheduler:
    """Manages scheduled prompts based on user settings."""
    
    def __init__(self, settings, notification_system, menu_update_callback=None):
        self.settings = settings
        self.notification_system = notification_system
        self.menu_update_callback = menu_update_callback
        self.running = False
        self.scheduler_thread = None
        self.stop_event = threading.Event()
        
    def should_prompt_now(self) -> bool:
        """Check if we should prompt now based on current settings."""
        # Check if today is a valid day
        if not self.settings.should_prompt_today():
            return False
        
        # Check if current time is within working hours
        if not self.settings.is_working_time():
            return False
        
        return True
    
    def prompt_callback(self):
        """Callback function for scheduled prompts."""
        if self.should_prompt_now():
            print(f"[{datetime.now()}] Triggering scheduled prompt")
            
            # Get previous plan
            previous_plan = self.notification_system.current_plan
            
            # Trigger the prompt
            result = self.notification_system.prompt_user_plan(previous_plan)
            
            if result and result.get('plan'):
                print(f"Plan recorded: {result['plan'][:50]}...")
                # Update the menu if callback is provided
                if self.menu_update_callback:
                    self.menu_update_callback()
            else:
                print("No plan recorded or user cancelled")
        else:
            print(f"[{datetime.now()}] Skipping prompt (outside working hours or weekend)")
    
    def setup_schedule(self):
        """Set up the scheduling based on current settings."""
        # Clear existing schedule
        schedule.clear()
        
        # Get interval from settings
        interval_hours = self.settings.get('interval_hours', 1.0)
        
        # Convert hours to minutes for more precise scheduling
        interval_minutes = int(interval_hours * 60)
        
        print(f"Setting up schedule: every {interval_minutes} minutes")
        
        # Schedule the prompt
        if interval_minutes >= 60:
            # Use hourly scheduling for intervals >= 1 hour
            hours = interval_minutes // 60
            schedule.every(hours).hours.do(self.prompt_callback)
        else:
            # Use minute-based scheduling for sub-hour intervals
            schedule.every(interval_minutes).minutes.do(self.prompt_callback)
    
    def run_scheduler(self):
        """Run the scheduler in a loop."""
        print("Starting scheduler...")
        self.setup_schedule()
        
        while not self.stop_event.is_set():
            try:
                # Check for pending scheduled jobs
                schedule.run_pending()
                
                # Sleep for a short time to avoid busy waiting
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in scheduler: {e}")
                time.sleep(60)  # Wait a bit longer on error
    
    def start(self):
        """Start the scheduler in a background thread."""
        if self.running:
            print("Scheduler already running")
            return
        
        self.running = True
        self.stop_event.clear()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(
            target=self.run_scheduler,
            daemon=True,
            name="PromptScheduler"
        )
        self.scheduler_thread.start()
        
        print("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.running:
            return
        
        print("Stopping scheduler...")
        self.running = False
        self.stop_event.set()
        
        # Clear scheduled jobs
        schedule.clear()
        
        # Wait for thread to finish (with timeout)
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        print("Scheduler stopped")
    
    def restart(self):
        """Restart the scheduler (useful when settings change)."""
        print("Restarting scheduler with new settings...")
        self.stop()
        time.sleep(1)  # Brief pause
        self.start()
    
    def get_next_prompt_time(self) -> str:
        """Get the time of the next scheduled prompt."""
        try:
            jobs = schedule.get_jobs()
            if not jobs:
                return "No prompts scheduled"
            
            next_run = min(job.next_run for job in jobs)
            if next_run:
                return next_run.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return "Next run time not available"
                
        except Exception as e:
            return f"Error getting next prompt time: {e}"
    
    def get_schedule_info(self) -> dict:
        """Get information about the current schedule."""
        interval_hours = self.settings.get('interval_hours', 1.0)
        start_time, end_time = self.settings.get_working_hours()
        weekdays_only = self.settings.get('weekdays_only', True)
        
        return {
            'running': self.running,
            'interval_hours': interval_hours,
            'start_time': start_time.strftime("%H:%M"),
            'end_time': end_time.strftime("%H:%M"),
            'weekdays_only': weekdays_only,
            'next_prompt': self.get_next_prompt_time(),
            'jobs_count': len(schedule.get_jobs()),
            'should_prompt_now': self.should_prompt_now()
        }


class ManualScheduler:
    """Simple scheduler for manual testing and immediate prompts."""
    
    def __init__(self, notification_system):
        self.notification_system = notification_system
    
    def trigger_prompt(self):
        """Manually trigger a prompt immediately."""
        previous_plan = self.notification_system.current_plan
        return self.notification_system.prompt_user_plan(previous_plan)