"""Simple setup script for py2app packaging without argv emulation."""

from setuptools import setup, find_packages
import sys
import os

# Add src directory to path so we can find the package
sys.path.insert(0, 'src')

APP = ['app_main.py']
DATA_FILES = []

# Copy the entire package to the resources
package_data = []
for root, dirs, files in os.walk('src/periodic_prompter'):
    for file in files:
        if file.endswith('.py'):
            rel_path = os.path.relpath(os.path.join(root, file), 'src')
            package_data.append(rel_path)

OPTIONS = {
    'argv_emulation': False,
    'site_packages': False,
    'strip': True,
    'optimize': 2,
    'packages': ['rumps', 'plyer', 'schedule', 'tkinter'],
    'includes': [
        'periodic_prompter',
        'periodic_prompter.main_rumps',
        'periodic_prompter.notifications',
        'periodic_prompter.settings', 
        'periodic_prompter.storage',
        'periodic_prompter.scheduler',
        'periodic_prompter.settings_gui'
    ],
    'excludes': [
        'matplotlib', 'numpy', 'scipy', 'Carbon', 'wx', 'pygame',
        'tkinter.test', 'test', 'unittest', 'lib2to3',
        'pydoc', 'doctest', 'django', 'flask', 'tornado'
    ],
    'frameworks': [],
    'resources': ['src/periodic_prompter'],
    'plist': {
        'CFBundleName': 'Periodic Prompter',
        'CFBundleDisplayName': 'Periodic Prompter',
        'CFBundleIdentifier': 'com.user.periodic-prompter',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'LSUIElement': True,
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
        'NSSupportsAutomaticGraphicsSwitching': True,
        'LSApplicationCategoryType': 'public.app-category.productivity'
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)