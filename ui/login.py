from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from database import db_manager

class RegisterWindow(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("Inventory System - Register")
        self.setFixedSize(400, 350)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("📝 Register Account")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a Username")
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Choose a Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        self.reg_btn = QPushButton("Register")
        self.reg_btn.clicked.connect(self.handle_register)
        self.reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reg_btn.setStyleSheet("margin-top: 15px;")
        layout.addWidget(self.reg_btn)
        
        self.back_btn = QPushButton("Back to Login")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setStyleSheet("background-color: transparent; color: #89B4FA; font-weight: normal; text-decoration: underline;")
        layout.addWidget(self.back_btn)
        
        self.setLayout(layout)
        
    def handle_register(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, "Error", "Username and Password cannot be empty.")
            return
            
        success, msg = db_manager.register_user(user, pwd)
        if success:
            QMessageBox.information(self, "Success", msg + "\nYou can now login.")
            self.go_back()
        else:
            QMessageBox.warning(self, "Error", msg)
            
    def go_back(self):
        self.login_window.username_input.setText(self.username_input.text())
        self.login_window.password_input.setText(self.password_input.text())
        self.login_window.show()
        self.close()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory System - Login")
        self.setFixedSize(400, 350)
        self.admin_failed_attempts = {}
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("📦 Inventory Login")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("margin-top: 15px;")
        layout.addWidget(self.login_btn)
        
        self.reg_btn = QPushButton("Don't have an account? Register Here")
        self.reg_btn.setStyleSheet("background-color: transparent; color: #89B4FA; font-weight: normal; text-decoration: underline;")
        self.reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reg_btn.clicked.connect(self.open_register)
        layout.addWidget(self.reg_btn)
        
        self.setLayout(layout)
        
    def handle_login(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text().strip()
        
        # Check if user is locked
        if self.admin_failed_attempts.get(user, 0) >= 3:
            QMessageBox.critical(self, "Security Lock", "Account temporarily locked due to 3 failed admin login attempts.")
            return
        
        # Check against database natively 
        auth_user = db_manager.authenticate_user(user, pwd)
        if auth_user:
            self.admin_failed_attempts[user] = 0 # Reset on success
            self.main_window = MainWindow(auth_user)
            self.main_window.show()
            self.close()
        else:
            # Check if attempting admin login
            user_record = db_manager.execute_query("SELECT role FROM users WHERE username=?", (user,), fetch=True)
            if user_record and user_record[0][0] == 'admin':
                self.admin_failed_attempts[user] = self.admin_failed_attempts.get(user, 0) + 1
                attempts_left = 3 - self.admin_failed_attempts[user]
                QMessageBox.warning(self, "Auth Failed", f"Invalid admin credentials. {attempts_left} attempts remaining.")
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials. Please try again or register.")
            
    def open_register(self):
        self.reg_window = RegisterWindow(self)
        self.reg_window.show()
        self.hide()
