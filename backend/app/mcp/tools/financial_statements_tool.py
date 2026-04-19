from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.mcp.base_tool import MCPBaseTool
from app.services.financials_service import FinancialsService
from app.services.market_data_service import MarketDataService


class FinancialStatementsInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    statement_type: Literal["all", "income", "balance", "cashflow"] = Field(
        "all", description="Which financial statement(s) to retrieve"
    )


class FinancialStatementsTool(MCPBaseTool):
    name = "get_financial_statements"
    description = "Retrieve financial statements (income, balance sheet, cash flow) and key metrics."
    input_schema = FinancialStatementsInput

    def __init__(self, financials: FinancialsService, market_data: MarketDataService):
        self._financials = financials
        self._market_data = market_data

    def run(self, inputs: FinancialStatementsInput) -> dict[str, Any]:
        result: dict[str, Any] = {"ticker": inputs.ticker}
        result["key_metrics"] = self._financials.get_key_metrics(inputs.ticker)

        if inputs.statement_type in ("all", "income"):
            result["income_statement"] = self._financials.get_income_statement(inputs.ticker)
        if inputs.statement_type in ("all", "balance"):
            result["balance_sheet"] = self._financials.get_balance_sheet(inputs.ticker)
        if inputs.statement_type in ("all", "cashflow"):
            result["cash_flow"] = self._financials.get_cash_flow(inputs.ticker)

        return result
