import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import plotly.graph_objects as go
import logging
import os
import requests

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
        
        #Fix dates
        df_combined['date'] = pd.to_datetime(df_combined['date'])
        df_combined.set_index('date', inplace=True)

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

        # Fix the dates
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
    df = df.copy()
    df.loc[:, 'returns'] = df['price'].pct_change()
    df.loc[:, 'volatility'] = df['returns'].rolling(window=window).std() * np.sqrt(window)
    return df

def generate_volatility_graph():
    df_combined = get_combined_data()
    
    # Put each currency in its own dataframe
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

    layout = go.Layout(title='Rolling Volatility Comparison', xaxis=dict(title='Date'), yaxis=dict(title='Volatility'))
    fig = go.Figure(data=[trace_bitcoin, trace_ethereum, trace_tether], layout=layout)
    
    return fig.to_html(full_html=False)

def get_sunburst_data():
    base_url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 10,
        'page': 1,
        'sparkline': False
    }
    
    logging.info("Fetching market data from CoinGecko API...")
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        market_data = response.json()
        # logging.info("Market data fetched successfully.")
        
        if not market_data:
            logging.warning("No market data returned from API.")
            return None
        
        # Create the top level category, which is the market capitalization of all cryptocurrencies
        sunburst_data = {
            'labels': ['Crypto Market'],
            'parents': [''],
            'values': [sum(coin['market_cap'] for coin in market_data)],
            'hovertext': ['Total market capitalization of top 10 cryptocurrencies']
        }
        
        categories = {
            'Top 3': ['bitcoin', 'ethereum', 'tether'],
            'Others': [coin['id'] for coin in market_data if coin['id'] not in ['bitcoin', 'ethereum', 'tether']]
        }
        
        # Break the values into second level categories, top 3 and other
        top_3_value = sum(coin['market_cap'] for coin in market_data if coin['id'] in categories['Top 3'])
        others_value = sum(coin['market_cap'] for coin in market_data if coin['id'] not in categories['Top 3'])
        
        # Setup the sunburst labels and parents for second level categories
        sunburst_data['labels'].append('Top 3')
        sunburst_data['parents'].append('Crypto Market')
        sunburst_data['values'].append(top_3_value)
        sunburst_data['hovertext'].append('Combined market cap of Bitcoin, Ethereum, and Tether')
        
        sunburst_data['labels'].append('Others')
        sunburst_data['parents'].append('Crypto Market')
        sunburst_data['values'].append(others_value)
        sunburst_data['hovertext'].append('Combined market cap of other cryptocurrencies')
        
        # Add bit, eth, and tether to Top 3 second level category
        for coin_id in categories['Top 3']:
            coin_data = next(coin for coin in market_data if coin['id'] == coin_id)
            sunburst_data['labels'].append(coin_data['name'])
            sunburst_data['parents'].append('Top 3')
            sunburst_data['values'].append(coin_data['market_cap'])
            sunburst_data['hovertext'].append(f"Market cap of {coin_data['name']}")
        
        # Add other coins to Others second level category
        for coin_id in categories['Others']:
            coin_data = next(coin for coin in market_data if coin['id'] == coin_id)
            sunburst_data['labels'].append(coin_data['name'])
            sunburst_data['parents'].append('Others')
            sunburst_data['values'].append(coin_data['market_cap'])
            sunburst_data['hovertext'].append(f"Market cap of {coin_data['name']}")
        
        logging.info("Sunburst data prepared successfully.")
        return sunburst_data
    else:
        logging.error(f"Error fetching market data: {response.status_code}")
        return None
