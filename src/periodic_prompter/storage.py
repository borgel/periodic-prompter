"""Persistent storage for user plans and logs."""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class PlanStorage:
    """Manages persistent storage of user plans and completion data."""
    
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = Path.home() / '.local' / 'share' / 'periodic_prompter'
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.plans_file = self.data_dir / 'plans.json'
        self.current_file = self.data_dir / 'current_state.json'
        
        # Initialize files if they don't exist
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Create data files if they don't exist."""
        if not self.plans_file.exists():
            self._save_json(self.plans_file, [])
        
        if not self.current_file.exists():
            self._save_json(self.current_file, {
                'current_plan': '',
                'plan_start_time': '',
                'last_completion_status': ''
            })
    
    def _load_json(self, file_path: Path) -> dict:
        """Load JSON data from file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {} if file_path == self.current_file else []
    
    def _save_json(self, file_path: Path, data):
        """Save data to JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
    
    def save_plan(self, plan: str, completion_status: str = '', previous_plan: str = ''):
        """Save a new plan entry."""
        timestamp = datetime.now().isoformat()
        
        # Load existing plans
        plans = self._load_json(self.plans_file)
        
        # Create plan entry
        plan_entry = {
            'timestamp': timestamp,
            'plan': plan,
            'previous_plan': previous_plan,
            'completion_status': completion_status,
            'completed': False  # Will be updated when next plan is set
        }
        
        # Mark previous plan as completed if exists
        if plans and completion_status:
            plans[-1]['completed'] = True
            plans[-1]['completion_status'] = completion_status
        
        plans.append(plan_entry)
        
        # Save updated plans
        self._save_json(self.plans_file, plans)
        
        # Update current state
        current_state = {
            'current_plan': plan,
            'plan_start_time': timestamp,
            'last_completion_status': completion_status
        }
        self._save_json(self.current_file, current_state)
        
        return plan_entry
    
    def get_current_plan(self) -> str:
        """Get the current active plan."""
        current_state = self._load_json(self.current_file)
        return current_state.get('current_plan', '')
    
    def get_last_plan(self) -> Optional[Dict]:
        """Get the last plan entry."""
        plans = self._load_json(self.plans_file)
        return plans[-1] if plans else None
    
    def get_plans_history(self, limit: int = 50) -> List[Dict]:
        """Get recent plans history."""
        plans = self._load_json(self.plans_file)
        return plans[-limit:] if plans else []
    
    def get_plans_for_date(self, date_str: str) -> List[Dict]:
        """Get all plans for a specific date (YYYY-MM-DD format)."""
        plans = self._load_json(self.plans_file)
        date_plans = []
        
        for plan in plans:
            try:
                plan_date = datetime.fromisoformat(plan['timestamp']).date().isoformat()
                if plan_date == date_str:
                    date_plans.append(plan)
            except:
                continue
        
        return date_plans
    
    def get_stats(self) -> Dict:
        """Get statistics about plans and completion."""
        plans = self._load_json(self.plans_file)
        
        if not plans:
            return {
                'total_plans': 0,
                'completed_plans': 0,
                'completion_rate': 0.0,
                'plans_this_week': 0,
                'plans_today': 0
            }
        
        total_plans = len(plans)
        completed_plans = sum(1 for p in plans if p.get('completed', False))
        completion_rate = (completed_plans / total_plans) * 100 if total_plans > 0 else 0
        
        # Count plans for current week and today
        now = datetime.now()
        today_str = now.date().isoformat()
        week_start = (now - datetime.timedelta(days=now.weekday())).date()
        
        plans_today = 0
        plans_this_week = 0
        
        for plan in plans:
            try:
                plan_date = datetime.fromisoformat(plan['timestamp']).date()
                if plan_date.isoformat() == today_str:
                    plans_today += 1
                if plan_date >= week_start:
                    plans_this_week += 1
            except:
                continue
        
        return {
            'total_plans': total_plans,
            'completed_plans': completed_plans,
            'completion_rate': completion_rate,
            'plans_this_week': plans_this_week,
            'plans_today': plans_today
        }


class LogWriter:
    """Handles writing logs to files in various formats."""
    
    def __init__(self, log_file_path: str):
        self.log_file_path = Path(log_file_path)
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def write_plan_log(self, plan_entry: Dict):
        """Write a plan entry to the log file."""
        try:
            timestamp = plan_entry['timestamp']
            plan = plan_entry['plan']
            completion = plan_entry.get('completion_status', '')
            previous = plan_entry.get('previous_plan', '')
            
            # Format log entry
            log_entry = f"[{timestamp}] Plan: {plan}"
            if previous:
                log_entry += f" | Previous: {previous} (Status: {completion})"
            log_entry += "\\n"
            
            # Append to log file
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def write_csv_log(self, plan_entry: Dict):
        """Write a plan entry to CSV format log."""
        try:
            csv_path = self.log_file_path.with_suffix('.csv')
            
            # Check if file exists to determine if we need headers
            write_headers = not csv_path.exists()
            
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                if write_headers:
                    writer.writerow(['timestamp', 'plan', 'previous_plan', 'completion_status', 'completed'])
                
                writer.writerow([
                    plan_entry['timestamp'],
                    plan_entry['plan'],
                    plan_entry.get('previous_plan', ''),
                    plan_entry.get('completion_status', ''),
                    plan_entry.get('completed', False)
                ])
                
        except Exception as e:
            print(f"Error writing to CSV log file: {e}")
    
    def export_all_plans(self, plans: List[Dict], format_type: str = 'txt'):
        """Export all plans to a file."""
        if format_type == 'csv':
            self._export_csv(plans)
        else:
            self._export_txt(plans)
    
    def _export_txt(self, plans: List[Dict]):
        """Export plans to text format."""
        try:
            export_path = self.log_file_path.with_name(f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write("Periodic Prompter - Plans Export\\n")
                f.write(f"Generated: {datetime.now().isoformat()}\\n\\n")
                
                for plan in plans:
                    f.write(f"[{plan['timestamp']}]\\n")
                    f.write(f"Plan: {plan['plan']}\\n")
                    if plan.get('previous_plan'):
                        f.write(f"Previous: {plan['previous_plan']} (Status: {plan.get('completion_status', 'Unknown')})\\n")
                    f.write(f"Completed: {plan.get('completed', False)}\\n\\n")
                    
            print(f"Plans exported to: {export_path}")
            
        except Exception as e:
            print(f"Error exporting plans: {e}")
    
    def _export_csv(self, plans: List[Dict]):
        """Export plans to CSV format."""
        try:
            export_path = self.log_file_path.with_name(f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'plan', 'previous_plan', 'completion_status', 'completed'])
                
                for plan in plans:
                    writer.writerow([
                        plan['timestamp'],
                        plan['plan'],
                        plan.get('previous_plan', ''),
                        plan.get('completion_status', ''),
                        plan.get('completed', False)
                    ])
                    
            print(f"Plans exported to CSV: {export_path}")
            
        except Exception as e:
            print(f"Error exporting CSV: {e}")