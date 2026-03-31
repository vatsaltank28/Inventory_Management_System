from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
from database import db_manager

class UsersView(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("System User Management (Admin Dashboard)")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #F38BA8;")
        layout.addWidget(title)
        
        subtitle = QLabel("Here you can securely audit all User registrations directly.")
        subtitle.setStyleSheet("margin-bottom: 20px; color: #A6ADC8;")
        layout.addWidget(subtitle)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["User ID", "Username", "Role", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
    def refresh(self):
        self.table.setRowCount(0)
        users = db_manager.get_all_users()
        
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
            
            btn_delete = QPushButton("🗑️ Ban System Access")
            btn_delete.setStyleSheet("background-color: #F38BA8; color: #11111B;")
            btn_delete.clicked.connect(lambda checked, user_id=u[0]: self.delete_user(user_id))
            
            actions_layout.addWidget(btn_delete)
            self.table.setCellWidget(row, 3, actions_widget)
            
    def delete_user(self, user_id):
        reply = QMessageBox.question(self, 'Confirm Ban', 'Are you sure you want to permanently delete this user?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db_manager.delete_user(user_id)
            self.refresh()
