"""Unit tests for InvestmentCrew execution mode routing and report builders."""
from __future__ import annotations

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.crews.investment_crew import AnalysisConfig, InvestmentCrew, _build_demo_report


class TestAnalysisConfig:
    def test_default_execution_mode_is_hybrid(self):
        cfg = AnalysisConfig(ticker="AAPL", run_id=str(uuid4()))
        assert cfg.execution_mode == "hybrid"

    def test_default_period_is_1y(self):
        cfg = AnalysisConfig(ticker="AAPL", run_id=str(uuid4()))
        assert cfg.period == "1y"

    def test_custom_execution_mode(self):
        cfg = AnalysisConfig(ticker="MSFT", run_id=str(uuid4()), execution_mode="rag_only")
        assert cfg.execution_mode == "rag_only"


class TestBuildDemoReport:
    def test_contains_ticker(self):
        report = _build_demo_report("AAPL", "1y")
        assert "AAPL" in report

    def test_contains_demo_warning(self):
        report = _build_demo_report("AAPL", "1y")
        assert "DEMO MODE" in report

    def test_contains_period(self):
        report = _build_demo_report("AAPL", "6mo")
        assert "6mo" in report

    def test_rag_only_mode_label(self):
        report = _build_demo_report("AAPL", "1y", execution_mode="rag_only")
        assert "RAG Only" in report

    def test_agent_only_mode_label(self):
        report = _build_demo_report("AAPL", "1y", execution_mode="agent_only")
        assert "Agent Only" in report

    def test_hybrid_mode_label(self):
        report = _build_demo_report("AAPL", "1y", execution_mode="hybrid")
        assert "Hybrid" in report

    def test_report_is_markdown(self):
        report = _build_demo_report("AAPL", "1y")
        assert report.startswith("#")

    def test_contains_disclaimer(self):
        report = _build_demo_report("AAPL", "1y")
        assert "not financial advice" in report.lower()


class TestInvestmentCrewModeRouting:
    """Test that InvestmentCrew routes to correct execution path based on config."""

    def _make_crew(self, mock_gateway=None):
        gw = mock_gateway or MagicMock()
        return InvestmentCrew(gateway=gw)

    def _make_config(self, mode: str = "hybrid") -> AnalysisConfig:
        return AnalysisConfig(ticker="AAPL", run_id=str(uuid4()), execution_mode=mode)

    @patch("app.crews.investment_crew.is_demo_mode", return_value=True)
    @patch("app.crews.investment_crew.get_sync_session")
    def test_demo_mode_calls_run_demo(self, mock_session, mock_is_demo):
        mock_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_session.return_value.__exit__ = MagicMock(return_value=False)

        crew = self._make_crew()
        config = self._make_config("hybrid")

        with patch.object(crew, "_run_demo", return_value="demo report") as mock_demo:
            result = crew.run(config)

        mock_demo.assert_called_once()
        assert result == "demo report"

    @patch("app.crews.investment_crew.is_demo_mode", return_value=True)
    @patch("app.crews.investment_crew.get_sync_session")
    def test_demo_mode_with_rag_only_calls_run_demo(self, mock_session, mock_is_demo):
        """In demo mode, even rag_only is intercepted → synthetic report."""
        mock_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_session.return_value.__exit__ = MagicMock(return_value=False)

        crew = self._make_crew()
        config = self._make_config("rag_only")

        with patch.object(crew, "_run_demo", return_value="demo report") as mock_demo:
            result = crew.run(config)

        mock_demo.assert_called_once()

    @patch("app.crews.investment_crew.is_demo_mode", return_value=False)
    @patch("app.crews.investment_crew.get_sync_session")
    def test_live_mode_rag_only_calls_run_rag_only(self, mock_session, mock_is_demo):
        mock_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_session.return_value.__exit__ = MagicMock(return_value=False)

        crew = self._make_crew()
        config = self._make_config("rag_only")

        with patch.object(crew, "_run_rag_only", return_value="rag report") as mock_rag:
            result = crew.run(config)

        mock_rag.assert_called_once()
        assert result == "rag report"

    @patch("app.crews.investment_crew.is_demo_mode", return_value=False)
    @patch("app.crews.investment_crew.get_sync_session")
    def test_live_mode_hybrid_calls_run_hybrid(self, mock_session, mock_is_demo):
        mock_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_session.return_value.__exit__ = MagicMock(return_value=False)

        crew = self._make_crew()
        config = self._make_config("hybrid")

        with patch.object(crew, "_run_hybrid", return_value="hybrid report") as mock_hybrid:
            result = crew.run(config)

        mock_hybrid.assert_called_once()
        assert result == "hybrid report"

    @patch("app.crews.investment_crew.is_demo_mode", return_value=False)
    @patch("app.crews.investment_crew.get_sync_session")
    def test_live_mode_agent_only_calls_run_live(self, mock_session, mock_is_demo):
        mock_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_session.return_value.__exit__ = MagicMock(return_value=False)

        crew = self._make_crew()
        config = self._make_config("agent_only")

        with patch.object(crew, "_run_live", return_value="live report") as mock_live:
            result = crew.run(config)

        mock_live.assert_called_once()
        assert result == "live report"

    @patch("app.crews.investment_crew.is_demo_mode", return_value=False)
    @patch("app.crews.investment_crew.get_sync_session")
    def test_exception_marks_run_failed(self, mock_session, mock_is_demo):
        mock_sess = MagicMock()
        mock_session.return_value = mock_sess

        mock_run_repo = MagicMock()
        mock_run_repo.update_status = MagicMock()

        with patch("app.crews.investment_crew.AnalysisRunSyncRepository", return_value=mock_run_repo):
            crew = self._make_crew()
            config = self._make_config("hybrid")

            with patch.object(crew, "_run_hybrid", side_effect=RuntimeError("unexpected error")):
                with pytest.raises(RuntimeError):
                    crew.run(config)

        from app.db.models.analysis_run import RunStatus
        calls = [str(c) for c in mock_run_repo.update_status.call_args_list]
        assert any("FAILED" in c for c in calls)
