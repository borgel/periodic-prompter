"""Settings GUI interface for Periodic Prompter."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path


class SettingsWindow:
    """GUI window for configuring application settings."""
    
    def __init__(self, settings, scheduler=None, notification_system=None):
        self.settings = settings
        self.scheduler = scheduler
        self.notification_system = notification_system
        self.window = None
        self.vars = {}
        
    def show(self):
        """Show the settings window."""
        if self.window is not None:
            # Window already exists, just bring it to front
            self.window.lift()
            self.window.focus_force()
            return
        
        self.window = tk.Toplevel()
        self.window.title("Periodic Prompter Settings")
        self.window.geometry("500x600")
        self.window.resizable(True, True)
        
        # Make window modal and keep on top
        self.window.transient()
        self.window.grab_set()
        self.window.lift()
        self.window.focus_force()
        
        self._create_widgets()
        self._load_current_settings()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        timing_frame = ttk.Frame(notebook)
        logging_frame = ttk.Frame(notebook)
        
        notebook.add(timing_frame, text="Timing & Schedule")
        notebook.add(logging_frame, text="Logging")
        
        self._create_timing_tab(timing_frame)
        self._create_logging_tab(logging_frame)
        
        # Create button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        # Buttons
        ttk.Button(button_frame, text="Save", command=self._save_settings).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_close).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults).pack(side='left', padx=5)
    
    def _create_timing_tab(self, parent):
        """Create timing and schedule settings tab."""
        # Interval settings
        interval_frame = ttk.LabelFrame(parent, text="Prompt Interval", padding=10)
        interval_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(interval_frame, text="Prompt every:").grid(row=0, column=0, sticky='w', pady=2)
        
        self.vars['interval_hours'] = tk.DoubleVar()
        interval_spin = ttk.Spinbox(
            interval_frame, 
            from_=0.1, 
            to=24.0, 
            increment=0.1,
            textvariable=self.vars['interval_hours'],
            width=10
        )
        interval_spin.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(interval_frame, text="hours").grid(row=0, column=2, sticky='w', pady=2)
        
        ttk.Label(interval_frame, text="(Minimum: 0.1 hours = 6 minutes)", 
                 font=('Arial', 8)).grid(row=1, column=0, columnspan=3, sticky='w', pady=2)
        
        # Working hours settings
        hours_frame = ttk.LabelFrame(parent, text="Working Hours", padding=10)
        hours_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(hours_frame, text="Start time:").grid(row=0, column=0, sticky='w', pady=2)
        self.vars['start_time'] = tk.StringVar()
        start_combo = ttk.Combobox(
            hours_frame, 
            textvariable=self.vars['start_time'],
            values=[f"{h:02d}:00" for h in range(24)],
            width=8
        )
        start_combo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(hours_frame, text="End time:").grid(row=0, column=2, sticky='w', padx=(20,0), pady=2)
        self.vars['end_time'] = tk.StringVar()
        end_combo = ttk.Combobox(
            hours_frame, 
            textvariable=self.vars['end_time'],
            values=[f"{h:02d}:00" for h in range(24)],
            width=8
        )
        end_combo.grid(row=0, column=3, padx=5, pady=2)
        
        # Weekdays only
        self.vars['weekdays_only'] = tk.BooleanVar()
        ttk.Checkbutton(
            hours_frame, 
            text="Weekdays only (Monday-Friday)",
            variable=self.vars['weekdays_only']
        ).grid(row=1, column=0, columnspan=4, sticky='w', pady=5)
        
        # Prompt options
        options_frame = ttk.LabelFrame(parent, text="Prompt Options", padding=10)
        options_frame.pack(fill='x', padx=5, pady=5)
        
        self.vars['show_next_hour_prompt'] = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="Ask what you plan to do in the next hour",
            variable=self.vars['show_next_hour_prompt']
        ).pack(anchor='w', pady=2)
    
    def _create_logging_tab(self, parent):
        """Create logging settings tab."""
        # Enable logging
        logging_frame = ttk.LabelFrame(parent, text="Log Settings", padding=10)
        logging_frame.pack(fill='x', padx=5, pady=5)
        
        self.vars['create_log'] = tk.BooleanVar()
        log_checkbox = ttk.Checkbutton(
            logging_frame,
            text="Create log file",
            variable=self.vars['create_log'],
            command=self._toggle_log_options
        )
        log_checkbox.pack(anchor='w', pady=2)
        
        # Log file path
        self.log_frame = ttk.Frame(logging_frame)
        self.log_frame.pack(fill='x', pady=5)
        
        ttk.Label(self.log_frame, text="Log file path:").pack(anchor='w')
        
        path_frame = ttk.Frame(self.log_frame)
        path_frame.pack(fill='x', pady=2)
        
        self.vars['log_file_path'] = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.vars['log_file_path'])
        path_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ttk.Button(path_frame, text="Browse...", command=self._browse_log_file).pack(side='right')
        
        # Log format options
        format_frame = ttk.LabelFrame(parent, text="Export Options", padding=10)
        format_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(format_frame, text="Export Plans to Text", 
                  command=self._export_text).pack(side='left', padx=5, pady=2)
        ttk.Button(format_frame, text="Export Plans to CSV", 
                  command=self._export_csv).pack(side='left', padx=5, pady=2)
        
        # Statistics
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding=10)
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="Loading statistics...")
        self.stats_label.pack(anchor='w')
        
        self._update_statistics()
    
    def _toggle_log_options(self):
        """Enable/disable log options based on create_log checkbox."""
        if self.vars['create_log'].get():
            for widget in self.log_frame.winfo_children():
                self._enable_widget(widget)
        else:
            for widget in self.log_frame.winfo_children():
                self._disable_widget(widget)
    
    def _enable_widget(self, widget):
        """Enable a widget and its children."""
        try:
            widget.configure(state='normal')
        except:
            pass
        for child in widget.winfo_children():
            self._enable_widget(child)
    
    def _disable_widget(self, widget):
        """Disable a widget and its children."""
        try:
            widget.configure(state='disabled')
        except:
            pass
        for child in widget.winfo_children():
            self._disable_widget(child)
    
    def _browse_log_file(self):
        """Browse for log file location."""
        filename = filedialog.asksaveasfilename(
            title="Choose log file location",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="periodic_prompter_log.txt"
        )
        if filename:
            self.vars['log_file_path'].set(filename)
    
    def _export_text(self):
        """Export plans to text format."""
        if self.notification_system and hasattr(self.notification_system, 'storage'):
            plans = self.notification_system.storage.get_plans_history(1000)
            if plans:
                filename = filedialog.asksaveasfilename(
                    title="Export plans to text",
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                )
                if filename:
                    log_writer = self.notification_system.log_writer
                    if log_writer:
                        log_writer.log_file_path = Path(filename)
                        log_writer.export_all_plans(plans, 'txt')
                        messagebox.showinfo("Export Complete", f"Plans exported to {filename}")
            else:
                messagebox.showinfo("No Data", "No plans found to export.")
    
    def _export_csv(self):
        """Export plans to CSV format."""
        if self.notification_system and hasattr(self.notification_system, 'storage'):
            plans = self.notification_system.storage.get_plans_history(1000)
            if plans:
                filename = filedialog.asksaveasfilename(
                    title="Export plans to CSV",
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                )
                if filename:
                    log_writer = self.notification_system.log_writer
                    if log_writer:
                        log_writer.log_file_path = Path(filename)
                        log_writer.export_all_plans(plans, 'csv')
                        messagebox.showinfo("Export Complete", f"Plans exported to {filename}")
            else:
                messagebox.showinfo("No Data", "No plans found to export.")
    
    def _update_statistics(self):
        """Update statistics display."""
        if self.notification_system and hasattr(self.notification_system, 'storage'):
            stats = self.notification_system.storage.get_stats()
            stats_text = f"""Total plans: {stats['total_plans']}
Completed plans: {stats['completed_plans']}
Completion rate: {stats['completion_rate']:.1f}%
Plans this week: {stats['plans_this_week']}
Plans today: {stats['plans_today']}"""
            self.stats_label.config(text=stats_text)
    
    def _load_current_settings(self):
        """Load current settings into the GUI."""
        current = self.settings.get_all()
        
        self.vars['interval_hours'].set(current['interval_hours'])
        self.vars['start_time'].set(current['start_time'])
        self.vars['end_time'].set(current['end_time'])
        self.vars['weekdays_only'].set(current['weekdays_only'])
        self.vars['show_next_hour_prompt'].set(current['show_next_hour_prompt'])
        self.vars['create_log'].set(current['create_log'])
        self.vars['log_file_path'].set(current['log_file_path'])
        
        # Update log options state
        self._toggle_log_options()
    
    def _save_settings(self):
        """Save settings and close window."""
        try:
            # Validate interval
            interval = self.vars['interval_hours'].get()
            if interval < 0.1:
                messagebox.showerror("Invalid Input", "Interval must be at least 0.1 hours (6 minutes)")
                return
            
            # Prepare updates
            updates = {
                'interval_hours': interval,
                'start_time': self.vars['start_time'].get(),
                'end_time': self.vars['end_time'].get(),
                'weekdays_only': self.vars['weekdays_only'].get(),
                'show_next_hour_prompt': self.vars['show_next_hour_prompt'].get(),
                'create_log': self.vars['create_log'].get(),
                'log_file_path': self.vars['log_file_path'].get()
            }
            
            # Save settings
            self.settings.update_multiple(updates)
            
            # Restart scheduler if it exists
            if self.scheduler:
                self.scheduler.restart()
            
            # Update notification system log writer
            if self.notification_system:
                if updates['create_log']:
                    # Use absolute imports for packaging compatibility
                    try:
                        from periodic_prompter.storage import LogWriter
                    except ImportError:
                        from .storage import LogWriter
                    self.notification_system.log_writer = LogWriter(updates['log_file_path'])
                else:
                    self.notification_system.log_writer = None
            
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
            self._on_close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def _reset_defaults(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.settings.reset_to_defaults()
            self._load_current_settings()
            messagebox.showinfo("Settings Reset", "Settings have been reset to defaults.")
    
    def _on_close(self):
        """Handle window close event."""
        if self.window:
            self.window.grab_release()
            root = self.window.master
            self.window.destroy()
            self.window = None
            # Quit the Tkinter mainloop to clean up properly
            try:
                root.quit()
            except:
                pass