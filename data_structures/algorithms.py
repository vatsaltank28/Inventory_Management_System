def binary_search(arr, target_val, key_func=lambda x: x):
    """
    Binary search on a sorted array of objects.
    key_func extracts the value to compare against target_val.
    Assumes `arr` is pre-sorted based on `key_func`.
    """
    low = 0
    high = len(arr) - 1
    
    # Optional: ensure case-insensitive if working with strings
    if isinstance(target_val, str):
        target_val = target_val.lower()
        
    while low <= high:
        mid = (low + high) // 2
        mid_val = key_func(arr[mid])
        
        if isinstance(mid_val, str):
            mid_val = mid_val.lower()
            
        if mid_val == target_val:
            return arr[mid]
        elif mid_val < target_val:
            low = mid + 1
        else:
            high = mid - 1
            
    return None

def quick_sort(arr, key_func=lambda x: x, reverse=False):
    """
    Quick sort implementation (Divide and Conquer).
    Average Time Complexity: O(n log n)
    """
    if len(arr) <= 1:
        return arr
        
    # Safe pivot selection
    pivot = arr[len(arr) // 2]
    pivot_val = key_func(pivot)
    
    # Handle string lowercasing for consistent sort
    if isinstance(pivot_val, str):
        pivot_val = pivot_val.lower()
        
        left = [x for x in arr if str(key_func(x)).lower() < pivot_val]
        middle = [x for x in arr if str(key_func(x)).lower() == pivot_val]
        right = [x for x in arr if str(key_func(x)).lower() > pivot_val]
    else:
        left = [x for x in arr if key_func(x) < pivot_val]
        middle = [x for x in arr if key_func(x) == pivot_val]
        right = [x for x in arr if key_func(x) > pivot_val]
        
    if not reverse:
        return quick_sort(left, key_func, reverse) + middle + quick_sort(right, key_func, reverse)
    else:
        return quick_sort(right, key_func, reverse) + middle + quick_sort(left, key_func, reverse)
