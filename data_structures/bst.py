class TreeNode:
    def __init__(self, key, item):
        self.key = key  # Represents the value to sort by (e.g., price, or name string)
        self.items = [item]  # Handle collisions (multiple items with same price)
        self.left = None
        self.right = None

class BinarySearchTree:
    """BST for fast O(log n) ordered traversal and search."""
    def __init__(self):
        self.root = None

    def insert(self, key, item):
        if self.root is None:
            self.root = TreeNode(key, item)
        else:
            self._insert_recursive(self.root, key, item)

    def _insert_recursive(self, node, key, item):
        if key == node.key:
            node.items.append(item)
        elif key < node.key:
            if node.left is None:
                node.left = TreeNode(key, item)
            else:
                self._insert_recursive(node.left, key, item)
        else:
            if node.right is None:
                node.right = TreeNode(key, item)
            else:
                self._insert_recursive(node.right, key, item)

    def in_order_traversal(self):
        """Returns a sorted list of items from lowest to highest key."""
        result = []
        self._in_order_recursive(self.root, result)
        return result

    def _in_order_recursive(self, node, result):
        if node:
            self._in_order_recursive(node.left, result)
            for item in node.items:
                result.append(item)
            self._in_order_recursive(node.right, result)

    def search(self, key):
        """Returns list of items matching the exact key, else empty []"""
        return self._search_recursive(self.root, key)

    def _search_recursive(self, node, key):
        if node is None:
            return []
        if key == node.key:
            return node.items
        if key < node.key:
            return self._search_recursive(node.left, key)
        return self._search_recursive(node.right, key)
