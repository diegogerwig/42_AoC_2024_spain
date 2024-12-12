# analytics/analytics_logger.py
import json
import time
from datetime import datetime
import logging
from pathlib import Path

class AnalyticsLogger:
    def __init__(self):
        # Configure logging
        self.log_dir = Path('analytics/logs')
        self.log_dir.mkdir(exist_ok=True, parents=True)
        
        logging.basicConfig(
            filename=self.log_dir / 'analytics.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Create analytics directory if it doesn't exist
        self.analytics_dir = Path('analytics/analytics_data')
        self.analytics_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize analytics data file
        self.data_file = self.analytics_dir / 'analytics_data.json'
        self.init_data_file()
    
    def init_data_file(self):
        """Initialize or load the analytics data file"""
        if not self.data_file.exists():
            initial_data = {
                'page_views': {},
                'button_clicks': {},
                'filter_usage': {},
                'search_queries': [],
                'session_data': [],
                'errors': []
            }
            self.save_data(initial_data)
    
    def load_data(self):
        """Load analytics data from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return self.init_data_file()
        except Exception as e:
            self.logger.error(f"Error loading analytics data: {e}")
            return None
    
    def save_data(self, data):
        """Save analytics data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving analytics data: {e}")
    
    def log_event(self, event_type, event_data):
        """Log an analytics event"""
        data = self.load_data()
        if not data:
            return
        
        timestamp = datetime.now().isoformat()
        
        if event_type == 'page_view':
            page = event_data
            data['page_views'][page] = data['page_views'].get(page, 0) + 1
            self.logger.info(f"Page view: {page}")
        
        elif event_type == 'button_click':
            button = event_data
            data['button_clicks'][button] = data['button_clicks'].get(button, 0) + 1
            self.logger.info(f"Button click: {button}")
        
        elif event_type == 'filter':
            filter_name, filter_value = event_data
            if filter_name not in data['filter_usage']:
                data['filter_usage'][filter_name] = []
            data['filter_usage'][filter_name].append({
                'value': filter_value,
                'timestamp': timestamp
            })
            self.logger.info(f"Filter usage: {filter_name} = {filter_value}")
        
        elif event_type == 'search':
            data['search_queries'].append({
                'query': event_data,
                'timestamp': timestamp
            })
            self.logger.info(f"Search query: {event_data}")
        
        elif event_type == 'error':
            data['errors'].append({
                'error': event_data,
                'timestamp': timestamp
            })
            self.logger.error(f"Error occurred: {event_data}")
        
        self.save_data(data)