#!/usr/bin/env python3
"""CLI entry point for the Binance Futures Testnet trading bot."""

from __future__ import annotations

import argparse
import os
import sys
import textwrap

try:
    from dotenv import load_dotenv
    load_dotenv()  # loads .env from project root automatically
except ImportError:
    pass  # python-dotenv not installed; fall back to plain env vars

from bot.client import BinanceAPIError, BinanceClient
from bot.logging_config import setup_logging
from bot.orders import (
    OrderResult,
    place_limit_order,
    place_market_order,
    place_stop_limit_order,
)
from bot.validators import (
    ValidationError,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = setup_logging()

# ──────────────────────────────────────────────────────────────
# Pretty printer
# ──────────────────────────────────────────────────────────────

SEPARATOR = "─" * 50


def _print_section(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def print_request_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None,
    stop_price: float | None,
) -> None:
    _print_section("ORDER REQUEST SUMMARY")
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Type       : {order_type}")
    print(f"  Quantity   : {quantity}")
    if price is not None:
        print(f"  Price      : {price}")
    if stop_price is not None:
        print(f"  Stop Price : {stop_price}")


def print_order_result(result: OrderResult) -> None:
    _print_section("ORDER RESPONSE")
    print(f"  Order ID      : {result.order_id}")
    print(f"  Symbol        : {result.symbol}")
    print(f"  Side          : {result.side}")
    print(f"  Type          : {result.order_type}")
    print(f"  Status        : {result.status}")
    print(f"  Orig Qty      : {result.orig_qty}")
    print(f"  Executed Qty  : {result.executed_qty}")
    print(f"  Avg Price     : {result.avg_price}")
    if result.price and result.price != "0":
        print(f"  Limit Price   : {result.price}")


def print_success() -> None:
    print(f"\n{'─' * 50}")
    print("  ✅  Order placed successfully!")
    print(f"{'─' * 50}\n")


def print_failure(reason: str) -> None:
    print(f"\n{'─' * 50}")
    print(f"  ❌  Order failed: {reason}")
    print(f"{'─' * 50}\n")


# ──────────────────────────────────────────────────────────────
# Argument parser
# ──────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            Binance Futures Testnet Trading Bot
            ────────────────────────────────────
            Place MARKET, LIMIT, or STOP_LIMIT orders on the testnet.

            API credentials are read from environment variables:
              BINANCE_API_KEY    — your testnet API key
              BINANCE_API_SECRET — your testnet API secret
            """
        ),
        epilog=textwrap.dedent(
            """\
            Examples:
              # Market BUY
              python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

              # Limit SELL
              python -m bot.cli --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 70000

              # Stop-Limit BUY (bonus)
              python -m bot.cli --symbol BTCUSDT --side BUY --type STOP_LIMIT \\
                --quantity 0.01 --price 68000 --stop-price 67500
            """
        ),
    )

    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL"], help="BUY or SELL"
    )
    parser.add_argument(
        "--type",
        required=True,
        dest="order_type",
        choices=["MARKET", "LIMIT", "STOP_LIMIT"],
        help="Order type",
    )
    parser.add_argument(
        "--quantity", required=True, type=float, help="Order quantity (base asset)"
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="Limit price (required for LIMIT and STOP_LIMIT)",
    )
    parser.add_argument(
        "--stop-price",
        type=float,
        default=None,
        dest="stop_price",
        help="Trigger price (required for STOP_LIMIT)",
    )
    parser.add_argument(
        "--tif",
        default="GTC",
        choices=["GTC", "IOC", "FOK"],
        help="Time-in-force for LIMIT orders (default: GTC)",
    )
    return parser


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # ── Validate inputs ───────────────────────────────────────
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)
        price = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)
    except ValidationError as exc:
        print_failure(str(exc))
        logger.warning("Validation error: %s", exc)
        return 1

    # ── Load credentials ──────────────────────────────────────
    api_key = os.environ.get("BINANCE_API_KEY", "").strip()
    api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        msg = (
            "BINANCE_API_KEY and BINANCE_API_SECRET environment variables must be set.\n"
            "  export BINANCE_API_KEY=your_key\n"
            "  export BINANCE_API_SECRET=your_secret"
        )
        print_failure(msg)
        logger.error("Missing API credentials in environment.")
        return 1

    # ── Print summary ─────────────────────────────────────────
    print_request_summary(symbol, side, order_type, quantity, price, stop_price)

    # ── Place order ───────────────────────────────────────────
    client = BinanceClient(api_key, api_secret)

    try:
        if order_type == "MARKET":
            result = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            result = place_limit_order(client, symbol, side, quantity, price, args.tif)
        else:  # STOP_LIMIT
            result = place_stop_limit_order(
                client, symbol, side, quantity, price, stop_price, args.tif
            )
    except ValidationError as exc:
        print_failure(str(exc))
        logger.warning("Validation error: %s", exc)
        return 1
    except BinanceAPIError as exc:
        print_failure(str(exc))
        return 1
    except Exception as exc:  # network / unexpected
        print_failure(f"Unexpected error: {exc}")
        logger.exception("Unexpected error placing order")
        return 1

    print_order_result(result)
    print_success()
    return 0


if __name__ == "__main__":
    sys.exit(main())
