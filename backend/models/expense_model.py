from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from models.category_model import Category
    from models.user_model import User


class Expenses(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    user_id: UUID = Field(default=None, foreign_key="user.id", ondelete="CASCADE")
    category_id: Optional[UUID] = Field(
        default=None, foreign_key="category.id", ondelete="SET NULL"
    )
    amount: float
    date: datetime = Field(default_factory=datetime.now)
    category: Optional["Category"] = Relationship(back_populates="expenses")
    note: Optional[str] = Field(default=None, max_length=250)
    owner: Optional["User"] = Relationship(back_populates="expenses")


class ExpenseCreate(SQLModel):
    category_id: UUID
    amount: float
    note: Optional[str] = None
