from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QDoubleSpinBox, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt

class ItemFormWindow(QWidget):
    def __init__(self, manager, parent_view, item=None):
        super().__init__()
        self.manager = manager
        self.parent_view = parent_view
        self.item = item
        
        self.setWindowTitle("Edit Item" if item else "Add New Item")
        self.setFixedSize(400, 450)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Name
        layout.addWidget(QLabel("Item Name:"))
        self.name_in = QLineEdit()
        layout.addWidget(self.name_in)
        
        # Category
        layout.addWidget(QLabel("Category:"))
        self.cat_in = QLineEdit()
        layout.addWidget(self.cat_in)
        
        # Supplier
        layout.addWidget(QLabel("Supplier:"))
        self.sup_in = QLineEdit()
        layout.addWidget(self.sup_in)
        
        # Price
        layout.addWidget(QLabel("Price ($):"))
        self.price_in = QDoubleSpinBox()
        self.price_in.setMaximum(999999.99)
        layout.addWidget(self.price_in)
        
        # Stock (only editable on Add, otherwise use Orders to restock)
        layout.addWidget(QLabel("Initial Stock:"))
        self.stock_in = QSpinBox()
        self.stock_in.setMaximum(999999)
        if item:
            self.stock_in.setDisabled(True)
        layout.addWidget(self.stock_in)
        
        if item:
            self.name_in.setText(item.name)
            self.cat_in.setText(item.category)
            self.sup_in.setText(item.supplier)
            self.price_in.setValue(item.price)
            self.stock_in.setValue(item.stock)
            
        btn_save = QPushButton("Save Item")
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)
        
    def save(self):
        name = self.name_in.text().strip()
        cat = self.cat_in.text().strip()
        sup = self.sup_in.text().strip()
        price = self.price_in.value()
        stock = self.stock_in.value()
        
        if not name or not cat or not sup:
            QMessageBox.warning(self, "Error", "All fields are required!")
            return
            
        if self.item:
            self.manager.update_item(self.item.item_id, name, self.item.stock, price, cat, sup)
        else:
            self.manager.add_item(name, stock, price, cat, sup)
            
        self.parent_view.refresh()
        self.close()
