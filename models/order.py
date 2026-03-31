from datetime import datetime

class Order:
    def __init__(self, order_id, item_id, quantity, order_type, timestamp=None, username='System'):
        self.order_id = order_id
        self.item_id = item_id
        self.quantity = quantity
        self.order_type = order_type.upper()  # 'IN' (restock) or 'OUT' (sale)
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.username = username

    def __repr__(self):
        return f"<Order {self.order_id}: {self.order_type} {self.quantity} units of Item {self.item_id} by {self.username}>"
