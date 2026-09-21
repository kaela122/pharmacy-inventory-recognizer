"""Small shared helpers."""
def stock_status(stock: int, reorder: int) -> str:
    if stock <= 0:
        return "Out of Stock"
    if stock < reorder:
        return "Low Stock"
    return "In Stock"
