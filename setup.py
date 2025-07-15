"""Setup script for py2app packaging."""

from setuptools import setup

APP = ['src/periodic_prompter/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PIL', 'pystray', 'plyer', 'schedule', 'tkinter'],
    'includes': [
        'periodic_prompter.notifications',
        'periodic_prompter.settings', 
        'periodic_prompter.storage',
        'periodic_prompter.scheduler',
        'periodic_prompter.settings_gui'
    ],
    'excludes': [
        'matplotlib', 'numpy', 'scipy', 'Carbon', 'wx', 'pygame',
        'tkinter.test', 'test', 'unittest', 'lib2to3'
    ],
    'frameworks': [],  # Don't include deprecated frameworks
    'plist': {
        'CFBundleName': 'Periodic Prompter',
        'CFBundleDisplayName': 'Periodic Prompter',
        'CFBundleIdentifier': 'com.user.periodic-prompter',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'LSUIElement': True,  # Run as background app (no dock icon)
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0'  # Require Catalina or later
    },
    'iconfile': None,  # We'll create a proper icon later
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)