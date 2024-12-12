import pandas as pd
import streamlit as st
import sys
import io
from .scraper import AOCScraper
import logging
from datetime import datetime
import os
import glob
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Define campus color mapping
CAMPUS_COLORS = {
    'UDZ': '#00FF00',  # Green
    'BCN': '#FFD700',  # Yellow
    'MAL': '#00FFFF',  # Cyan
    'MAD': '#FF00FF'   # Magenta
}

def clean_old_files(except_file: str):
    """
    Remove all CSV files except the specified one.
    
    Args:
        except_file: Full path of the file to keep
    """
    try:
        data_dir = './data'
        csv_files = glob.glob(os.path.join(data_dir, 'aoc_rankings_*.csv'))
        
        deleted_count = 0
        for file in csv_files:
            if file != except_file:
                try:
                    os.remove(file)
                    deleted_count += 1
                    logger.info(f"Deleted old file: {file}")
                except Exception as e:
                    logger.error(f"Error deleting {file}: {str(e)}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old CSV files")
            
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def get_latest_csv() -> Tuple[str, Optional[datetime]]:
    """
    Get the most recent CSV file from the data directory.
    Returns (filepath, datetime) or ('', None) if no files found.
    """
    try:
        data_dir = './data'
        csv_files = glob.glob(os.path.join(data_dir, 'aoc_rankings_*.csv'))
        
        if not csv_files:
            logger.warning("No CSV files found in data directory")
            return '', None
            
        # Get the latest file based on filename timestamp
        latest_file = max(csv_files)
        
        # Extract timestamp from filename
        timestamp_str = os.path.basename(latest_file).split('_')[1].split('.')[0]
        timestamp = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
        
        logger.info(f"Found latest backup file: {latest_file} from {timestamp}")
        return latest_file, timestamp
        
    except Exception as e:
        logger.error(f"Error finding latest CSV: {str(e)}")
        return '', None

def load_backup_data() -> Optional[pd.DataFrame]:
    """Load data from the most recent CSV file."""
    filepath, timestamp = get_latest_csv()
    if not filepath:
        return None
        
    try:
        logger.info(f"Loading backup data from {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"Successfully loaded backup with {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error loading backup data: {str(e)}")
        return None

def load_data():
    """Load and cache data from scraper, falling back to backup CSV if scraping fails"""
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def _load():
        # Temporarily redirect stdout to capture scraper output
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            logger.info("Starting data load")
            scraper = AOCScraper()
            df = scraper.scrape_data()
            
            if df.empty:
                logger.warning("Scraping failed, attempting to load backup data")
                df = load_backup_data()
                if df is not None:
                    logger.info("Successfully loaded backup data")
                    st.warning("Could not fetch new data. Showing latest saved data.")
                else:
                    logger.error("Both scraping and backup loading failed")
                    st.error("Could not fetch new data or load backup.")
            else:
                # Save the fresh data
                filepath = scraper.save_data(df)
                if filepath:
                    logger.info(f"Fresh data saved to {filepath}")
                    # Clean up old files after successful save
                    clean_old_files(filepath)
            
            return df.sort_values('points', ascending=False).reset_index(drop=True) if df is not None else pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error in data loading: {str(e)}")
            # Try to load backup data in case of error
            df = load_backup_data()
            if df is not None:
                logger.info("Successfully loaded backup data after error")
                st.warning("Could not fetch new data. Showing latest saved data.")
                return df.sort_values('points', ascending=False).reset_index(drop=True)
            return pd.DataFrame()
            
        finally:
            # Always restore stdout
            sys.stdout = old_stdout
    
    return _load()

def get_current_aoc_day(df):
    """Get current day based on available day columns"""
    return len([col for col in df.columns if col.startswith('day_')])

def create_metrics_dataframe(df, is_global=True):
    """Create a formatted dataframe for metrics"""
    current_day = get_current_aoc_day(df)
    max_possible_stars = current_day * 2

    if is_global:
        total_users = len(df)
        active_users = len(df[df['points'] > 0])
        total_stars = df['total_stars'].sum()
        
        participation_rate = (active_users / total_users * 100) if total_users > 0 else 0
        total_success_rate = (total_stars / (total_users * max_possible_stars)) * 100
        active_success_rate = (total_stars / (active_users * max_possible_stars)) * 100 if active_users > 0 else 0
        
        data = [{
            'Section': '🌍 Global',
            'Students (Total / Active)': f"{total_users} / {active_users}",
            'Participation': f"{participation_rate:.1f}%",
            'Points (Avg / Max)': f"{df['points'].mean():.1f} / {df['points'].max():.1f}",
            'Streak (Avg / Max)': f"{df['streak'].mean():.1f} / {df['streak'].max()}",
            'Stars (Gold / Silver)': f"{int(df['gold_stars'].sum())} / {int(df['silver_stars'].sum())}",
            'Success Rate (Total / Active)': f"{total_success_rate:.1f}% / {active_success_rate:.1f}%"
        }]
    else:
        data = []
        for campus in sorted(df['campus'].unique()):
            campus_data = df[df['campus'] == campus]
            
            total_users = len(campus_data)
            active_users = len(campus_data[campus_data['points'] > 0])
            total_stars = campus_data['total_stars'].sum()
            
            participation_rate = (active_users / total_users * 100) if total_users > 0 else 0
            total_success_rate = (total_stars / (total_users * max_possible_stars)) * 100
            active_success_rate = (total_stars / (active_users * max_possible_stars)) * 100 if active_users > 0 else 0
            
            colored_campus = f"<span style='color: {CAMPUS_COLORS[campus]}'>🏛️ {campus}</span>"
            
            data.append({
                'Section': colored_campus,
                'Students (Total / Active)': f"{total_users} / {active_users}",
                'Participation': f"{participation_rate:.1f}%",
                'Points (Avg / Max)': f"{campus_data['points'].mean():.1f} / {campus_data['points'].max():.1f}",
                'Streak (Avg / Max)': f"{campus_data['streak'].mean():.1f} / {campus_data['streak'].max()}",
                'Stars (Gold / Silver)': f"{int(campus_data['gold_stars'].sum())} / {int(campus_data['silver_stars'].sum())}",
                'Success Rate (Total / Active)': f"{total_success_rate:.1f}% / {active_success_rate:.1f}%"
            })

    return pd.DataFrame(data)