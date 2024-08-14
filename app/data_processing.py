import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import plotly.graph_objects as go
import logging
import os

logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.getenv('DATABASE_URL')

def normalize_data(df, method='min_max'):
    if method == 'min_max':
        df['price'] = (df['price'] - df['price'].min()) / (df['price'].max() - df['price'].min())
    elif method == 'z_score':
        df['price'] = (df['price'] - df['price'].mean()) / df['price'].std()
    elif method == 'log':
        df['price'] = np.log1p(df['price'])
    elif method == 'scale':
        df['price'] = (df['price'] - df['price'].min()) / (df['price'].max() - df['price'].min()) * 100
    else:
        raise ValueError("Unknown normalization method")
    return df

def get_combined_data():
    try:
        # Create a SQLAlchemy engine
        engine = create_engine(DATABASE_URL)

        # Fetch data from Bitcoin table
        query_bitcoin = "SELECT date AS date, price FROM bitcoin_prices"
        df_bitcoin = pd.read_sql(query_bitcoin, engine)
        df_bitcoin['crypto'] = 'bitcoin'

        # Fetch data from Ethereum table
        query_ethereum = "SELECT date AS date, price FROM ethereum_prices"
        df_ethereum = pd.read_sql(query_ethereum, engine)
        df_ethereum['crypto'] = 'ethereum'

        # Fetch data from Tether table
        query_tether = "SELECT date AS date, price FROM tether_prices"
        df_tether = pd.read_sql(query_tether, engine)
        df_tether['crypto'] = 'tether'

        # Combine data from all tables
        df_combined = pd.concat([df_bitcoin, df_ethereum, df_tether])

        # Convert 'date' column to datetime format and set it as index
        df_combined['date'] = pd.to_datetime(df_combined['date'])
        df_combined.set_index('date', inplace=True)

        # Normalize data
        # df_combined = normalize_data(df_combined, method='scale')  # Uncomment this line if normalization is required
        return df_combined
    except Exception as e:
        logging.error(f"Error fetching combined data: {e}")
        raise

def get_resampled_data():
    df_combined = get_combined_data()
    
    # Resample and compute OHLC for each cryptocurrency
    df_combined.index = pd.to_datetime(df_combined.index)
    df_resampled = df_combined.groupby('crypto').resample('D').price.ohlc().reset_index()
    df_resampled.set_index(['crypto', 'date'], inplace=True)
    
    df_resampled.reset_index(inplace=True)
    df_resampled['date'] = df_resampled['date'].dt.date
    return df_resampled

def get_line_graph_data():
    try:
        # Create a SQLAlchemy engine
        engine = create_engine(DATABASE_URL)

        # Fetch data from Bitcoin table
        query_bitcoin = "SELECT date AS date, price FROM bitcoin_prices"
        df_bitcoin = pd.read_sql(query_bitcoin, engine)

        # Fetch data from Ethereum table
        query_ethereum = "SELECT date AS date, price FROM ethereum_prices"
        df_ethereum = pd.read_sql(query_ethereum, engine)

        # Fetch data from Tether table
        query_tether = "SELECT date AS date, price FROM tether_prices"
        df_tether = pd.read_sql(query_tether, engine)

        # Convert 'date' column to datetime format
        df_bitcoin['date'] = pd.to_datetime(df_bitcoin['date'])
        df_ethereum['date'] = pd.to_datetime(df_ethereum['date'])
        df_tether['date'] = pd.to_datetime(df_tether['date'])

        # Prepare data for line graphs
        bitcoin_dates = df_bitcoin['date'].dt.strftime('%Y-%m-%d').tolist()
        bitcoin_prices = df_bitcoin['price'].tolist()
        ethereum_dates = df_ethereum['date'].dt.strftime('%Y-%m-%d').tolist()
        ethereum_prices = df_ethereum['price'].tolist()
        tether_dates = df_tether['date'].dt.strftime('%Y-%m-%d').tolist()
        tether_prices = df_tether['price'].tolist()

        return bitcoin_dates, bitcoin_prices, ethereum_dates, ethereum_prices, tether_dates, tether_prices
    except Exception as e:
        logging.error(f"Error fetching line graph data: {e}")
        raise

def calculate_rolling_volatility(df, window=30):
    # Ensure no SettingWithCopyWarning by using .loc
    df = df.copy()  # Make a copy to avoid modifying the original DataFrame
    df.loc[:, 'returns'] = df['price'].pct_change()
    df.loc[:, 'volatility'] = df['returns'].rolling(window=window).std() * np.sqrt(window)
    return df

def generate_volatility_graph():
    df_combined = get_combined_data()
    
    # Separate by cryptocurrency
    df_bitcoin = df_combined.loc[df_combined['crypto'] == 'bitcoin'].copy()
    df_ethereum = df_combined.loc[df_combined['crypto'] == 'ethereum'].copy()
    df_tether = df_combined.loc[df_combined['crypto'] == 'tether'].copy()
    
    # Calculate rolling volatility
    df_bitcoin_vol = calculate_rolling_volatility(df_bitcoin)
    df_ethereum_vol = calculate_rolling_volatility(df_ethereum)
    df_tether_vol = calculate_rolling_volatility(df_tether)
    
    # Create traces for Plotly
    trace_bitcoin = go.Scatter(x=df_bitcoin_vol.index, y=df_bitcoin_vol['volatility'], mode='lines', name='Bitcoin Volatility')
    trace_ethereum = go.Scatter(x=df_ethereum_vol.index, y=df_ethereum_vol['volatility'], mode='lines', name='Ethereum Volatility')
    trace_tether = go.Scatter(x=df_tether_vol.index, y=df_tether_vol['volatility'], mode='lines', name='Tether Volatility')
    
    # Create layout and figure
    layout = go.Layout(title='Rolling Volatility Comparison', xaxis=dict(title='Date'), yaxis=dict(title='Volatility'))
    fig = go.Figure(data=[trace_bitcoin, trace_ethereum, trace_tether], layout=layout)
    
    return fig.to_html(full_html=False)  # Return HTML to be embedded in the template
