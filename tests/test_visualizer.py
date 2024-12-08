import pytest
import pandas as pd
import matplotlib.pyplot as plt
from src.visualizer import AOCVisualizer

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'login': ['user1', 'user2', 'user3'],
        'campus': ['campus1', 'campus2', 'campus1'],
        'streak': [5, 3, 4],
        'points': [100, 50, 75],
        'days': [10, 5, 7]
    })

@pytest.fixture
def sample_stats():
    return {
        'correlations': pd.DataFrame({
            'points': [1.0, 0.8, 0.7],
            'streak': [0.8, 1.0, 0.6],
            'days': [0.7, 0.6, 1.0]
        }, index=['points', 'streak', 'days'])
    }

def test_plot_points_distribution(sample_data):
    fig = AOCVisualizer.plot_points_distribution(sample_data)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_correlation_matrix(sample_stats):
    fig = AOCVisualizer.plot_correlation_matrix(sample_stats)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_streak_distribution(sample_data):
    fig = AOCVisualizer.plot_streak_distribution(sample_data)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_points_vs_days(sample_data):
    fig = AOCVisualizer.plot_points_vs_days(sample_data)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)

def test_plot_top_users(sample_data):
    fig = AOCVisualizer.plot_top_users(sample_data, n=2)
    assert isinstance(fig, plt.Figure)
    plt.close(fig)