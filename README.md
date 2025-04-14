#  Real Estate Platform API

This is an API for managing users in a real estate system. The project is built using **FastAPI**, **SQLAlchemy**, **Unit of Work**, **JWT authentication**, and **role-based access control** (admin, customer).

##  Technologies

- FastAPI
- SQLAlchemy + async (asyncpg/aiosqlite)
- Pydantic v2
- JWT (access + refresh tokens)
- Dependency Injection (DI)
- Unit of Work (UoW)
- Middleware (admin panel protection)
- Starlette Admin
- Pytest

##  Project Structure

```
users/
├── auth.py            # Authentication and token generation
├── models.py          # SQLAlchemy models: User, Group, UserGroup
├── repositories.py    # CRUD Repositories
├── schema.py          # Pydantic schemas
├── services.py        # Business logic
├── unit_of_work.py    # Unit of Work implementation
├── utils.py           # Helper functions like is_admin()
├── routes.py          # API routes
```

##  Running Tests

```bash
pytest
```

Test coverage includes:
- Creating, reading, deleting users
- Login and token refreshing
- Authorized and unauthorized requests
- Full Unit of Work logic

##  Admin Middleware

Access to `/admin` is protected by `AdminAuthMiddleware`. Only users in the `admin` group are allowed. If the token is invalid, users are redirected to `/api/login`.

##  How to Run

```bash
uvicorn main:app --reload
```

Or run via **PyCharm** with **debug mode** enabled — `debugpy` and breakpoints will work.

##  Authentication

- Get token: `POST /api/login`
- Protected endpoints: `Authorization: Bearer <token>`
- Get new access token with refresh: `POST /api/refresh`

##  Features

- Full Unit of Work implementation with DI (`Depends(get_user_uow)`)
- User creation checks for existing emails
- All database transactions go through `async with SqlAlchemyUnitOfWork(...)`

## 📄 License

