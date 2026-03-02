from dataclasses import dataclass
from agents import function_tool, RunContextWrapper
from sqlmodel import select, func
from models import User, Expenses, Category, Budget
from app import AsyncSession
from datetime import datetime
from sqlmodel import col as _col


@dataclass
class AgentContext:
    user: User
    session: AsyncSession


@function_tool
async def get_spending_summary(
    ctx: RunContextWrapper[AgentContext], category_name: str
):
    """
    Get total spending summary by category

    Args:
        category_name: The name of the category to get spending summary for
    """
    session = ctx.context.session
    user = ctx.context.user

    category = (
        await session.exec(
            select(Category).where(
                func.lower(Category.name) == category_name.lower(),
                Category.user_id == user.id,
            )
        )
    ).first()

    if not category:
        return f"No category found with the name '{category_name}'."

    total = (
        await session.exec(
            select(func.sum(Expenses.amount)).where(
                Expenses.category_id == category.id,
                Expenses.user_id == user.id,
            )
        )
    ).one()

    spent = total or 0.0
    return f"Total spending in '{category.name}': ${spent:.2f}"


@function_tool
async def get_budget_status(ctx: RunContextWrapper[AgentContext]):
    """
    Check which categories are over budget, approaching the limit, or within budget.
    Use this when the user asks about their budget status, overspending, or budget health.
    """
    session = ctx.context.session
    user = ctx.context.user

    budgets = (
        await session.exec(select(Budget).where(Budget.user_id == user.id))
    ).all()

    if not budgets:
        return "You have no budgets set. Create a budget for a category first."

    over, approaching, ok = [], [], []

    for budget in budgets:
        category = await session.get(Category, budget.category_id)
        category_name = category.name if category else str(budget.category_id)

        total = (
            await session.exec(
                select(func.sum(Expenses.amount)).where(
                    Expenses.category_id == budget.category_id,
                    Expenses.user_id == user.id,
                )
            )
        ).one()

        spent = total or 0.0
        limit = budget.monthly_limit
        remaining = limit - spent
        pct = (spent / limit * 100) if limit > 0 else 0

        entry = f"- {category_name}: spent ${spent:.2f} of ${limit:.2f} ({pct:.0f}%)"

        if spent > limit:
            over.append(f"{entry} — OVER by ${abs(remaining):.2f}")
        elif pct >= 80:
            approaching.append(f"{entry} — only ${remaining:.2f} left")
        else:
            ok.append(f"{entry} — ${remaining:.2f} remaining")

    lines = []
    if over:
        lines.append("Over budget:\n" + "\n".join(over))
    if approaching:
        lines.append("Approaching limit (80%+):\n" + "\n".join(approaching))
    if ok:
        lines.append("Within budget:\n" + "\n".join(ok))

    return "\n\n".join(lines)


@function_tool
async def get_top_expenses(ctx: RunContextWrapper[AgentContext], limit: int = 5):
    """
    Get the biggest expenses for the current month, sorted by amount descending.
    Use this when the user asks about their largest purchases, biggest spending, or top expenses this month.

    Args:
        limit: Number of top expenses to return. Defaults to 5.
    """

    session = ctx.context.session
    user = ctx.context.user
    now = datetime.now()

    expenses = (
        await session.exec(
            select(Expenses)
            .where(
                Expenses.user_id == user.id,
                func.extract("month", _col(Expenses.date)) == now.month,
                func.extract("year", _col(Expenses.date)) == now.year,
            )
            .order_by(_col(Expenses.amount).desc())
            .limit(limit)
        )
    ).all()

    if not expenses:
        return "You have no expenses recorded for this month."

    lines = [f"Your top {len(expenses)} expense(s) this month:"]
    for i, expense in enumerate(expenses, start=1):
        category = await session.get(Category, expense.category_id)
        category_name = category.name if category else "Uncategorized"
        note = f" — {expense.note}" if expense.note else ""
        lines.append(f"{i}. ${expense.amount:.2f} in {category_name}{note}")

    return "\n".join(lines)


@function_tool
async def can_afford_suggestion(
    ctx: RunContextWrapper[AgentContext], item_name: str, item_price: float
):
    """
    Analyze whether the user can afford a specific purchase based on their real financial data.
    Use this when the user asks things like:
    - "Can I afford a Samsung S26 Ultra?"
    - "Should I buy a $500 item?"
    - "Where am I spending the most?"
    - "Do I have money left this month?"

    Args:
        item_name: The name of the item the user wants to buy (e.g. "Samsung S26 Ultra")
        item_price: The price of the item in dollars (e.g. 1200.0)
    """
    session = ctx.context.session
    user = ctx.context.user
    now = datetime.now()

    # Get all budgets and calculate remaining for each category
    budgets = (
        await session.exec(select(Budget).where(Budget.user_id == user.id))
    ).all()

    total_budget = 0.0
    total_spent_this_month = 0.0
    category_breakdown = []

    for budget in budgets:
        category = await session.get(Category, budget.category_id)
        category_name = category.name if category else "Unknown"

        spent = (
            await session.exec(
                select(func.sum(Expenses.amount)).where(
                    Expenses.category_id == budget.category_id,
                    Expenses.user_id == user.id,
                    func.extract("month", _col(Expenses.date)) == now.month,
                    func.extract("year", _col(Expenses.date)) == now.year,
                )
            )
        ).one() or 0.0

        remaining = budget.monthly_limit - spent
        total_budget += budget.monthly_limit
        total_spent_this_month += spent
        category_breakdown.append(
            f"  - {category_name}: ${remaining:.2f} remaining of ${budget.monthly_limit:.2f}"
        )

    total_remaining = total_budget - total_spent_this_month

    # Build the response
    lines = [
        f"Here's your financial snapshot for {now.strftime('%B %Y')}:",
        f"  Total budget:  ${total_budget:.2f}",
        f"  Spent so far:  ${total_spent_this_month:.2f}",
        f"  Remaining:     ${total_remaining:.2f}",
    ]

    if category_breakdown:
        lines.append("\nBy category:")
        lines.extend(category_breakdown)

    lines.append(f"\nItem: {item_name} — ${item_price:.2f}")

    if total_remaining <= 0:
        lines.append(
            "\nVerdict: You've already used up your entire budget this month. "
            "It's not a good time to make this purchase."
        )
    elif item_price > total_remaining:
        shortage = item_price - total_remaining
        lines.append(
            f"\nVerdict: You can't comfortably afford {item_name} right now. "
            f"You're ${shortage:.2f} short based on your remaining budget."
        )
    elif item_price > total_remaining * 0.5:
        lines.append(
            f"\nVerdict: You could technically afford {item_name}, but it would use "
            f"{(item_price / total_remaining * 100):.0f}% of your remaining budget. "
            "Consider whether it's worth it this month."
        )
    else:
        lines.append(
            f"\nVerdict: Yes, you can afford {item_name}! "
            f"You'll still have ${total_remaining - item_price:.2f} left in your budget after this purchase."
        )

    return "\n".join(lines)


# Can I afford a Samsung S26 Ultra for $1200?
