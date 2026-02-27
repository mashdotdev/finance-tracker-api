from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.user_model import User
    from models.expense_model import Expenses
    from models.budget_model import Budget


class Category(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    user_id: Optional[UUID] = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    name: str = Field(min_length=3, max_length=10)
    expenses: list["Expenses"] = Relationship(back_populates="category")
    created_at: datetime = Field(default_factory=datetime.now)
    owner: Optional["User"] = Relationship(back_populates="categories")
    budget: Optional["Budget"] = Relationship(back_populates="category")


class CategoryCreate(SQLModel):
    name: str
