#!/usr/bin/env python3
"""Build script for creating macOS .app bundle."""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """Main build function."""
    print("Building Periodic Prompter macOS app...")
    
    # Clean previous builds
    build_dirs = ['build', 'dist']
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Run py2app
    print("Running py2app...")
    try:
        result = subprocess.run([
            sys.executable, 'setup.py', 'py2app'
        ], check=True, capture_output=True, text=True)
        
        print("Build successful!")
        print(result.stdout)
        
        # Check if app was created
        final_path = Path('dist/Periodic Prompter.app')
        if final_path.exists():
            print(f"App created at: {final_path.absolute()}")
            
            # Create a symbolic link for easy access
            link_path = Path('Periodic Prompter.app')
            if link_path.exists():
                link_path.unlink()
            link_path.symlink_to(final_path.absolute())
            
            print("\\nBuild complete! You can now:")
            print(f"1. Run the app: open '{final_path}'")
            print("2. Move it to Applications folder")
            print(f"3. Run from command line: '{final_path}/Contents/MacOS/Periodic Prompter'")
            
        else:
            print("ERROR: App was not created")
            return 1
            
    except subprocess.CalledProcessError as e:
        print("Build failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())