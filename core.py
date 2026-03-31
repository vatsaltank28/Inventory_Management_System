from database import db_manager
from models.item import Item
from models.order import Order
from data_structures.linked_list import LinkedList
from data_structures.stack import Stack
from data_structures.queue import OrderQueue
from data_structures.bst import BinarySearchTree
from data_structures.graph import SupplierGraph

class InventoryManager:
    def __init__(self, current_user=None):
        db_manager.init_db()
        
        # User tuple: (id, username, password, role)
        self.current_user = current_user
        
        # Primary HashMap for O(1) lookup
        self.inventory_dict = {}  
        
        # Linked List for sequential log
        self.order_history = LinkedList()
        
        # Stack for Undo
        self.undo_stack = Stack()
        
        # Queue for pending orders
        self.order_queue = OrderQueue()
        
        # Binary Search Trees for sorted retrievals
        self.price_bst = BinarySearchTree()
        
        # Graph for Supplier-Item mapping
        self.supplier_graph = SupplierGraph()
        
        self.load_data()
        
    @property
    def current_role(self):
        return self.current_user[3] if self.current_user else 'user'
        
    @property
    def current_username(self):
        return self.current_user[1] if self.current_user else 'System'
        
    def load_data(self):
        self.inventory_dict.clear()
        self.price_bst = BinarySearchTree()
        self.supplier_graph.clear()
        
        # Load items
        items_data = db_manager.execute_query("SELECT * FROM items", fetch=True)
        for row in items_data:
            item = Item(*row)
            self._add_to_structures(item)
            
        # Load orders into LinkedList
        self.order_history = LinkedList()
        orders_data = db_manager.execute_query("SELECT * FROM orders ORDER BY order_id", fetch=True)
        for row in orders_data:
            if len(row) == 5:
                order = Order(*row, username='System')
            else:
                order = Order(*row)
            self.order_history.append(order)

    def _add_to_structures(self, item):
        self.inventory_dict[item.item_id] = item
        self.price_bst.insert(item.price, item)
        self.supplier_graph.add_item_to_supplier(item.supplier, item.item_id)

    def add_item(self, name, stock, price, category, supplier):
        item_id = db_manager.execute_query(
            "INSERT INTO items (name, stock, price, category, supplier) VALUES (?, ?, ?, ?, ?)",
            (name, stock, price, category, supplier), fetch=False
        )
        item = Item(item_id, name, stock, price, category, supplier)
        self._add_to_structures(item)
        
        # Add to stack for undo
        self.undo_stack.push({'action': 'add', 'item': item})
        return item
        
    def update_item(self, item_id, name, stock, price, category, supplier):
        if item_id in self.inventory_dict:
            old_item = self.inventory_dict[item_id]
            old_state = Item(old_item.item_id, old_item.name, old_item.stock, old_item.price, old_item.category, old_item.supplier)
            self.undo_stack.push({'action': 'update', 'item': old_state})
            
            db_manager.execute_query(
                "UPDATE items SET name=?, stock=?, price=?, category=?, supplier=? WHERE id=?",
                (name, stock, price, category, supplier, item_id), fetch=False
            )
            self.load_data()
            return True
        return False

    def delete_item(self, item_id):
        if item_id in self.inventory_dict:
            item = self.inventory_dict[item_id]
            self.undo_stack.push({'action': 'delete', 'item': item})
            
            db_manager.execute_query("DELETE FROM items WHERE id=?", (item_id,), fetch=False)
            self.load_data()
            return True
        return False
        
    def undo_last_action(self):
        last_action = self.undo_stack.pop()
        if not last_action:
            return False
            
        action = last_action['action']
        item = last_action['item']
        
        if action == 'add':
            db_manager.execute_query("DELETE FROM items WHERE id=?", (item.item_id,), fetch=False)
        elif action == 'delete':
            db_manager.execute_query(
                "INSERT INTO items (id, name, stock, price, category, supplier) VALUES (?, ?, ?, ?, ?, ?)",
                (item.item_id, item.name, item.stock, item.price, item.category, item.supplier), fetch=False
            )
        elif action == 'update':
            db_manager.execute_query(
                "UPDATE items SET name=?, stock=?, price=?, category=?, supplier=? WHERE id=?",
                (item.name, item.stock, item.price, item.category, item.supplier, item.item_id), fetch=False
            )
            
        self.load_data()
        return True
        
    def queue_order(self, item_id, quantity, order_type):
        self.order_queue.enqueue({'item_id': item_id, 'quantity': quantity, 'type': order_type})
        
    def process_order_queue(self):
        processed = []
        while not self.order_queue.is_empty():
            order_data = self.order_queue.dequeue()
            item_id = order_data['item_id']
            quantity = order_data['quantity']
            order_type = order_data['type']
            
            if item_id in self.inventory_dict:
                item = self.inventory_dict[item_id]
                new_stock = item.stock
                if order_type == 'IN':
                    new_stock += quantity
                elif order_type == 'OUT':
                    if item.stock >= quantity:
                        new_stock -= quantity
                    else:
                        continue # Skip invalid order
                        
                # Update DB
                db_manager.execute_query("UPDATE items SET stock=? WHERE id=?", (new_stock, item_id), fetch=False)
                
                # Log order with auditing track (who did it)
                order_id = db_manager.execute_query(
                    "INSERT INTO orders (item_id, quantity, order_type, timestamp, username) VALUES (?, ?, ?, datetime('now'), ?)",
                    (item_id, quantity, order_type, self.current_username), fetch=False
                )
                
                # Process successfully
                item.stock = new_stock
                order_obj = Order(order_id, item_id, quantity, order_type, username=self.current_username)
                self.order_history.append(order_obj)
                processed.append(order_obj)
        return processed
        
    def get_all_items(self):
        return list(self.inventory_dict.values())
        
    def get_low_stock_items(self, threshold=10):
        return [item for item in self.get_all_items() if item.stock <= threshold]
