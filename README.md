# Robo Advisory Investment System

A professional web-based robo advisory application built with Streamlit that provides AI-driven portfolio recommendations and analysis.

## Features

- **Risk Profile Selection**: Choose between Conservative, Moderate, and Aggressive investment strategies
- **Portfolio Allocation**: Automatic asset allocation based on selected risk profile
  - Conservative: 70% Bonds (AGG), 30% Equity (SPY)
  - Moderate: 50% Bonds, 50% Equity
  - Aggressive: 20% Bonds, 80% Equity

- **Financial Analytics**:
  - Expected annual returns and volatility calculations
  - Sharpe ratio computation
  - Historical asset price trends

- **Monte Carlo Simulation**: 1000 simulations to project portfolio growth over your investment horizon
  - 5th, 50th, and 95th percentile outcomes
  - Best case, median, and worst-case scenarios

- **Efficient Frontier Analysis**: Visual representation of portfolio optimization across 5000 randomly generated portfolios

- **Correlation Analysis**: Asset correlation matrix to understand diversification benefits

- **Professional Features**:
  - Data caching for faster performance
  - Real-time market data from Yahoo Finance
  - Comprehensive error handling
  - Clean, responsive UI with matplotlib visualizations

## Installation

### Step 1: Install Python
Ensure you have Python 3.8 or higher installed on your system.

### Step 2: Install Dependencies
Navigate to the project directory and install required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

Execute the following command in the project directory:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage

1. **Sidebar Settings**:
   - View student information (Name & Roll Number)
   - Select your risk profile
   - Enter your investment amount
   - Specify your investment horizon (in years)

2. **Main Metrics**: View key portfolio statistics including expected return, volatility, and Sharpe ratio

3. **Visualizations**:
   - Portfolio allocation pie chart
   - Historical asset prices over 5 years
   - Monte Carlo simulation results
   - Efficient frontier scatter plot
   - Asset correlation heatmap

4. **Portfolio Details**: Review detailed breakdown of each asset in the portfolio

## Student Information

- **Name**: Mehak Gupta
- **Roll Number**: 2310991984

## Technical Stack

- **Python**: Core programming language
- **Streamlit**: Web framework for interactive dashboard
- **yfinance**: Real-time market data
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **matplotlib**: Professional data visualization

## Data Source

Historical stock data is fetched from Yahoo Finance using the `yfinance` library. The application uses 5 years of historical data for calculations.

## Performance Notes

- Data is cached for 1 hour to improve performance
- Initial load may take 30-60 seconds as market data is downloaded
- Monte Carlo simulations run with 1000 iterations for statistical accuracy

## Disclaimer

This application is for educational purposes only and does not constitute financial advice. Past performance does not guarantee future results. Always consult a qualified financial advisor before making investment decisions.

## Troubleshooting

### Issue: "Failed to download market data"
- Check your internet connection
- Ensure yfinance can access Yahoo Finance

### Issue: Slow performance
- Clear browser cache and restart the app
- Data is cached for 1 hour; subsequent runs within this period should be faster

### Issue: Import errors
- Verify all packages are installed: `pip install -r requirements.txt`
- Create a fresh virtual environment if conflicts exist

## License

Educational Project
