import os
from unittest.mock import patch, mock_open, MagicMock
from currency_converter import CurrencyConverter
from datetime import date
import pytest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'code')))

import helper

@pytest.fixture
def mock_currency_converter():
    """Fixture to mock the CurrencyConverter instance."""
    mock_converter = MagicMock(spec=CurrencyConverter)
    mock_converter.currencies = {"USD", "EUR", "INR"}  # Example supported currencies
    return mock_converter

@patch("helper.CurrencyConverter")
@patch("helper.urllib.request.urlopen")
@patch("helper.open", new_callable=mock_open)
def test_get_currency_converter(mock_open_func, mock_urlopen, mock_currency_converter):
    """Test if the currency file is downloaded and converter is created."""
    # Mock the file download
    mock_urlopen.return_value.__enter__.return_value.read.return_value = b"mocked file content"

    # Ensure the file doesn't already exist
    currency_file_name = f"ecb_{date.today():%Y%m%d}.zip"
    if os.path.exists(currency_file_name):
        os.remove(currency_file_name)

    # Call the function
    converter = helper.get_currency_converter()

    # Assertions
    mock_open_func.assert_called_once_with(currency_file_name, "wb")
    mock_urlopen.assert_called_once()
    mock_currency_converter.assert_called_once_with(currency_file_name)
    assert converter == mock_currency_converter.return_value

@patch("helper.get_currency_converter")
def test_convert_currency_valid(mock_get_currency_converter, mock_currency_converter):
    """Test converting currency when currencies are supported."""
    mock_get_currency_converter.return_value = mock_currency_converter
    
    # Mock conversion result
    mock_currency_converter.convert.return_value = 100.5
    
    result = helper.convert_currency(100, "USD", "EUR")
    mock_currency_converter.convert.assert_called_once_with(100, "USD", "EUR")
    assert result == 100.5

def test_convert_currency_same_currency():
    """Test converting when source and target currencies are the same."""
    result = helper.convert_currency(100, "USD", "USD")
    assert result == 100

@patch("helper.get_currency_converter")
def test_convert_currency_unsupported_currency(mock_get_currency_converter, mock_currency_converter):
    """Test converting currency with unsupported currencies."""
    mock_get_currency_converter.return_value = mock_currency_converter
    mock_currency_converter.currencies = {"USD", "EUR"}
    
    with pytest.raises(ValueError, match="Unsupported currency conversion from INR to EUR"):
        helper.convert_currency(100, "INR", "EUR")

@patch("helper.get_currency_converter")
def test_get_currencies(mock_get_currency_converter, mock_currency_converter):
    """Test fetching the list of supported currencies."""
    mock_get_currency_converter.return_value = mock_currency_converter
    mock_currency_converter.currencies = {"USD", "EUR", "INR"}
    
    currencies = helper.get_currencies()
    assert currencies == ["EUR", "INR", "USD"]
