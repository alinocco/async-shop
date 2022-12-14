from sanic import Sanic
from sqlalchemy.ext.asyncio import create_async_engine

app = Sanic("MyHelloWorld")

bind = create_async_engine("postgresql+asyncpg://asyncshop:asyncshop@localhost/asyncshop", echo=True)


# ./routes.py
from sanic.response import text

@app.get("/")
async def hello_world(request):
    return text("Hello, World!") 


# ./middlewares.py
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


_base_model_session_ctx = ContextVar("session")

@app.middleware("request")
async def inject_session(request):
    request.ctx.session = sessionmaker(bind, AsyncSession, expire_on_commit=False)()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)


@app.middleware("response")
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()

# ./routes.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sanic.response import json

from app.models import Car, Person


@app.post("/user")
async def create_user(request):
    session = request.ctx.session
    async with session.begin():
        car = Car(brand="Tesla")
        person = Person(name="foo", cars=[car])
        session.add_all([person])
    return json(person.to_dict())


@app.get("/user/<pk:int>")
async def get_user(request, pk):
    session = request.ctx.session
    async with session.begin():
        stmt = select(Person).where(Person.id == pk).options(selectinload(Person.cars))
        result = await session.execute(stmt)
        person = result.scalar()

    if not person:
        return json({})

    return json(person.to_dict())

