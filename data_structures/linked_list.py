class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    """Linked List to maintain order history in an ordered manner."""
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def prepend(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node

    def get_all(self):
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

    def is_empty(self):
        return self.head is None
