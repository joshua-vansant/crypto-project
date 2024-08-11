from flask import Blueprint, render_template
from app.database import Session, BitcoinPriceData, EthereumPriceData, TetherPriceData
import plotly.graph_objs as go
import app.database as database
from app.data_processing import get_resampled_data, generate_volatility_graph, get_line_graph_data
import pandas as pd

main = Blueprint('main', __name__)

@main.route('/')
def index():
    session = Session()
    df_resampled = get_resampled_data()

    # Ensure date is not an index and is a datetime
    df_resampled.reset_index(inplace=True)
    df_resampled['date'] = pd.to_datetime(df_resampled['date']).dt.strftime('%Y-%m-%d') 

    plot_data = {
        'x': df_resampled['date'].tolist(),
        'crypto': df_resampled['crypto'].tolist(),
        'open': df_resampled['open'].tolist(),
        'high': df_resampled['high'].tolist(),
        'low': df_resampled['low'].tolist(),
        'close': df_resampled['close'].tolist()
    }

    volatility_graph = generate_volatility_graph()

    session.close()  # Close the session

    return render_template('index.html', volatility_graph=volatility_graph, plot_data=plot_data)

@main.route('/candlestick')
def candlestick():
    df_resampled = get_resampled_data()
    plot_data = {
        'x': df_resampled['date'].tolist(),
        'crypto': df_resampled['crypto'].tolist(),
        'open': df_resampled['open'].tolist(),
        'high': df_resampled['high'].tolist(),
        'low': df_resampled['low'].tolist(),
        'close': df_resampled['close'].tolist()
    }
    return render_template('candlestick.html', plot_data=plot_data)

@main.route('/line_graph')
def line_graph():
    # Get data using the function from data_processing.py
    bitcoin_dates, bitcoin_prices, ethereum_dates, ethereum_prices, tether_dates, tether_prices = get_line_graph_data()

    # Create Bitcoin price plot
    bitcoin_trace = go.Scatter(x=bitcoin_dates, y=bitcoin_prices, mode='lines', name='Bitcoin')
    bitcoin_layout = go.Layout(title='Bitcoin Prices', xaxis=dict(title='Date'), yaxis=dict(title='Price (USD)'))
    bitcoin_fig = go.Figure(data=[bitcoin_trace], layout=bitcoin_layout)
    bitcoin_graph = bitcoin_fig.to_html(full_html=False)

    # Create Ethereum price plot
    ethereum_trace = go.Scatter(x=ethereum_dates, y=ethereum_prices, mode='lines', name='Ethereum')
    ethereum_layout = go.Layout(title='Ethereum Prices', xaxis=dict(title='Date'), yaxis=dict(title='Price (USD)'))
    ethereum_fig = go.Figure(data=[ethereum_trace], layout=ethereum_layout)
    ethereum_graph = ethereum_fig.to_html(full_html=False)

    return render_template('line_graph.html', bitcoin_graph=bitcoin_graph, ethereum_graph=ethereum_graph)

@main.route('/volatility')
def volatility():
    volatility_graph = generate_volatility_graph()
    return render_template('volatility.html', volatility_graph=volatility_graph)
