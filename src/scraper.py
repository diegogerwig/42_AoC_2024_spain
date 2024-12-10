import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
import traceback
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class AOCScraper:
    def __init__(self):
        self.url = "https://aoc.42barcelona.com/ranking/es"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.data_dir = './data'
        os.makedirs(self.data_dir, exist_ok=True)
        logger.info(f"Data directory initialized: {self.data_dir}")

    def _process_row(self, row) -> Optional[Dict]:
        """Process a single row of data."""
        try:
            cells = row.find_all('td')
            if len(cells) < 5:
                return None

            # Basic data
            data = {
                'login': cells[0].text.strip(),
                'campus': cells[1].text.strip(),
                'streak': int(cells[2].text.strip()),
                'points': float(cells[3].text.strip()),
            }

            # Initialize counters
            completed_days = 0
            gold_stars = 0
            silver_stars = 0

            # Process stars day by day
            star_cells = cells[4:]
            for i, cell in enumerate(star_cells):
                day_num = i + 1
                
                # Get all star spans
                spans = cell.find_all('span')
                
                # Count gold and silver stars separately
                day_gold = len(cell.find_all('span', class_='star1'))  # Gold
                day_silver = len(cell.find_all('span', class_='star0'))  # Silver
                
                # Limit to maximum 2 stars per type
                day_gold = min(day_gold, 2)
                day_silver = min(day_silver, 2)
                
                # Update total counters
                gold_stars += day_gold
                silver_stars += day_silver
                
                # Update completed days if any stars were earned
                if (day_gold + day_silver > 0) and day_num > completed_days:
                    completed_days = day_num
                
                # Store total stars for the day (max 2)
                data[f'day_{day_num}'] = min(day_gold + day_silver, 2)

            # Add star totals
            data['completed_days'] = completed_days
            data['gold_stars'] = gold_stars
            data['silver_stars'] = silver_stars
            data['total_stars'] = gold_stars + silver_stars

            return data
            
        except Exception as e:
            logger.error(f"Error processing row: {str(e)}")
            return None

    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert numeric columns to their proper type."""
        numeric_cols = ['streak', 'points', 'completed_days', 
                       'gold_stars', 'silver_stars', 'total_stars']
        day_cols = [col for col in df.columns if col.startswith('day_')]
        numeric_cols.extend(day_cols)
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                # Keep points as float, convert others to int
                if col != 'points':
                    df[col] = df[col].astype(int)
        
        return df

    def scrape_data(self) -> pd.DataFrame:
        """Scrape AOC rankings data."""
        try:
            logger.info(f"Fetching data from {self.url}")
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            table = soup.find('table', id='rankingTable')
            if not table:
                logger.error("Ranking table not found")
                return pd.DataFrame()

            tbody = table.find('tbody')
            if not tbody:
                logger.error("Table body not found")
                return pd.DataFrame()

            data = []
            logger.info("Processing table rows...")
            for row in tbody.find_all('tr'):
                row_data = self._process_row(row)
                if row_data:
                    data.append(row_data)

            if not data:
                logger.error("No data found in table")
                return pd.DataFrame()

            logger.info("Converting data to DataFrame...")
            df = pd.DataFrame(data)
            df = self._convert_numeric_columns(df)
            return df.sort_values('points', ascending=False).reset_index(drop=True)
            
        except Exception as e:
            logger.error(f"Error scraping data: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return pd.DataFrame()

    def save_data(self, df: pd.DataFrame) -> str:
        """Save DataFrame to CSV and return filepath."""
        if df.empty:
            logger.error("Cannot save empty DataFrame")
            return ""
            
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'aoc_rankings_{timestamp}.csv'
            filepath = os.path.join(self.data_dir, filename)
            
            logger.info(f"Saving to {filepath}")
            df.to_csv(filepath, index=False)
            
            if os.path.exists(filepath):
                logger.info(f"File saved successfully ({os.path.getsize(filepath)} bytes)")
                return filepath
            return ""
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return ""

    def get_column_descriptions(self) -> Dict[str, str]:
        """Get descriptions for all columns."""
        return {
            'login': 'User login name',
            'campus': 'Campus name',
            'streak': 'Current streak of consecutive days completed',
            'points': 'Total points earned',
            'completed_days': 'Highest day number with at least one star',
            'gold_stars': 'Total number of gold stars',
            'silver_stars': 'Total number of silver stars',
            'total_stars': 'Total number of stars (gold + silver, max 2 per day)',
            **{f'day_{i}': f'Day {i} total stars (0-2, can be gold or silver)' 
               for i in range(1, 26)}
        }