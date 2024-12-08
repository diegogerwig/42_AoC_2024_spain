import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import Optional, Dict, List

class AOCScraper:
    def __init__(self):
        self.url = "https://aoc.42barcelona.com/ranking/es"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.star_mapping = {
            '★': 2,  # Gold star
            '☆': 1,  # Silver star
            'x': 0   # No star
        }

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
                'streak': cells[2].text.strip(),
                'points': cells[3].text.strip(),
            }

            # Initialize counters
            completed_days = 0
            gold_stars = 0
            silver_stars = 0

            # Process stars day by day
            star_cells = cells[4:]
            for i, cell in enumerate(star_cells):
                day_num = i + 1
                
                # Look for star spans within the cell
                star_spans = cell.find_all('span', class_='star1')
                num_stars = len(star_spans)
                
                # Determine star value based on number of spans
                if num_stars == 2:
                    value = 2  # Gold star (two spans)
                    gold_stars += 1
                    completed_days += 1
                elif num_stars == 1:
                    value = 1  # Silver star (one span)
                    silver_stars += 1
                    completed_days += 1
                else:
                    value = 0  # No star

                data[f'day_{day_num}'] = value

            # Add totals
            data['completed_days'] = completed_days
            data['gold_stars'] = gold_stars
            data['silver_stars'] = silver_stars

            return data
            
        except Exception as e:
            print(f"Error processing row: {str(e)}")
            return None

    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert numeric columns to their proper type."""
        numeric_cols = ['streak', 'points', 'completed_days', 'gold_stars', 'silver_stars']
        day_cols = [col for col in df.columns if col.startswith('day_')]
        numeric_cols.extend(day_cols)
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        return df

    def scrape_data(self) -> pd.DataFrame:
        """Scrape AOC rankings data."""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', id='rankingTable')
            
            if not table:
                print("Table not found")
                return pd.DataFrame()

            tbody = table.find('tbody')
            if not tbody:
                print("No tbody found")
                return pd.DataFrame()

            data = []
            for row in tbody.find_all('tr'):
                row_data = self._process_row(row)
                if row_data:
                    data.append(row_data)

            if not data:
                print("No data found")
                return pd.DataFrame()

            df = pd.DataFrame(data)
            df = self._convert_numeric_columns(df)
            
            df = df.sort_values('points', ascending=False).reset_index(drop=True)
            
            print(f"Scraped {len(df)} rows with {len(df.columns)} columns")
            return df
            
        except Exception as e:
            print(f"Error scraping data: {str(e)}")
            return pd.DataFrame()

    def get_column_descriptions(self) -> Dict[str, str]:
        """Get descriptions for all columns."""
        descriptions = {
            'login': 'User login name',
            'campus': 'Campus name',
            'streak': 'Current streak',
            'points': 'Total points',
            'completed_days': 'Number of days with at least one star',
            'gold_stars': 'Total number of gold stars',
            'silver_stars': 'Total number of silver stars'
        }
        
        for i in range(1, 26):
            descriptions[f'day_{i}'] = f'Day {i} star status (0=none, 1=silver, 2=gold)'
        
        return descriptions