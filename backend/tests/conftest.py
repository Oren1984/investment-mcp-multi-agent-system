"""
Shared fixtures for all test layers.
Tests that need a DB use an in-memory SQLite engine.
Tests that need external services mock them out entirely.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.analysis_run import AnalysisRun, RunStatus
from app.db.models.agent_output import AgentOutput
from app.db.models.report import Report
from app.db.models.ticker import Ticker

# ── In-memory SQLite for tests ─────────────────────────────────────────────────

TEST_SYNC_URL = "sqlite:///:memory:"
TEST_ASYNC_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def sync_test_engine():
    engine = create_engine(
        TEST_SYNC_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def sync_db_session(sync_test_engine) -> Session:
    connection = sync_test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest_asyncio.fixture(scope="session")
async def async_test_engine():
    engine = create_async_engine(
        TEST_ASYNC_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_db_session(async_test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session_factory = async_sessionmaker(async_test_engine, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session


# ── Mock services ──────────────────────────────────────────────────────────────

@pytest.fixture
def mock_market_data():
    svc = MagicMock()
    svc.get_price_history.return_value = {
        "ticker": "AAPL",
        "period": "1y",
        "interval": "1d",
        "current_price": 175.0,
        "price_change_pct": 12.5,
        "data": {},
    }
    svc.get_company_info.return_value = {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "exchange": "NASDAQ",
        "market_cap": 2_700_000_000_000,
        "pe_ratio": 28.5,
        "forward_pe": 26.0,
        "pb_ratio": 45.0,
        "dividend_yield": 0.005,
        "52w_high": 199.0,
        "52w_low": 143.0,
        "description": "Apple designs and sells electronics.",
    }
    svc.get_sector_comparison.return_value = {
        "ticker": "AAPL",
        "sector": "Technology",
        "sector_etf": "XLK",
        "stock_1y_return_pct": 15.0,
        "sector_1y_return_pct": 10.0,
        "relative_performance_pct": 5.0,
    }
    return svc


@pytest.fixture
def mock_financials():
    svc = MagicMock()
    svc.get_key_metrics.return_value = {
        "ticker": "AAPL",
        "eps": 6.13,
        "eps_growth_yoy": 0.08,
        "revenue_growth_yoy": 0.05,
        "gross_margins": 0.44,
        "operating_margins": 0.30,
        "profit_margins": 0.25,
        "return_on_equity": 1.60,
        "return_on_assets": 0.27,
        "debt_to_equity": 1.73,
        "current_ratio": 0.99,
        "quick_ratio": 0.91,
        "free_cashflow": 90_000_000_000,
        "total_revenue": 383_000_000_000,
        "total_debt": 100_000_000_000,
        "book_value": 3.95,
    }
    svc.get_income_statement.return_value = {"ticker": "AAPL", "statement": "income", "data": {}}
    svc.get_balance_sheet.return_value = {"ticker": "AAPL", "statement": "balance_sheet", "data": {}}
    svc.get_cash_flow.return_value = {"ticker": "AAPL", "statement": "cash_flow", "data": {}}
    return svc


@pytest.fixture
def mock_risk():
    svc = MagicMock()
    svc.get_risk_metrics.return_value = {
        "ticker": "AAPL",
        "period": "1y",
        "beta": 1.25,
        "annualized_volatility_pct": 24.5,
        "annualized_return_pct": 15.0,
        "max_drawdown_pct": -18.3,
        "sharpe_ratio": 0.85,
        "var_95_1day_pct": -2.1,
        "benchmark": "SPY",
    }
    svc.get_technical_indicators.return_value = {
        "ticker": "AAPL",
        "current_price": 175.0,
        "sma_20": 172.0,
        "sma_50": 168.0,
        "sma_200": 160.0,
        "ema_12": 174.0,
        "ema_26": 170.0,
        "macd": 4.0,
        "macd_signal": 3.5,
        "macd_histogram": 0.5,
        "rsi_14": 58.0,
        "bollinger_upper": 185.0,
        "bollinger_lower": 159.0,
        "volume_vs_avg_pct": 10.0,
        "trend": "BULLISH",
        "rsi_signal": "NEUTRAL",
    }
    return svc


@pytest.fixture
def mock_news():
    svc = MagicMock()
    svc.get_news_sentiment.return_value = {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "days_covered": 7,
        "article_count": 5,
        "headlines": ["Apple beats earnings expectations", "iPhone 16 demand strong"],
        "sentiment_score": 0.4,
        "sentiment_label": "POSITIVE",
    }
    return svc


@pytest.fixture
def mock_gateway(mock_market_data, mock_financials, mock_risk, mock_news):
    from app.mcp.gateway import MCPGateway
    from app.services.llm_service import LLMService
    gateway = MCPGateway(
        market_data=mock_market_data,
        financials=mock_financials,
        risk=mock_risk,
        news=mock_news,
        llm=MagicMock(spec=LLMService),
    )
    return gateway


# ── FastAPI test client ────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def test_client(async_db_session, mock_gateway) -> AsyncGenerator[AsyncClient, None]:
    from app.main import create_app
    from app.db.session import get_async_session
    from app.mcp.gateway import get_gateway

    test_app = create_app()

    async def override_db():
        yield async_db_session

    def override_gateway():
        return mock_gateway

    test_app.dependency_overrides[get_async_session] = override_db
    test_app.dependency_overrides[get_gateway] = override_gateway

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        yield client

    test_app.dependency_overrides.clear()


# ── Helper factories ───────────────────────────────────────────────────────────

def make_run(
    ticker: str = "AAPL",
    status: RunStatus = RunStatus.PENDING,
    run_id: str | None = None,
) -> AnalysisRun:
    return AnalysisRun(
        id=run_id or str(uuid4()),
        ticker=ticker,
        status=status,
        config={"period": "1y"},
        created_at=datetime.now(timezone.utc),
    )


def make_report(run_id: str, ticker: str = "AAPL") -> Report:
    return Report(
        id=str(uuid4()),
        run_id=run_id,
        ticker_symbol=ticker,
        content="# Investment Report\n## Executive Summary\nTest report.",
        structured={"executive_summary": "Test summary", "recommendation": "BUY"},
        created_at=datetime.now(timezone.utc),
    )
