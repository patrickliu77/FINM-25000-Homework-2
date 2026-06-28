import os
import unittest
from unittest.mock import MagicMock, patch

from data_loader import AlpacaConfigurationError, authenticate_paper_account


class DataLoaderTests(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_credentials_raise_clear_error(self):
        with self.assertRaises(AlpacaConfigurationError):
            authenticate_paper_account()

    @patch.dict(os.environ, {"ALPACA_API_KEY": "key", "ALPACA_SECRET_KEY": "secret"}, clear=True)
    @patch("alpaca.trading.client.TradingClient")
    def test_authenticate_uses_paper_trading_client(self, trading_client):
        account = MagicMock()
        trading_client.return_value.get_account.return_value = account
        self.assertIs(authenticate_paper_account(), account)
        trading_client.assert_called_once_with("key", "secret", paper=True)


if __name__ == "__main__":
    unittest.main()
