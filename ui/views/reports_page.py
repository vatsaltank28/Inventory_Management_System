from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
from utils.export import export_to_csv
from utils.notifications import check_low_stock

class ReportsView(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Reports & Analytics")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Supplier Graph mapping
        layout.addWidget(QLabel("\nSupplier Graph Connectivity (Adjacency List):"))
        self.supplier_table = QTableWidget(0, 2)
        self.supplier_table.setHorizontalHeaderLabels(["Supplier Node", "Connected Item IDs (Edges)"])
        self.supplier_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.supplier_table)
        
        # BST Data Output
        layout.addWidget(QLabel("\nItems via Binary Search Tree In-Order Traversal (Fast Ordered Read):"))
        self.bst_table = QTableWidget(0, 3)
        self.bst_table.setHorizontalHeaderLabels(["Price Key", "Item ID", "Item Name"])
        self.bst_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.bst_table)
        
        btn_export = QPushButton("📥 Export Full Inventory to CSV")
        btn_export.setStyleSheet("background-color: #CBA6F7; color: #11111B; padding: 12px; margin-top: 20px;")
        btn_export.clicked.connect(self.export_csv)
        layout.addWidget(btn_export)
        
    def refresh(self):
        # Alerts
        alerts = check_low_stock(self.manager, threshold=10)
        if alerts:
            alert_str = "\n".join(alerts)
            QMessageBox.warning(self, "Low Stock Alert", "The following items are running low:\n\n" + alert_str)
            
        # Draw Supplier Graph table
        self.supplier_table.setRowCount(0)
        suppliers = self.manager.supplier_graph.get_all_suppliers()
        for supplier in suppliers:
            row = self.supplier_table.rowCount()
            self.supplier_table.insertRow(row)
            self.supplier_table.setItem(row, 0, QTableWidgetItem(supplier))
            
            items = self.manager.supplier_graph.get_supplier_items(supplier)
            self.supplier_table.setItem(row, 1, QTableWidgetItem(str(items)))
            
        # Draw BST Table
        self.bst_table.setRowCount(0)
        sorted_items = self.manager.price_bst.in_order_traversal()
        for item in sorted_items:
            row = self.bst_table.rowCount()
            self.bst_table.insertRow(row)
            self.bst_table.setItem(row, 0, QTableWidgetItem(f"${item.price:.2f}"))
            self.bst_table.setItem(row, 1, QTableWidgetItem(str(item.item_id)))
            self.bst_table.setItem(row, 2, QTableWidgetItem(item.name))

    def export_csv(self):
        items = self.manager.get_all_items()
        if not items:
            QMessageBox.information(self, "Export", "Inventory is empty!")
            return
            
        filepath = export_to_csv(items)
        QMessageBox.information(self, "Export Success", f"Inventory exported successfully to:\n{filepath}")
