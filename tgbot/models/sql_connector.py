from sqlalchemy import MetaData, inspect, Column, String, insert, select, Integer, Text, Boolean, Time, \
    DateTime, update, TIMESTAMP
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker, as_declarative
from sqlalchemy.sql import expression

from create_bot import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@as_declarative()
class Base:
    metadata = MetaData()

    def _asdict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class UtcNow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(UtcNow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class UsersDB(Base):
    """Пользователи"""
    __tablename__ = "users"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String, nullable=True)
    mailing = Column(Boolean, nullable=False, server_default="false")
    category = Column(String, nullable=True)  # требует уточнения


class TicketsDB(Base):
    """Обращения"""
    __tablename__ = "tickets"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    dtime = Column(TIMESTAMP, nullable=False, server_default=UtcNow())
    is_finished = Column(Boolean, nullable=False, server_default="false")


class TextsDB(Base):
    """Тексты сообщений бота"""
    __tablename__ = "texts"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    parent = Column(Integer, nullable=True)
    button = Column(String, nullable=True)
    text = Column(Text, nullable=True)


class WorktimeDB(Base):
    """Рабочее время компании"""
    __tablename__ = "worktime"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    day = Column(String, nullable=False)
    start = Column(Time, nullable=True)
    finish = Column(Time, nullable=True)


class BaseDAO:
    """Класс взаимодействия с БД"""
    model = None

    @classmethod
    async def get_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def get_many(cls, **filter_by) -> list:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def create(cls, **data):
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(**data)
            result = await session.execute(stmt)
            await session.commit()
            return result.mappings().one_or_none()


class UsersDAO(BaseDAO):
    model = UsersDB


class TextsDAO(BaseDAO):
    model = TextsDB

    @classmethod
    async def get_order_by_parents(cls) -> list:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).order_by(TextsDB.parent.asc())
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def update(cls, button_id: int, **data):
        async with async_session_maker() as session:
            stmt = update(cls.model).values(**data).filter_by(id=button_id)
            await session.execute(stmt)
            await session.commit()
