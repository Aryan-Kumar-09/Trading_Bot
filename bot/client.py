"""Low-level Binance Futures Testnet REST client."""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logging

BASE_URL = "https://testnet.binancefuture.com"
logger = setup_logging()


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceClient:
    """Thin wrapper around the Binance Futures Testnet REST API."""

    def __init__(self, api_key: str, api_secret: str, timeout: int = 10) -> None:
        if not api_key or not api_secret:
            raise ValueError("Both API key and secret must be non-empty.")
        self._api_key = api_key
        self._api_secret = api_secret
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-MBX-APIKEY": self._api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.debug("BinanceClient initialised (base_url=%s)", BASE_URL)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> dict:
        """Append HMAC-SHA256 signature to params dict."""
        query = urlencode(params)
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _handle_response(self, response: requests.Response) -> dict:
        """Parse JSON; raise BinanceAPIError on API-level errors."""
        logger.debug(
            "HTTP %s %s -> status=%s",
            response.request.method,
            response.request.url,
            response.status_code,
        )
        try:
            data: Any = response.json()
        except ValueError:
            response.raise_for_status()
            raise BinanceAPIError(-1, "Non-JSON response from server.")

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            # Binance error responses have negative codes
            if int(data["code"]) < 0:
                raise BinanceAPIError(data["code"], data.get("msg", "Unknown error"))

        response.raise_for_status()
        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_exchange_info(self) -> dict:
        """Fetch exchange info (no auth required)."""
        url = f"{BASE_URL}/fapi/v1/exchangeInfo"
        logger.debug("GET exchangeInfo")
        try:
            resp = self._session.get(url, timeout=self._timeout)
            return self._handle_response(resp)
        except requests.RequestException as exc:
            logger.error("Network error on exchangeInfo: %s", exc)
            raise

    def get_account(self) -> dict:
        """Fetch account information (signed)."""
        params = {"timestamp": self._timestamp()}
        params = self._sign(params)
        url = f"{BASE_URL}/fapi/v2/account"
        logger.debug("GET account")
        try:
            resp = self._session.get(url, params=params, timeout=self._timeout)
            return self._handle_response(resp)
        except requests.RequestException as exc:
            logger.error("Network error on account: %s", exc)
            raise

    def place_order(self, **kwargs) -> dict:
        """
        Place a futures order.

        kwargs are forwarded directly as POST parameters.
        Required by Binance: symbol, side, type, quantity
        Optional: price (LIMIT), stopPrice (STOP_MARKET), timeInForce
        """
        params = {**kwargs, "timestamp": self._timestamp()}
        params = self._sign(params)
        url = f"{BASE_URL}/fapi/v1/order"

        logger.info("ORDER REQUEST  -> %s", {k: v for k, v in kwargs.items()})
        try:
            resp = self._session.post(url, data=params, timeout=self._timeout)
            result = self._handle_response(resp)
            logger.info("ORDER RESPONSE <- %s", result)
            return result
        except BinanceAPIError as exc:
            logger.error("Binance API error placing order: %s", exc)
            raise
        except requests.RequestException as exc:
            logger.error("Network error placing order: %s", exc)
            raise
