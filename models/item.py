class Item:
    def __init__(self, item_id, name, stock, price, category, supplier):
        self.item_id = item_id
        self.name = name
        self.stock = stock
        self.price = price
        self.category = category
        self.supplier = supplier

    def __repr__(self):
        return f"<Item {self.item_id}: {self.name} | Stock: {self.stock} | Price: ₹{self.price:.2f}>"

    def update_stock(self, amount):
        """Update stock level. Positive for addition, negative for deduction."""
        self.stock += amount
