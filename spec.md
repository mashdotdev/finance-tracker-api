# Smart Expense Tracker AI

## Overview

A personal finance API where users can track their budget, set their budget and get AI-powered insights.

## Success Criteria

Every criterion must pass for the implementation to be completed

### Authentication

- [] POST /users/signup creates user with Argon2-hashed password
- [] POST /token signin users by signing JSON WEB TOKEN for valid credentials
- [] Invalid credentials should return 401 error with generic message
- [] JWT should expire after certain time

### Task CRUD

#### Categories Endpoints

- [] POST /categories - create category like Food, Rent, etc..
- [] GET /categories - get all created categories
- [] DELETE /categories/{id} - delete category by id

#### Expenses Endpoints

- [] POST /expenses - create expenses with amount, category, date, note
- [] GET /expenses - get all available expenses
- [] GET /expenses/{id} - get specific expense by id
- [] PUT /expenses/{id} - update specific expense by id
- [] DELETE /expenses/{id} - delete specific expense by id

#### Budget Endpoints

- [] GET /budget - get all the budgets limits
- [] PUT /budget/{category_id} - set monthly limit for a category
- [] GET /summary - get summary by spending vs budget for the current month

#### Agent Endpoints

- [] POST /advisor/chat - chat with ai agent

### Tools for AI Agent

- [] get_spending_summary() - total spend summary by category
- [] get_top_expenses() - biggest purchase for the current month
- [] get_budget_status() - which categories are over budget
- [] use can ask question like "where I am spending? or can can I afford new samsung s26 ultra? and then the agent queries the real data and give the answer

### Models

- [] - User model
- [] - Category model
- [] - Expense model
- [] - Budget model
