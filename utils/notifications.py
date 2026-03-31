def check_low_stock(inventory_manager, threshold=10):
    """Returns a list of messages for items below the threshold."""
    low_stock = inventory_manager.get_low_stock_items(threshold)
    notifications = []
    for item in low_stock:
        warnings = f"⚠️ Low Stock Alert: {item.name} has only {item.stock} units left!"
        notifications.append(warnings)
    return notifications
