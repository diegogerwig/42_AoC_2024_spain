import pytest
import pandas as pd
from src.analyzer import AOCAnalyzer

def test_analyzer_statistics():
    # Create sample data
    data = {
        'login': ['user1', 'user2'],
        'campus': ['campus1', 'campus1'],
        'streak': [5, 3],
        'points': [100, 50],
        'days': [10, 5]
    }
    df = pd.DataFrame(data)
    
    stats = AOCAnalyzer.generate_statistics(df)
    
    assert isinstance(stats, dict)
    assert 'general' in stats
    assert stats['general']['total_users'] == 2
    assert stats['general']['unique_campuses'] == 1

def test_analyzer_top_users():
    data = {
        'login': ['user1', 'user2', 'user3'],
        'points': [100, 50, 75]
    }
    df = pd.DataFrame(data)
    
    top = AOCAnalyzer.get_top_users(df, n=2)
    assert len(top) == 2
    assert top.iloc[0]['points'] == 100