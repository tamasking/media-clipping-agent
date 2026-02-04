from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import Base, Metric

DATABASE_URL = "sqlite+aiosqlite:///./agentdash.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize default metrics if none exist
    async with async_session() as session:
        result = await session.execute(select(Metric))
        if not result.scalar_one_or_none():
            metric = Metric(total_requests=0, success_rate=0.0, avg_latency=0.0, active_agents=0)
            session.add(metric)
            await session.commit()

async def get_db():
    async with async_session() as session:
        yield session
