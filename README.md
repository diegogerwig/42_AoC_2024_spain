# 42 AOC 2024 Spain Data Analyzer

A data analysis tool for 42 Spain Advent of Code rankings.

## Features

- Web scraping of AOC rankings
- Statistical analysis of student performance
- Interactive visualizations
- Real-time data updates
- Comprehensive test coverage

## Requirements

- Python 3.10+
- Virtual environment support
- Make (for build automation)

## Installation

1. Clone the repository:
```bash
git clone 
cd 42_aoc_analyzer
```

2. Install system dependencies:
```bash
make system-deps
```

3. Install project dependencies:
```bash
make install
```

## Usage

Run the application:
```bash
make run
```

Run tests:
```bash
make test
```

## Development

- `make clean`: Clean temporary files
- `make test`: Run tests with coverage
- `make format`: Format code using black
- `make lint`: Run linter checks

## Project Structure

- `src/`: Source code
  - `scraper.py`: Data collection
  - `analyzer.py`: Data analysis
  - `visualizer.py`: Data visualization
- `tests/`: Test files
- `app.py`: Streamlit application

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Project Structure

42_AoC_2024_data/
├── src/
│   ├── __init__.py
│   ├── scraper.py         # Data scraping functionality
│   ├── analyzer.py        # Statistical analysis
│   └── visualizer.py      # Data visualization
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py
│   ├── test_analyzer.py
│   └── test_visualizer.py
├── app.py                 # Streamlit application
├── requirements.txt       # Project dependencies
├── Makefile              # Build automation
├── README.md             # Project documentation
└── LICENSE
