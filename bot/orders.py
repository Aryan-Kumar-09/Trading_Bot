"""Order placement logic — sits between the client and the CLI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from bot.client import BinanceClient
from bot.logging_config import setup_logging

logger = setup_logging()


@dataclass
class OrderResult:
    order_id: int
    symbol: str
    side: str
    order_type: str
    status: str
    orig_qty: str
    executed_qty: str
    avg_price: str
    price: str
    raw: dict


def _parse_result(data: dict) -> OrderResult:
    return OrderResult(
        order_id=data.get("orderId", 0),
        symbol=data.get("symbol", ""),
        side=data.get("side", ""),
        order_type=data.get("type", ""),
        status=data.get("status", ""),
        orig_qty=data.get("origQty", "0"),
        executed_qty=data.get("executedQty", "0"),
        avg_price=data.get("avgPrice", "0"),
        price=data.get("price", "0"),
        raw=data,
    )


def place_market_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
) -> OrderResult:
    """Place a MARKET order."""
    logger.info(
        "Placing MARKET %s %s qty=%s", side, symbol, quantity
    )
    data = client.place_order(
        symbol=symbol,
        side=side,
        type="MARKET",
        quantity=quantity,
    )
    return _parse_result(data)


def place_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> OrderResult:
    """Place a LIMIT order."""
    logger.info(
        "Placing LIMIT %s %s qty=%s price=%s tif=%s",
        side, symbol, quantity, price, time_in_force,
    )
    data = client.place_order(
        symbol=symbol,
        side=side,
        type="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce=time_in_force,
    )
    return _parse_result(data)


def place_stop_limit_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
    time_in_force: str = "GTC",
) -> OrderResult:
    """Place a STOP_LIMIT order (bonus order type)."""
    logger.info(
        "Placing STOP_LIMIT %s %s qty=%s price=%s stopPrice=%s tif=%s",
        side, symbol, quantity, price, stop_price, time_in_force,
    )
    data = client.place_order(
        symbol=symbol,
        side=side,
        type="STOP",
        quantity=quantity,
        price=price,
        stopPrice=stop_price,
        timeInForce=time_in_force,
    )
    return _parse_result(data)
