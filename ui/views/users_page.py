from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog, QLineEdit)
from PyQt6.QtCore import Qt
from database import db_manager

class UsersView(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.failed_attempts = 0
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("System User Management (Admin Dashboard)")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #F38BA8;")
        layout.addWidget(title)
        
        subtitle = QLabel("Here you can securely audit all User registrations directly.")
        subtitle.setStyleSheet("font-size: 14px; margin-bottom: 20px; color: #BAC2DE;")
        layout.addWidget(subtitle)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["User ID", "Username", "Role", "Actions"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 400) # Increased to prevent 'Promote to Admin' cutoff
        
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        layout.addWidget(self.table)
        
    def refresh(self):
        self.table.setRowCount(0)
        users = db_manager.get_all_users()
        
        if not users:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("✨ No standard users found. The system is clean.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # empty_item.setForeground(Qt.GlobalColor.darkGray) # Optional subtle text
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 4)
            return
            
        for u in users:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(u[0])))
            
            uname = QTableWidgetItem(u[1])
            self.table.setItem(row, 1, uname)
            
            self.table.setItem(row, 2, QTableWidgetItem(u[2].upper()))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5,2,5,2)
            
            btn_promote = QPushButton("⬆️ Promote to Admin")
            btn_promote.setObjectName("PromoteBtn")
            btn_promote.setToolTip("Elevate this user to an Administrator role.")
            btn_promote.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_promote.clicked.connect(lambda checked, uname=u[1]: self.promote_user(uname))
            
            btn_delete = QPushButton("🚫 Disable User")
            btn_delete.setObjectName("BanBtn")
            btn_delete.setToolTip("Permanently disable this user's system access.")
            btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_delete.clicked.connect(lambda checked, user_id=u[0]: self.delete_user(user_id))
            
            actions_layout.addWidget(btn_promote)
            actions_layout.addWidget(btn_delete)
            self.table.setCellWidget(row, 3, actions_widget)
            
    def delete_user(self, user_id):
        reply = QMessageBox.question(self, 'Confirm Ban', 'Are you sure you want to permanently delete this user?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db_manager.delete_user(user_id)
            self.refresh()

    def promote_user(self, target_username):
        if self.failed_attempts >= 3:
            QMessageBox.critical(self, "Security Lock", "Too many failed attempts. Promotion blocked for this session.")
            return

        reply = QMessageBox.question(self, 'Confirm Promotion', f"Are you sure you want to promote '{target_username}' to Admin?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        pwd, ok = QInputDialog.getText(self, "Admin Verification", 
                                       f"Enter YOUR admin password to promote '{target_username}':",
                                       QLineEdit.EchoMode.Password)
        if not ok or not pwd.strip():
            return

        success, msg = db_manager.promote_to_admin(target_username, self.manager.current_username, pwd.strip())
        
        if success:
            self.failed_attempts = 0  # Reset counter upon successful validation
            QMessageBox.information(self, "Success", msg)
            self.refresh()
        else:
            if "Invalid admin credentials" in msg:
                self.failed_attempts += 1
                QMessageBox.warning(self, "Auth Failed", f"Invalid verification. Attempt {self.failed_attempts}/3")
            else:
                QMessageBox.warning(self, "Failed", msg)
