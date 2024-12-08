import pytest
import requests
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from src.scraper import AOCScraper

def test_create_empty_dataframe():
    """Test creation of empty DataFrame."""
    scraper = AOCScraper()
    df = scraper._create_empty_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['login', 'campus', 'streak', 'points', 'days']
    assert len(df) == 0

def test_scraper_initialization():
    """Test scraper initialization."""
    scraper = AOCScraper()
    assert scraper.url == "https://aoc.42barcelona.com/ranking/es"
    assert isinstance(scraper.headers, dict)
    assert "Mozilla" in scraper.headers["User-Agent"]

def test_process_row_valid():
    """Test processing of valid row."""
    scraper = AOCScraper()
    cols = [
        MagicMock(text=" test_user "),  # Add spaces to test strip()
        MagicMock(text=" test_campus "),
        MagicMock(text=" 5 "),
        MagicMock(text=" 100 "),
        MagicMock(text=" 10 ")
    ]
    result = scraper._process_row(cols)
    assert result is not None
    assert result['login'] == "test_user"
    assert result['campus'] == "test_campus"
    assert result['streak'] == "5"
    assert result['points'] == "100"
    assert result['days'] == "10"

def test_process_row_none():
    """Test processing None input."""
    scraper = AOCScraper()
    result = scraper._process_row(None)
    assert result is None

def test_process_row_empty():
    """Test processing empty list."""
    scraper = AOCScraper()
    result = scraper._process_row([])
    assert result is None

def test_process_row_insufficient_columns():
    """Test processing row with insufficient columns."""
    scraper = AOCScraper()
    cols = [MagicMock(text="test_user")] * 4  # Only 4 columns
    result = scraper._process_row(cols)
    assert result is None

def test_convert_numeric_columns():
    """Test numeric column conversion."""
    scraper = AOCScraper()
    data = {
        'login': ['test_user'],
        'campus': ['test_campus'],
        'streak': ['5'],
        'points': ['100'],
        'days': ['10']
    }
    df = pd.DataFrame(data)
    result = scraper._convert_numeric_columns(df)
    assert result['streak'][0] == 5
    assert result['points'][0] == 100
    assert result['days'][0] == 10

@patch('requests.get')
def test_scrape_data_network_error(mock_get):
    """Test handling of network errors."""
    mock_get.side_effect = requests.RequestException("Network error")
    scraper = AOCScraper()
    df = scraper.scrape_data()
    assert len(df) == 0
    assert list(df.columns) == ['login', 'campus', 'streak', 'points', 'days']

@patch('requests.get')
def test_scrape_data_success(mock_get):
    """Test successful data scraping."""
    response = MagicMock()
    response.text = """
    <table>
        <tr>
            <td>test_user</td>
            <td>test_campus</td>
            <td>5</td>
            <td>100</td>
            <td>10</td>
        </tr>
    </table>
    """
    mock_get.return_value = response
    scraper = AOCScraper()
    df = scraper.scrape_data()
    assert len(df) == 1
    assert df.iloc[0]['login'] == 'test_user'
    assert df.iloc[0]['points'] == 100

@patch('requests.get')
def test_scrape_data_invalid_response(mock_get):
    """Test handling of invalid response data."""
    response = MagicMock()
    response.text = "invalid html"
    mock_get.return_value = response
    scraper = AOCScraper()
    df = scraper.scrape_data()
    assert len(df) == 0

@patch('requests.get')
def test_scrape_data_empty_table(mock_get):
    """Test handling of empty table."""
    response = MagicMock()
    response.text = "<table></table>"
    mock_get.return_value = response
    scraper = AOCScraper()
    df = scraper.scrape_data()
    assert len(df) == 0

def test_process_row_attribute_error():
    """Test handling of attribute error in row processing."""
    scraper = AOCScraper()
    mock_col = MagicMock()
    # Remove the text attribute to trigger AttributeError
    del mock_col.text  
    cols = [mock_col] * 5
    result = scraper._process_row(cols)
    assert result is None

@patch('requests.get')
def test_scrape_data_with_malformed_rows(mock_get):
    """Test scraping with malformed rows that trigger attribute errors."""
    response = MagicMock()
    response.text = """
    <table>
        <tr>
            <td>user1</td>
            <td>campus1</td>
            <td>5</td>
            <td>100</td>
        </tr>
        <tr>
            <td>user2</td>
            <td>campus2</td>
            <td>3</td>
            <td>75</td>
            <td>8</td>
        </tr>
    </table>
    """
    mock_get.return_value = response
    scraper = AOCScraper()
    df = scraper.scrape_data()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1  # Only one valid row
    assert df.iloc[0]['login'] == 'user2'

def test_process_stars():
    """Test star processing functionality."""
    scraper = AOCScraper()
    test_stars = "★☆x"  # Gold, Silver, None
    result = scraper._process_stars(test_stars)
    
    assert result['day_1'] == 2  # Gold star
    assert result['day_2'] == 1  # Silver star
    assert result['day_3'] == 0  # No star

@patch('requests.get')
def test_scrape_data_with_stars(mock_get):
    """Test scraping with star data."""
    response = MagicMock()
    response.text = """
    <table>
        <tr>
            <td>test_user</td>
            <td>test_campus</td>
            <td>5</td>
            <td>100</td>
            <td>★☆x</td>
        </tr>
    </table>
    """
    mock_get.return_value = response
    scraper = AOCScraper()
    df = scraper.scrape_data()
    
    assert len(df) == 1
    assert df.iloc[0]['login'] == 'test_user'
    assert df.iloc[0]['points'] == 100
    assert df.iloc[0]['day_1'] == 2
    assert df.iloc[0]['day_2'] == 1
    assert df.iloc[0]['day_3'] == 0
    assert df.iloc[0]['completed_days'] == 2
    assert df.iloc[0]['gold_stars'] == 1
    assert df.iloc[0]['silver_stars'] == 1
