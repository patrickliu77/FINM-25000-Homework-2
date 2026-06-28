"""Generate chart files and the final report PDF for GitHub submission.

Run with local Alpaca credentials for final results:

    python generate_submission_artifacts.py --symbol AAPL

If credentials are not configured yet, use ``--allow-mock`` to generate
clearly-labeled sample artifacts so the submission structure can be reviewed.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import wrap

from backtest_service import AlpacaBacktestService
from frontend.charts import create_drawdown_chart, create_equity_curve_chart, create_price_chart
from frontend.mock_backtest import MockBacktestService


def main() -> None:
    args = parse_args()
    report, error = load_report(args.symbol, args.years, args.allow_mock)

    charts_dir = Path("charts")
    reports_dir = Path("reports")
    charts_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(exist_ok=True)

    selected = report.strategies["Trend Following"]
    create_price_chart(report.prices, selected).write_html(
        charts_dir / f"{report.symbol.lower()}_trend_price_signals.html",
        include_plotlyjs="cdn",
    )
    create_equity_curve_chart(report).write_html(
        charts_dir / f"{report.symbol.lower()}_equity_curves.html",
        include_plotlyjs="cdn",
    )
    create_drawdown_chart(report).write_html(
        charts_dir / f"{report.symbol.lower()}_drawdowns.html",
        include_plotlyjs="cdn",
    )

    lines = build_report_lines(report, error)
    write_simple_pdf(reports_dir / "final_report.pdf", lines)
    print(f"Wrote charts to {charts_dir.resolve()}")
    print(f"Wrote PDF report to {(reports_dir / 'final_report.pdf').resolve()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate HW2 charts and final report.")
    parser.add_argument("--symbol", default="AAPL", help="Ticker to backtest.")
    parser.add_argument("--years", type=int, default=5, help="Years of daily data.")
    parser.add_argument(
        "--allow-mock",
        action="store_true",
        help="Use synthetic data if Alpaca credentials/API access are unavailable.",
    )
    return parser.parse_args()


def load_report(symbol: str, years: int, allow_mock: bool):
    try:
        return AlpacaBacktestService().run_backtest(symbol, years), None
    except Exception as error:
        if not allow_mock:
            raise
        return MockBacktestService().run_backtest(symbol.upper(), years), str(error)


def build_report_lines(report, backend_error: str | None) -> list[str]:
    source = "Synthetic mock data" if report.using_mock else "Alpaca historical market data"
    lines = [
        "FINM 25000 Homework 2: Technical Indicators & Strategy Backtesting",
        "",
        f"Ticker: {report.symbol}",
        f"Period: {report.years} years of daily OHLCV bars",
        f"Data source: {source}",
        "Initial capital: $100,000",
        "Constraints: long-only, no leverage, no short selling",
        "",
    ]
    if backend_error:
        lines.extend(
            [
                "Artifact note:",
                "These artifacts were generated in mock mode because Alpaca credentials",
                "were not available in this local repo at generation time.",
                f"Backend detail: {backend_error}",
                "",
            ]
        )

    lines.extend(
        [
            "Strategy Descriptions",
            "",
            "Buy & Hold: fully invested benchmark used as the baseline comparison.",
            "",
            "Trend Following: buys when MACD is above its signal line, ADX is above",
            "25, and price is above the 50-day SMA. It exits when MACD crosses below",
            "its signal or price loses the 50-day SMA.",
            "",
            "Mean Reversion: buys oversold conditions where RSI is below 30 and price",
            "is below the lower Bollinger Band. It exits when RSI is above 70 or price",
            "moves above the upper Bollinger Band.",
            "",
            "Custom Strategy: combines trend, momentum, volatility, and volume. It",
            "requires EMA20 > SMA50, MACD > signal, RSI between 45 and 70, price above",
            "the Bollinger midline, positive CMF, and a normal ATR regime. It exits on",
            "trend, momentum, or volume deterioration.",
            "",
            "Performance Comparison",
            "",
            "Strategy                 Total Return   CAGR   Volatility   Sharpe   Sortino   Max DD   Win Rate",
        ]
    )

    for result in [report.buy_hold, *report.strategies.values()]:
        metrics = result.metrics
        lines.append(
            f"{result.name:<24} "
            f"{pct(metrics['total_return']):>11} "
            f"{pct(metrics['cagr']):>7} "
            f"{pct(metrics['volatility']):>11} "
            f"{metrics['sharpe']:>8.2f} "
            f"{metrics['sortino']:>9.2f} "
            f"{pct(metrics['max_drawdown']):>8} "
            f"{pct(metrics['win_rate']):>9}"
        )

    best = max([report.buy_hold, *report.strategies.values()], key=lambda result: result.metrics["sharpe"])
    lines.extend(
        [
            "",
            "Discussion",
            "",
            f"The highest Sharpe ratio in this run belongs to {best.name}. The key",
            "comparison is risk-adjusted performance, not just raw return, so the",
            "equity curve and drawdown chart should be reviewed together with the",
            "Sharpe, Sortino, and maximum drawdown metrics.",
            "",
            "Charts",
            "",
            "The repository includes HTML chart exports in the charts/ folder:",
            "- price chart with indicators and buy/sell signals",
            "- equity curve comparison",
            "- drawdown comparison",
        ]
    )
    return lines


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_simple_pdf(path: Path, lines: list[str]) -> None:
    """Write a basic multi-page PDF using only the Python standard library."""
    pages = []
    current: list[str] = []
    for line in expand_lines(lines):
        if len(current) >= 48:
            pages.append(current)
            current = []
        current.append(line)
    if current:
        pages.append(current)

    objects: list[bytes] = []

    def add_object(payload: bytes) -> int:
        objects.append(payload)
        return len(objects)

    catalog_id = add_object(b"")
    pages_id = add_object(b"")
    font_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    page_ids = []
    for page_lines in pages:
        content = pdf_content_stream(page_lines)
        content_id = add_object(
            b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"\nendstream"
        )
        page_id = add_object(
            (
                f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>"
            ).encode("ascii")
        )
        page_ids.append(page_id)

    objects[catalog_id - 1] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii")
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_id, payload in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode("ascii"))
        output.extend(payload)
        output.extend(b"\nendobj\n")
    xref_start = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("ascii")
    )
    path.write_bytes(output)


def expand_lines(lines: list[str]) -> list[str]:
    expanded: list[str] = []
    for line in lines:
        if not line:
            expanded.append("")
            continue
        expanded.extend(wrap(line, width=88, replace_whitespace=False) or [""])
    return expanded


def pdf_content_stream(lines: list[str]) -> bytes:
    commands = ["BT", "/F1 10 Tf", "50 750 Td", "14 TL"]
    for line in lines:
        commands.append(f"({escape_pdf_text(line)}) Tj")
        commands.append("T*")
    commands.append("ET")
    return "\n".join(commands).encode("ascii")


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


if __name__ == "__main__":
    main()
