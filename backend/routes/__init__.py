from routes.category import router as category_router
from routes.user import router as authentication_router
from routes.expense import router as expense_router
from routes.budget import router as budget_router
from routes.admin import router as admin_router

__all__ = [
    "category_router",
    "authentication_router",
    "expense_router",
    "budget_router",
    "admin_router",
]
