from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                           QLineEdit, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from ui.views.item_form import ItemFormWindow
from data_structures.algorithms import binary_search, quick_sort

class InventoryView(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.is_admin = (self.manager.current_role == 'admin')
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Top Bar
        top_bar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search exact ID (BinarySearch) or Keyword...")
        self.search_input.textChanged.connect(self.handle_search)
        top_bar.addWidget(self.search_input)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Sort: ID (Default)", "Sort: Price (QuickSort)", "Sort: Stock"])
        self.sort_combo.currentIndexChanged.connect(self.handle_sort)
        top_bar.addWidget(self.sort_combo)
        
        self.btn_add = QPushButton("➕ Add Item")
        self.btn_add.clicked.connect(self.open_add_form)
        
        self.btn_undo = QPushButton("↩️ Undo Stack")
        self.btn_undo.clicked.connect(self.handle_undo)
        
        if self.is_admin:
            top_bar.addWidget(self.btn_add)
            top_bar.addWidget(self.btn_undo)
        else:
            self.btn_add.hide()
            self.btn_undo.hide()
            
        layout.addLayout(top_bar)
        
        # Table dynamically resize columns based on role
        cols = 7 if self.is_admin else 6
        self.table = QTableWidget(0, cols)
        
        headers = ["ID", "Name", "Stock", "Price", "Category", "Supplier"]
        if self.is_admin:
            headers.append("Actions")
            
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
    def refresh(self):
        self.handle_sort()
        
    def load_table_data(self, items):
        self.table.setRowCount(0)
        for item in items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item.item_id)))
            self.table.setItem(row, 1, QTableWidgetItem(item.name))
            
            # Highlight low stock
            stock_item = QTableWidgetItem(str(item.stock))
            if item.stock <= 10:
                stock_item.setForeground(Qt.GlobalColor.red)
                
            self.table.setItem(row, 2, stock_item)
            self.table.setItem(row, 3, QTableWidgetItem(f"${item.price:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(item.category))
            self.table.setItem(row, 5, QTableWidgetItem(item.supplier))
            
            if self.is_admin:
                # Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5,2,5,2)
                
                btn_edit = QPushButton("✏️")
                btn_edit.clicked.connect(lambda checked, i=item: self.open_edit_form(i))
                
                btn_delete = QPushButton("❌")
                btn_delete.setStyleSheet("background-color: #F38BA8; color: #11111B;")
                btn_delete.clicked.connect(lambda checked, i_id=item.item_id: self.delete_item(i_id))
                
                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_delete)
                self.table.setCellWidget(row, 6, actions_widget)

    def handle_search(self):
        query = self.search_input.text().strip()
        items = self.manager.get_all_items()
        
        if not query:
            self.handle_sort()
            return

        if query.isdigit():
            target_id = int(query)
            sorted_by_id = quick_sort(items, key_func=lambda x: x.item_id)
            result = binary_search(sorted_by_id, target_id, key_func=lambda x: x.item_id)
            if result:
                self.load_table_data([result])
            else:
                self.load_table_data([])
        else:
            filtered = [item for item in items if query.lower() in item.name.lower() or query.lower() in item.category.lower()]
            self.load_table_data(filtered)

    def handle_sort(self):
        items = self.manager.get_all_items()
        if not items:
            self.load_table_data([])
            return
            
        idx = self.sort_combo.currentIndex()
        query = self.search_input.text().strip()
        if query: 
            return
        
        if idx == 0:
            sorted_items = quick_sort(items, key_func=lambda x: x.item_id)
        elif idx == 1:
            sorted_items = quick_sort(items, key_func=lambda x: x.price)
        else:
            sorted_items = quick_sort(items, key_func=lambda x: x.stock)
            
        self.load_table_data(sorted_items)

    def open_add_form(self):
        self.form = ItemFormWindow(self.manager, self)
        self.form.show()
        
    def open_edit_form(self, item):
        self.form = ItemFormWindow(self.manager, self, item)
        self.form.show()

    def delete_item(self, item_id):
        reply = QMessageBox.question(self, 'Confirm Delete', 'Are you sure you want to delete this item? This action is pushed to the Undo Stack.',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.manager.delete_item(item_id)
            self.refresh()
            
    def handle_undo(self):
        if self.manager.undo_last_action():
            self.refresh()
            QMessageBox.information(self, "Undo Success", "Last action reverted via Stack.pop()")
        else:
            QMessageBox.information(self, "Undo", "The Undo Stack is empty!")
