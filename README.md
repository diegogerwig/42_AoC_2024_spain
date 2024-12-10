# 42 Spain | Advent of Code 2024 Dashboard

A Streamlit dashboard for analyzing and visualizing 42 Spain's Advent of Code 2024 rankings data.

## 🌟 Features

- Real-time scraping of AOC rankings from 42 Barcelona's website
- Campus-specific performance metrics
- Interactive data filtering and sorting
- Comprehensive visualizations:
  - Star distribution analysis
  - Progress tracking
  - Campus comparisons
  - Points distribution
  - Success rates
- Performance metrics by campus
- Detailed ranking tables
- Data caching for improved performance

## 🛠️ Requirements

- Python 3.10+
- Virtual environment support
- Make (for build automation)

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/diegogerwig/42_AoC_2024_spain.git
cd 42_AoC_2024_spain
```

2. Install system dependencies:
```bash
make system-deps
```

3. Install project dependencies:
```bash
make install
```

## 🚀 Usage

Run the dashboard:
```bash
make run
```

For a complete setup and run:
```bash
make local
```

## 📁 Project Structure

```
42_AoC_2024_spain/
├── src/
│   ├── __init__.py
│   ├── scraper.py         # Data scraping functionality
│   ├── app_utils.py       # Utility functions
│   ├── app_operations.py  # Dashboard operations
│   └── app_visualization.py # Data visualization
├── data/                  # Data storage (gitignored)
├── app.py                 # Streamlit application
├── requirements.txt       # Project dependencies
├── Makefile              # Build automation
└── README.md             # Project documentation
```

## 🧹 Maintenance

Clean temporary files and caches:
```bash
make clean
```

## 👨‍💻 Development Commands

- `make help`: Show available commands
- `make system-deps`: Install system dependencies
- `make install`: Set up virtual environment and install dependencies
- `make run`: Start the Streamlit dashboard
- `make clean`: Remove cache files
- `make local`: Clean, install, and run

## 🤝 Author

Developed by [Diego Gerwig](https://github.com/diegogerwig)

42 Intra Profile: [dgerwig-](https://profile.intra.42.fr/users/dgerwig-)