class SupplierGraph:
    """Graph to map many-to-many relationship between suppliers and item categories/ids."""
    def __init__(self):
        # Uses an adjacency list representation
        self.graph = {}

    def add_supplier(self, supplier):
        if supplier not in self.graph:
            self.graph[supplier] = []

    def add_item_to_supplier(self, supplier, item_id):
        if supplier not in self.graph:
            self.add_supplier(supplier)
        if item_id not in self.graph[supplier]:
            self.graph[supplier].append(item_id)

    def remove_item_from_supplier(self, supplier, item_id):
        if supplier in self.graph and item_id in self.graph[supplier]:
            self.graph[supplier].remove(item_id)

    def get_supplier_items(self, supplier):
        return self.graph.get(supplier, [])
        
    def get_all_suppliers(self):
        return list(self.graph.keys())
        
    def clear(self):
        self.graph = {}
