from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                           QLineEdit, QComboBox, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt

class OrdersView(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        title = QLabel("Order Processing (Queue System)")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        form_layout = QHBoxLayout()
        
        self.item_combo = QComboBox()
        form_layout.addWidget(QLabel("Item:"))
        form_layout.addWidget(self.item_combo)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["IN (Restock)", "OUT (Sale)"])
        form_layout.addWidget(QLabel("Type:"))
        form_layout.addWidget(self.type_combo)
        
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(9999)
        form_layout.addWidget(QLabel("Qty:"))
        form_layout.addWidget(self.qty_spin)
        
        btn_queue = QPushButton("📥 Enqueue Order")
        btn_queue.clicked.connect(self.enqueue_order)
        form_layout.addWidget(btn_queue)
        
        layout.addLayout(form_layout)
        
        q_layout = QHBoxLayout()
        self.queue_status = QLabel("Pending Orders in Queue: 0")
        self.queue_status.setStyleSheet("color: #FAB387; font-weight: bold;")
        q_layout.addWidget(self.queue_status)
        
        btn_process = QPushButton("⚙️ Process Queue (FIFO)")
        btn_process.setStyleSheet("background-color: #A6E3A1; color: #11111B;")
        btn_process.clicked.connect(self.process_queue)
        q_layout.addWidget(btn_process)
        
        layout.addLayout(q_layout)
        
        layout.addWidget(QLabel("Order History (Traversed via Linked List):"))
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Order ID", "Item ID", "Item Name", "Op", "Resp. User", "Timestamp"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
    def refresh(self):
        self.item_combo.clear()
        items = self.manager.get_all_items()
        for item in items:
            self.item_combo.addItem(f"{item.item_id} - {item.name}", item.item_id)
            
        self.update_queue_label()
        self.load_history()
        
    def update_queue_label(self):
        size = self.manager.order_queue.size()
        self.queue_status.setText(f"Pending Orders in Queue: {size}")
        
    def enqueue_order(self):
        if self.item_combo.currentIndex() == -1:
            return
            
        item_id = self.item_combo.currentData()
        qty = self.qty_spin.value()
        type_str = "IN" if self.type_combo.currentIndex() == 0 else "OUT"
        
        self.manager.queue_order(item_id, qty, type_str)
        self.update_queue_label()
        
    def process_queue(self):
        processed = self.manager.process_order_queue()
        QMessageBox.information(self, "Queue Processed", f"Successfully processed {len(processed)} orders from the FIFO Queue.")
        self.update_queue_label()
        self.load_history()
        
    def load_history(self):
        self.table.setRowCount(0)
        history_list = self.manager.order_history.get_all()
        
        for order in history_list:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(order.order_id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(order.item_id)))
            
            item = self.manager.inventory_dict.get(order.item_id)
            item_name = item.name if item else "Unknown"
            self.table.setItem(row, 2, QTableWidgetItem(item_name))
            
            op_label = f"{order.order_type} " + ("(+)" if order.order_type == "IN" else "(-)") + str(order.quantity)
            item_op = QTableWidgetItem(op_label)
            if order.order_type == "IN":
                item_op.setForeground(Qt.GlobalColor.green)
            else:
                item_op.setForeground(Qt.GlobalColor.red)
                
            self.table.setItem(row, 3, item_op)
            self.table.setItem(row, 4, QTableWidgetItem(order.username))
            self.table.setItem(row, 5, QTableWidgetItem(str(order.timestamp)))
