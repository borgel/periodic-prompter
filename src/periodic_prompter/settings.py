"""Settings configuration system for Periodic Prompter."""

import json
import os
from pathlib import Path
from typing import Dict, Any
from datetime import time


class Settings:
    """Manages application settings with validation."""
    
    DEFAULT_SETTINGS = {
        'interval_hours': 1.0,
        'start_time': '09:00',
        'end_time': '18:00',
        'weekdays_only': True,
        'show_next_hour_prompt': True,
        'create_log': True,
        'log_file_path': str(Path.home() / 'periodic_prompter_log.txt'),
        'log_file_name': 'periodic_prompter_log.txt'
    }
    
    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = Path.home() / '.config' / 'periodic_prompter'
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'settings.json'
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file or create default settings."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)
                    # Update settings with saved values, keeping defaults for missing keys
                    self.settings.update(saved_settings)
                    self.validate_settings()
            else:
                self.save_settings()  # Create default settings file
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """Save current settings to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def validate_settings(self):
        """Validate and fix settings values."""
        # Validate interval
        if self.settings['interval_hours'] < 0.1:
            self.settings['interval_hours'] = 0.1
        elif self.settings['interval_hours'] > 24:
            self.settings['interval_hours'] = 24
        
        # Validate time format
        for time_key in ['start_time', 'end_time']:
            try:
                time_str = self.settings[time_key]
                if isinstance(time_str, str) and ':' in time_str:
                    hours, minutes = map(int, time_str.split(':'))
                    if 0 <= hours <= 23 and 0 <= minutes <= 59:
                        continue
                # If validation fails, use default
                self.settings[time_key] = self.DEFAULT_SETTINGS[time_key]
            except:
                self.settings[time_key] = self.DEFAULT_SETTINGS[time_key]
        
        # Validate boolean settings
        for bool_key in ['weekdays_only', 'show_next_hour_prompt', 'create_log']:
            if not isinstance(self.settings[bool_key], bool):
                self.settings[bool_key] = self.DEFAULT_SETTINGS[bool_key]
        
        # Validate log file path
        try:
            Path(self.settings['log_file_path']).parent.mkdir(parents=True, exist_ok=True)
        except:
            self.settings['log_file_path'] = self.DEFAULT_SETTINGS['log_file_path']
    
    def get(self, key: str, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a setting value."""
        self.settings[key] = value
        self.validate_settings()
        self.save_settings()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings."""
        return self.settings.copy()
    
    def update_multiple(self, updates: Dict[str, Any]):
        """Update multiple settings at once."""
        self.settings.update(updates)
        self.validate_settings()
        self.save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()
    
    def get_working_hours(self):
        """Get start and end time as time objects."""
        try:
            start_str = self.settings['start_time']
            end_str = self.settings['end_time']
            
            start_hours, start_minutes = map(int, start_str.split(':'))
            end_hours, end_minutes = map(int, end_str.split(':'))
            
            start_time = time(start_hours, start_minutes)
            end_time = time(end_hours, end_minutes)
            
            return start_time, end_time
        except:
            # Return defaults if parsing fails
            return time(9, 0), time(18, 0)
    
    def is_working_time(self, current_time=None):
        """Check if current time is within working hours."""
        if current_time is None:
            from datetime import datetime
            current_time = datetime.now().time()
        
        start_time, end_time = self.get_working_hours()
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:
            # Handle case where end time is next day (e.g., 22:00 to 06:00)
            return current_time >= start_time or current_time <= end_time
    
    def should_prompt_today(self):
        """Check if we should prompt today based on weekdays_only setting."""
        if not self.settings['weekdays_only']:
            return True
        
        from datetime import datetime
        today = datetime.now().weekday()
        return today < 5  # Monday=0, Sunday=6