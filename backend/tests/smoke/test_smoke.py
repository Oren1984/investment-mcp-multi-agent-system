"""
Smoke tests — verify that the system can be imported and initialized
without errors. No network calls, no external APIs, no DB needed.
"""
from __future__ import annotations

import pytest


class TestImports:
    """All key modules must import without error."""

    def test_import_main_app(self):
        from app.main import create_app
        assert create_app is not None

    def test_import_config(self):
        from app.core.config import settings
        assert settings.app_name is not None

    def test_import_db_models(self):
        from app.db.models import AnalysisRun, AgentOutput, Report, Ticker, RunStatus
        assert AnalysisRun is not None
        assert RunStatus.PENDING is not None

    def test_import_mcp_base(self):
        from app.mcp.base_tool import MCPBaseTool, MCPToolResult
        assert MCPBaseTool is not None

    def test_import_mcp_gateway(self):
        from app.mcp.gateway import MCPGateway, get_gateway, create_gateway
        assert MCPGateway is not None

    def test_import_all_mcp_tools(self):
        from app.mcp.tools import (
            StockPriceTool,
            FinancialStatementsTool,
            TechnicalIndicatorsTool,
            SectorAnalysisTool,
            RiskMetricsTool,
            NewsSentimentTool,
            SaveReportTool,
        )
        for cls in [StockPriceTool, FinancialStatementsTool, TechnicalIndicatorsTool,
                    SectorAnalysisTool, RiskMetricsTool, NewsSentimentTool, SaveReportTool]:
            assert hasattr(cls, "name")
            assert hasattr(cls, "description")
            assert hasattr(cls, "input_schema")

    def test_import_services(self):
        from app.services import (
            MarketDataService, FinancialsService, RiskService,
            NewsService, LLMService, ReportService,
        )
        for cls in [MarketDataService, FinancialsService, RiskService, NewsService]:
            assert cls is not None

    def test_import_schemas(self):
        from app.schemas import (
            AnalysisRequest, AnalysisResponse, AnalysisStatusResponse,
            ReportResponse, HistoryResponse, HealthResponse,
        )
        for cls in [AnalysisRequest, AnalysisResponse, HistoryResponse]:
            assert cls is not None

    def test_import_agents(self):
        from app.agents import (
            build_research_agent,
            build_technical_analyst_agent,
            build_sector_analyst_agent,
            build_risk_analyst_agent,
            build_report_writer_agent,
        )
        for fn in [build_research_agent, build_technical_analyst_agent,
                   build_sector_analyst_agent, build_risk_analyst_agent,
                   build_report_writer_agent]:
            assert callable(fn)

    def test_import_crew(self):
        from app.crews import InvestmentCrew, AnalysisConfig
        assert InvestmentCrew is not None
        assert AnalysisConfig is not None


class TestMCPGatewayInitialization:
    """Gateway must initialize with all 6 tools registered."""

    def test_gateway_registers_all_tools(self, mock_gateway):
        tools = mock_gateway.list_tools()
        assert len(tools) == 6
        for name in tools:
            assert isinstance(name, str)
            assert len(name) > 0

    def test_gateway_tool_names(self, mock_gateway):
        tools = set(mock_gateway.list_tools())
        assert "get_stock_price" in tools
        assert "get_financial_statements" in tools
        assert "get_technical_indicators" in tools
        assert "get_sector_analysis" in tools
        assert "get_risk_metrics" in tools
        assert "get_news_sentiment" in tools


class TestConfigurationSmoke:
    def test_settings_have_reasonable_defaults(self):
        from app.core.config import Settings
        s = Settings(_env_file=None)
        assert s.max_concurrent_runs >= 1
        assert s.db_pool_size >= 1
        assert s.api_v1_prefix.startswith("/")

    def test_run_status_enum_values(self):
        from app.db.models.analysis_run import RunStatus
        assert set(RunStatus) == {RunStatus.PENDING, RunStatus.RUNNING, RunStatus.COMPLETED, RunStatus.FAILED}
