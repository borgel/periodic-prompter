"""Wrapper script for the packaged application."""

import sys
import os

# Fix for Carbon framework issues on modern macOS
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

def setup_paths():
    """Setup Python paths for package discovery."""
    # Get the resource path
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        resource_path = sys._MEIPASS
    else:
        # Running as py2app bundle or in development
        resource_path = os.environ.get('RESOURCEPATH', os.path.dirname(os.path.abspath(__file__)))
    
    # Add various potential paths
    paths_to_try = [
        resource_path,
        os.path.join(resource_path, 'src'),
        os.path.join(resource_path, 'lib', 'python3.13'),
        os.path.join(resource_path, 'lib', 'python3.13', 'site-packages'),
        os.path.dirname(os.path.abspath(__file__)),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    ]
    
    for path in paths_to_try:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)

def main():
    """Main entry point."""
    setup_paths()
    
    # Debug: print sys.path and try to find the module
    print("Python path:")
    for path in sys.path:
        print(f"  {path}")
    
    print("\nLooking for periodic_prompter module...")
    
    # Try multiple import strategies
    try:
        # First try direct import
        from periodic_prompter.main import main as app_main
        print("✓ Found periodic_prompter.main")
        app_main()
    except ImportError as e1:
        print(f"✗ Direct import failed: {e1}")
        
        try:
            # Try adding current directory to path and importing
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(current_dir, 'src')
            if os.path.exists(src_dir):
                sys.path.insert(0, src_dir)
                from periodic_prompter.main import main as app_main
                print("✓ Found periodic_prompter.main from src/")
                app_main()
            else:
                raise ImportError("Could not find periodic_prompter package")
        except ImportError as e2:
            print(f"✗ Src import failed: {e2}")
            
            # List what we can find
            print("\nAvailable in resource path:")
            resource_path = os.environ.get('RESOURCEPATH', os.path.dirname(os.path.abspath(__file__)))
            for item in os.listdir(resource_path):
                print(f"  {item}")
            
            raise ImportError(f"Could not import periodic_prompter module: {e1}, {e2}")

if __name__ == "__main__":
    main()