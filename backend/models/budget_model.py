from pydantic import BaseModel
from sqlmodel import SQLModel, Relationship, Field
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from models.category_model import Category
    from models.user_model import User


class Budget(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    category_id: UUID = Field(
        foreign_key="category.id", ondelete="CASCADE", unique=True
    )
    monthly_limit: float
    created_at: datetime = Field(default_factory=datetime.now)
    category: Optional["Category"] = Relationship(back_populates="budget")
    owner: Optional["User"] = Relationship(back_populates="budgets")


class BudgetCreate(SQLModel):
    monthly_limit: float
    category_id: str


class BudgetUpdate(BaseModel):
    monthly_limit: float
