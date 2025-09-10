from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importer les modèles pour lier les tables au metadata
from .user_model import User          # noqa: E402,F401
from .book_model import Book          # noqa: E402,F401
from .author_model import Author      # noqa: E402,F401
from .category_model import Category  # noqa: E402,F401
from .order_model import Order        # noqa: E402,F401
from .order_details_model import OrderDetail  # noqa: E402,F401
from .cart_items_model import CartItem        # noqa: E402,F401

__all__ = [
    "db", "User", "Book", "Author", "Category",
    "Order", "OrderDetail", "CartItem"
]
