from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

if TYPE_CHECKING:
    from models.category_model import Category
    from models.expense_model import Expenses
    from models.budget_model import Budget


class Role(str, Enum):
    user = "user"
    admin = "admin"


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    name: Optional[str] = Field(default=None, min_length=4, max_length=10)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
    categories: list["Category"] = Relationship(
        back_populates="owner", cascade_delete=True
    )
    expenses: list["Expenses"] = Relationship(
        back_populates="owner", cascade_delete=True
    )
    budgets: list["Budget"] = Relationship(back_populates="owner", cascade_delete=True)


class UserCreate(SQLModel):
    name: Optional[str] = None
    email: str
    password: str
