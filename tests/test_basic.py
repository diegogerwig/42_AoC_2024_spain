from src.scraper import AOCScraper
import pytest

def test_scraper_exists():
    scraper = AOCScraper()
    assert isinstance(scraper, AOCScraper)