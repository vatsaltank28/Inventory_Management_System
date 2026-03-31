import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.login import LoginWindow

# Create app data directories if they don't exist
os.makedirs('data_structures', exist_ok=True)
os.makedirs('database', exist_ok=True)

def main():
    app = QApplication(sys.argv)
    
    # Load stylesheet
    try:
        with open('ui/styles.qss', 'r') as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Warning: Could not load stylesheet: {e}")
        
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
