"""Input validation for trading bot CLI arguments."""

from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}


class ValidationError(ValueError):
    """Raised when user-supplied input is invalid."""


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s or not s.isalnum():
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Must be alphanumeric (e.g. BTCUSDT)."
        )
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return t


def validate_quantity(quantity: str | float) -> float:
    try:
        q = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if q <= 0:
        raise ValidationError(f"Quantity must be greater than zero, got {q}.")
    return q


def validate_price(price: str | float | None, order_type: str) -> float | None:
    """Price is required for LIMIT and STOP_LIMIT orders."""
    if order_type in ("LIMIT", "STOP_LIMIT"):
        if price is None:
            raise ValidationError(f"--price is required for {order_type} orders.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
        if p <= 0:
            raise ValidationError(f"Price must be greater than zero, got {p}.")
        return p
    return None


def validate_stop_price(stop_price: str | float | None, order_type: str) -> float | None:
    """Stop price is required for STOP_LIMIT orders."""
    if order_type == "STOP_LIMIT":
        if stop_price is None:
            raise ValidationError("--stop-price is required for STOP_LIMIT orders.")
        try:
            sp = float(stop_price)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid stop price '{stop_price}'. Must be a positive number.")
        if sp <= 0:
            raise ValidationError(f"Stop price must be greater than zero, got {sp}.")
        return sp
    return None
