import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Robo Advisory System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .sidebar .sidebar-content {
        padding: 2rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# CACHING FUNCTIONS
# ============================================================================

@st.cache_data(ttl=3600)
def generate_synthetic_data(ticker, years=5):
    """Generate synthetic historical data for demonstration purposes."""
    np.random.seed(hash(ticker) % 2**32)
    dates = pd.date_range(end=datetime.now(), periods=252*years, freq='D')
    
    # Generate realistic price movements
    if ticker == 'AGG':
        # Bond price movement (lower volatility, lower return)
        daily_return = 0.0003
        volatility = 0.005
    else:
        # Equity price movement (higher volatility, higher return)
        daily_return = 0.0004
        volatility = 0.012
    
    # Generate returns without extreme values
    returns = np.clip(np.random.normal(daily_return, volatility, len(dates)), -0.1, 0.1)
    
    # Generate prices with exponential growth
    prices = 100 * np.exp(np.cumsum(returns))
    
    series = pd.Series(prices, index=dates)
    
    # Ensure no NaN or inf values
    series = series.replace([np.inf, -np.inf], np.nan)
    series = series.dropna()
    
    return series

@st.cache_data(ttl=3600)
def download_yfinance_data(ticker, years=5):
    """Download historical stock data from Yahoo Finance with caching."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*years)
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data is None or data.empty:
            return generate_synthetic_data(ticker, years)
        return data['Adj Close']
    except Exception as e:
        return generate_synthetic_data(ticker, years)

@st.cache_data
def calculate_portfolio_metrics(_prices_dict, _weights, annual_trading_days=252):
    """Calculate portfolio metrics from price data."""
    try:
        # Get list of tickers from prices_dict
        tickers_list = list(_prices_dict.keys())
        
        # Calculate daily returns for each asset
        all_returns = {}
        for ticker in tickers_list:
            prices = _prices_dict[ticker]
            if prices is not None and len(prices) > 1:
                ret = prices.pct_change().dropna()
                if len(ret) > 10:
                    all_returns[ticker] = ret
        
        if len(all_returns) < 2:
            st.error(f"Not enough assets with valid data. Need 2, got {len(all_returns)}")
            return None, None, None
        
        # Create dataframe with outer join to get all dates
        returns_df = pd.DataFrame(all_returns)
        
        # Fill NaN values - use forward fill then backward fill
        returns_df = returns_df.fillna(0)  # Fill with 0 (conservative approach)
        
        # Remove rows that are all zeros (if they exist)
        returns_df = returns_df[(returns_df != 0).any(axis=1)]
        
        if len(returns_df) < 10:
            st.error(f"After cleaning: only {len(returns_df)} valid rows. Need at least 10")
            return None, None, None
        
        st.success(f"✅ Using {len(returns_df)} valid trading days for calculations")
        
        # Calculate annualized metrics
        mean_returns = returns_df.mean() * annual_trading_days
        volatility = returns_df.std() * np.sqrt(annual_trading_days)
        
        # Ensure no NaN values
        mean_returns = mean_returns.fillna(0.01)
        volatility = volatility.fillna(0.05)
        
        # Portfolio metrics
        portfolio_return = float(np.sum(_weights * mean_returns.values))
        correlation_matrix = returns_df.corr()
        cov_matrix = returns_df.cov() * annual_trading_days
        
        portfolio_volatility = float(np.sqrt(np.dot(_weights, np.dot(cov_matrix.values, _weights))))
        
        # Ensure values are positive and not NaN
        portfolio_return = max(float(np.nan_to_num(portfolio_return, 0.001)), 0.001)
        portfolio_volatility = max(float(np.nan_to_num(portfolio_volatility, 0.05)), 0.001)
        
        return {
            'returns': mean_returns,
            'volatility': volatility,
            'portfolio_return': portfolio_return,
            'portfolio_volatility': portfolio_volatility,
            'cov_matrix': cov_matrix,
            'returns_df': returns_df
        }, correlation_matrix, returns_df
            
    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")
        return None, None, None

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

st.sidebar.title("📊 Robo Advisory System")
st.sidebar.markdown("---")

# Student Information
st.sidebar.subheader("Student Information")
st.sidebar.write("**Name:** Mehak Gupta")
st.sidebar.write("**Roll Number:** 2310991984")
st.sidebar.markdown("---")

# Risk Profile Selection
st.sidebar.subheader("📈 Investment Parameters")
risk_profile = st.sidebar.selectbox(
    "Select Risk Profile",
    ["Conservative", "Moderate", "Aggressive"],
    help="Choose your investment risk tolerance"
)

# Investment Amount
investment_amount = st.sidebar.number_input(
    "Investment Amount ($)",
    min_value=100.0,
    max_value=1000000.0,
    value=10000.0,
    step=1000.0,
    help="Enter your initial investment amount"
)

# Investment Horizon
investment_horizon = st.sidebar.number_input(
    "Investment Horizon (Years)",
    min_value=1,
    max_value=50,
    value=10,
    help="How long do you plan to invest?"
)

st.sidebar.markdown("---")

# ============================================================================
# PORTFOLIO ALLOCATION BASED ON RISK PROFILE
# ============================================================================

# Define asset allocation based on risk profile
allocation_dict = {
    "Conservative": {"AGG": 0.70, "SPY": 0.30},
    "Moderate": {"AGG": 0.50, "SPY": 0.50},
    "Aggressive": {"AGG": 0.20, "SPY": 0.80}
}

tickers = list(allocation_dict[risk_profile].keys())
weights = np.array(list(allocation_dict[risk_profile].values()))

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
st.title("🤖 Robo Advisory Investment System")
st.markdown(f"**Risk Profile:** {risk_profile} | **Investment Amount:** ${investment_amount:,.2f} | **Horizon:** {investment_horizon} years")
st.markdown("---")

# Load data
st.info("📥 Loading historical data... (This may take a moment)")
prices_data = {}
for ticker in tickers:
    prices_data[ticker] = download_yfinance_data(ticker, years=5)

# Validate loaded data
data_valid = True
for ticker, prices in prices_data.items():
    if prices is None or prices.empty:
        st.warning(f"⚠️ No data for {ticker}")
        data_valid = False
    elif len(prices) < 10:
        st.warning(f"⚠️ Insufficient data for {ticker}: {len(prices)} records")
        data_valid = False

# Check if data was loaded successfully
if all(prices is not None and not prices.empty for prices in prices_data.values()) and len(prices_data) == len(tickers):
    # Calculate metrics
    metrics, correlation_matrix, returns_df = calculate_portfolio_metrics(prices_data, weights)
    
    if metrics is not None:
        # ====================================================================
        # ROW 1: KEY METRICS
        # ====================================================================
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Expected Annual Return",
                f"{metrics['portfolio_return']*100:.2f}%",
                help="Annualized portfolio return based on historical data"
            )
        
        with col2:
            st.metric(
                "Annual Volatility",
                f"{metrics['portfolio_volatility']*100:.2f}%",
                help="Portfolio standard deviation (risk measure)"
            )
        
        with col3:
            sharpe_ratio = metrics['portfolio_return'] / metrics['portfolio_volatility'] if metrics['portfolio_volatility'] > 0 else 0
            st.metric(
                "Sharpe Ratio",
                f"{sharpe_ratio:.2f}",
                help="Risk-adjusted return metric (higher is better)"
            )
        
        with col4:
            st.metric(
                "5-Year Historical Return",
                f"{((prices_data[tickers[0]].iloc[-1] / prices_data[tickers[0]].iloc[0]) - 1) * 100:.2f}%",
                help="Actual return over 5-year period"
            )
        
        st.markdown("---")
        
        # ====================================================================
        # ROW 2: VISUALIZATIONS
        # ====================================================================
        col_left, col_right = st.columns(2)
        
        # Portfolio Allocation Pie Chart
        with col_left:
            st.subheader("Portfolio Allocation")
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            wedges, texts, autotexts = ax1.pie(
                weights, 
                labels=tickers, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colors[:len(tickers)],
                textprops={'fontsize': 11, 'weight': 'bold'}
            )
            ax1.set_title(f'{risk_profile} Portfolio Allocation', fontsize=13, weight='bold', pad=20)
            plt.tight_layout()
            st.pyplot(fig1)
        
        # Asset Prices Over Time
        with col_right:
            st.subheader("Historical Asset Prices (5 Years)")
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            
            for i, ticker in enumerate(tickers):
                normalized_prices = (prices_data[ticker] / prices_data[ticker].iloc[0]) * 100
                ax2.plot(normalized_prices.index, normalized_prices.values, 
                        label=ticker, linewidth=2.5, color=colors[i])
            
            ax2.set_xlabel('Date', fontsize=10, weight='bold')
            ax2.set_ylabel('Normalized Price (Base = 100)', fontsize=10, weight='bold')
            ax2.set_title('Asset Price Trends (Normalized)', fontsize=13, weight='bold')
            ax2.legend(loc='best', fontsize=10)
            ax2.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig2)
        
        # ====================================================================
        # MONTE CARLO SIMULATION
        # ====================================================================
        st.subheader("📊 Monte Carlo Simulation (1000 Simulations)")
        
        with st.spinner("Running Monte Carlo simulation..."):
            try:
                np.random.seed(42)
                num_simulations = 1000
                num_trading_days = investment_horizon * 252
                
                # Prepare data for simulation
                final_values = np.zeros(num_simulations)
                simulated_paths = np.zeros((num_trading_days, num_simulations))
                
                # Calculate portfolio daily return and volatility
                portfolio_daily_return = metrics['portfolio_return'] / 252
                portfolio_daily_volatility = metrics['portfolio_volatility'] / np.sqrt(252)
                
                # Run simulations
                for sim in range(num_simulations):
                    portfolio_value = investment_amount
                    daily_returns = np.random.normal(
                        portfolio_daily_return,
                        portfolio_daily_volatility,
                        num_trading_days
                    )
                    
                    for day in range(num_trading_days):
                        portfolio_value *= (1 + daily_returns[day])
                        simulated_paths[day, sim] = portfolio_value
                    
                    final_values[sim] = portfolio_value
                
                # Calculate statistics
                percentile_5 = np.percentile(final_values, 5)
                percentile_50 = np.percentile(final_values, 50)
                percentile_95 = np.percentile(final_values, 95)
                
                # Display statistics
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                with stat_col1:
                    st.metric(
                        "Worst Case (5%)",
                        f"${percentile_5:,.0f}",
                        f"{((percentile_5/investment_amount - 1)*100):.1f}%"
                    )
                
                with stat_col2:
                    st.metric(
                        "Median (50%)",
                        f"${percentile_50:,.0f}",
                        f"{((percentile_50/investment_amount - 1)*100):.1f}%"
                    )
                
                with stat_col3:
                    st.metric(
                        "Best Case (95%)",
                        f"${percentile_95:,.0f}",
                        f"{((percentile_95/investment_amount - 1)*100):.1f}%"
                    )
                
                with stat_col4:
                    st.metric(
                        "Expected Value",
                        f"${np.mean(final_values):,.0f}",
                        f"{((np.mean(final_values)/investment_amount - 1)*100):.1f}%"
                    )
                
                # Plot simulation paths
                fig3, ax3 = plt.subplots(figsize=(12, 6))
                
                # Plot all simulation paths
                for sim in range(num_simulations):
                    ax3.plot(simulated_paths[:, sim], alpha=0.01, color='steelblue')
                
                # Plot percentiles
                days = np.arange(num_trading_days)
                percentile_5_path = np.percentile(simulated_paths, 5, axis=1)
                percentile_50_path = np.percentile(simulated_paths, 50, axis=1)
                percentile_95_path = np.percentile(simulated_paths, 95, axis=1)
                
                ax3.plot(days, percentile_5_path, color='red', linewidth=2, label='5th Percentile', linestyle='--')
                ax3.plot(days, percentile_50_path, color='green', linewidth=2.5, label='Median')
                ax3.plot(days, percentile_95_path, color='darkgreen', linewidth=2, label='95th Percentile', linestyle='--')
                
                ax3.axhline(y=investment_amount, color='black', linestyle=':', linewidth=2, label='Initial Investment')
                ax3.fill_between(days, percentile_5_path, percentile_95_path, alpha=0.1, color='steelblue')
                
                ax3.set_xlabel('Trading Days', fontsize=11, weight='bold')
                ax3.set_ylabel('Portfolio Value ($)', fontsize=11, weight='bold')
                ax3.set_title(f'Monte Carlo Simulation: {num_simulations} Paths ({investment_horizon} Years)', 
                             fontsize=13, weight='bold')
                ax3.legend(loc='upper left', fontsize=10)
                ax3.grid(True, alpha=0.3)
                ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
                plt.tight_layout()
                st.pyplot(fig3)
                
                st.markdown("---")
                
            except Exception as e:
                st.error(f"Error running simulation: {str(e)}")
        
        # ====================================================================
        # EFFICIENT FRONTIER
        # ====================================================================
        st.subheader("📈 Efficient Frontier Analysis")
        
        with st.spinner("Calculating efficient frontier..."):
            try:
                # Generate random portfolios
                num_portfolios = 5000
                np.random.seed(42)
                
                results = np.zeros((3, num_portfolios))
                weighted_allocations = np.zeros((num_portfolios, len(tickers)))
                
                for i in range(num_portfolios):
                    # Generate random weights
                    random_weights = np.random.random(len(tickers))
                    random_weights /= np.sum(random_weights)
                    weighted_allocations[i] = random_weights
                    
                    # Calculate portfolio return and volatility
                    portfolio_ret = np.sum(metrics['returns'] * random_weights)
                    portfolio_vol = np.sqrt(np.dot(random_weights, np.dot(metrics['cov_matrix'], random_weights)))
                    
                    # Calculate Sharpe ratio
                    sharpe = portfolio_ret / portfolio_vol if portfolio_vol > 0 else 0
                    
                    results[0, i] = portfolio_vol
                    results[1, i] = portfolio_ret
                    results[2, i] = sharpe
                
                # Find maximum Sharpe ratio portfolio
                max_sharpe_idx = np.argmax(results[2])
                max_sharpe_return = results[1, max_sharpe_idx]
                max_sharpe_volatility = results[0, max_sharpe_idx]
                
                # Plot efficient frontier
                fig4, ax4 = plt.subplots(figsize=(10, 7))
                
                # Scatter plot of random portfolios
                scatter = ax4.scatter(
                    results[0, :] * 100, 
                    results[1, :] * 100, 
                    c=results[2, :], 
                    cmap='viridis', 
                    alpha=0.5,
                    s=30,
                    edgecolors='none'
                )
                
                # Plot current portfolio
                ax4.scatter(
                    metrics['portfolio_volatility'] * 100,
                    metrics['portfolio_return'] * 100,
                    marker='*',
                    color='red',
                    s=800,
                    label=f'{risk_profile} Portfolio',
                    edgecolors='darkred',
                    linewidth=1.5
                )
                
                # Plot maximum Sharpe ratio portfolio
                ax4.scatter(
                    max_sharpe_volatility * 100,
                    max_sharpe_return * 100,
                    marker='D',
                    color='gold',
                    s=300,
                    label='Max Sharpe Ratio',
                    edgecolors='orange',
                    linewidth=1.5
                )
                
                # Add colorbar
                cbar = plt.colorbar(scatter, ax=ax4)
                cbar.set_label('Sharpe Ratio', fontsize=10, weight='bold')
                
                ax4.set_xlabel('Volatility (Annual %)', fontsize=11, weight='bold')
                ax4.set_ylabel('Expected Return (Annual %)', fontsize=11, weight='bold')
                ax4.set_title('Efficient Frontier - Portfolio Analysis (5000 Random Portfolios)', 
                             fontsize=13, weight='bold')
                ax4.legend(loc='best', fontsize=10)
                ax4.grid(True, alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig4)
                
            except Exception as e:
                st.error(f"Error calculating efficient frontier: {str(e)}")
        
        st.markdown("---")
        
        # ====================================================================
        # CORRELATION MATRIX HEATMAP
        # ====================================================================
        st.subheader("🔗 Asset Correlation Matrix")
        
        fig5, ax5 = plt.subplots(figsize=(8, 6))
        
        # Create correlation matrix heatmap
        im = ax5.imshow(correlation_matrix, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
        
        # Set ticks and labels
        ax5.set_xticks(np.arange(len(tickers)))
        ax5.set_yticks(np.arange(len(tickers)))
        ax5.set_xticklabels(tickers)
        ax5.set_yticklabels(tickers)
        
        # Add correlation values
        for i in range(len(tickers)):
            for j in range(len(tickers)):
                text = ax5.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                              ha="center", va="center", color="black", fontweight='bold')
        
        plt.colorbar(im, ax=ax5, label='Correlation')
        ax5.set_title('Asset Correlation Matrix', fontsize=13, weight='bold')
        plt.tight_layout()
        st.pyplot(fig5)
        
        st.markdown("---")
        
        # ====================================================================
        # PORTFOLIO DETAILS TABLE
        # ====================================================================
        st.subheader("📋 Portfolio Details")
        
        portfolio_details = pd.DataFrame({
            'Asset': tickers,
            'Allocation': [f"{w*100:.1f}%" for w in weights],
            'Investment Amount': [f"${investment_amount * w:,.2f}" for w in weights],
            'Annual Return': [f"{metrics['returns'][ticker]*100:.2f}%" for ticker in tickers],
            'Annual Volatility': [f"{metrics['volatility'][ticker]*100:.2f}%" for ticker in tickers],
            'Current Price': [f"${prices_data[ticker].iloc[-1]:.2f}" for ticker in tickers]
        })
        
        st.dataframe(portfolio_details, use_container_width=True)
        
        st.markdown("---")
        
        # ====================================================================
        # DISCLAIMER
        # ====================================================================
        st.info("""
        **⚠️ DISCLAIMER:** This is an educational tool for demonstration purposes only. 
        It does not constitute financial advice. Past performance does not guarantee future results. 
        Please consult a qualified financial advisor before making investment decisions.
        
        **Note:** If live market data is unavailable (network issues), the application uses synthetic 
        historical data for demonstration purposes.
        """)
    
    else:
        st.error("Failed to calculate portfolio metrics. Please try again.")
else:
    st.error("Failed to download market data. Please check your internet connection and try again.")
