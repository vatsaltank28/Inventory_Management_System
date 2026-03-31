from collections import deque

class OrderQueue:
    """Queue implementation to manage pending orders in FIFO order."""
    def __init__(self):
        # We use deque for O(1) appends and pops from both ends
        self.items = deque()
        
    def enqueue(self, item):
        self.items.append(item)
        
    def dequeue(self):
        if not self.is_empty():
            return self.items.popleft()
        return None
        
    def is_empty(self):
        return len(self.items) == 0
        
    def size(self):
        return len(self.items)

    def peek(self):
        if not self.is_empty():
            return self.items[0]
        return None
