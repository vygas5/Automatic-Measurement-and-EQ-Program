import os
import subprocess
import sys
from pathlib import Path

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_script_path(script_name):
    """Get the full path to a script in the same directory as this menu."""
    script_dir = Path(__file__).parent
    return script_dir / script_name 

def run_script(script_name):
    """Run a Python script with error handling."""
    script_path = get_script_path(script_name)
    
    print(f"\nRunning {script_name}...")
    print(f"Path: {script_path}")
    
    if not script_path.exists():
        print(f"Error: {script_name} not found at {script_path}")
        return
    
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
    except Exception as e:
        print(f"Unexpected error running {script_name}: {e}")

def run_both():
    """Run both scripts sequentially."""
    run_script("MeasurePlot.py")
    run_script("EQ.py")

def display_menu():
    """Display the main menu."""
    clear_screen()
    print(f"""
    ************************************
    *  AutoEqualisation for APO - Menu  *
    ************************************

    1. Run MeasurePlot.py
    2. Run EQ.py
    3. Run Both (MeasurePlot first, then EQ)
    4. Run MeasureSpeaker
    0. Exit

    Current directory: {Path(__file__).parent}
    """)

def main():
    """Main function to run the menu."""
    missing = []
    for script in ["MeasurePlot.py", "EQ.py"]:
        if not get_script_path(script).exists():
            missing.append(script)
    
    if missing:
        print(f"Warning: The following scripts are missing: {', '.join(missing)}")
        print("Please ensure they're in the same directory as this menu.")
        input("Press Enter to continue anyway...")

    while True:
        display_menu()
        choice = input("Enter your choice (0-3): ").strip()

        if choice == '1':
            run_script("MeasurePlot.py")
        elif choice == '2':
            run_script("EQ.py")
        elif choice == '3':
            run_both()
        elif choice == '4':
            run_script("MeasureSpeaker.py")
        elif choice == '0':
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 0 and 3.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()