import csv
import os
from datetime import datetime

def export_to_csv(items, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"inventory_export_{timestamp}.csv"
        
    filepath = os.path.join(os.getcwd(), filename)
    
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Stock", "Price", "Category", "Supplier"])
        
        for item in items:
            writer.writerow([item.item_id, item.name, item.stock, f"₹{item.price:.2f}", item.category, item.supplier])
            
    return filepath
