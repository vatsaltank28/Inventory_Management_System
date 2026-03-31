# Pro Inventory Manager (DSA Edition)

A full-fledged, modern Inventory Management System built in Python, showcasing robust Data Structures and Algorithms (DSA) combined with a sleek PyQt6 Dark Mode interface.

## Core Data Structures & Algorithms Implemented
- **HashMap (Python Dictionary)**: O(1) instantaneous item lookups via the `InventoryManager` core controller.
- **Linked List**: Maintaining a sequential order history log without array reallocation overhead (`data_structures/linked_list.py`).
- **Stack**: Providing powerful Undo functionality for item modifications/deletions (`data_structures/stack.py`).
- **Queue**: Managing pending Restock (IN) / Sale (OUT) orders using a strict FIFO algorithm (`data_structures/queue.py`).
- **Binary Search Tree (BST)**: Guaranteeing fast ordered sequential retrieval of items (`data_structures/bst.py`).
- **Graph**: Adjacency List representing the relationships between Suppliers and Item nodes (`data_structures/graph.py`).
- **Binary Search & QuickSort**: O(log n) searching and O(N log N) sorting implementations used directly within the Inventory Table for fast GUI responsiveness (`data_structures/algorithms.py`).

## Tech Stack
- **Language**: Python 3.9+
- **Database**: SQLite3 (Persistent storage syncing with in-memory structures)
- **GUI**: PyQt6 (Custom CSS/QSS styling)
- **Charting**: Matplotlib (Dashboard visually reporting stock volumes)

## Setup Instructions

1. **Open your terminal inside this folder.**
2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application:**
   ```bash
   python main.py
   ```

### Default Login
- **Username**: `admin`
- **Password**: `admin`
