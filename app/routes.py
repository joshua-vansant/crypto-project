from flask import Blueprint, render_template, current_app
from app.database import Session, BitcoinPriceData, EthereumPriceData, TetherPriceData
import plotly.graph_objs as go
from app.data_processing import get_resampled_data, generate_volatility_graph, get_line_graph_data, get_sunburst_data
import pandas as pd


main = Blueprint('main', __name__)

@main.route('/')
def index():
    session = Session()
    df_resampled = get_resampled_data()

    # Fix the dates
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

    session.close()

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

@main.route('/sunburst-chart')
def sunburst_chart():
    try:
        sunburst_data = get_sunburst_data()
        if sunburst_data:
            fig = go.Figure(go.Sunburst(
                labels=sunburst_data['labels'],
                parents=sunburst_data['parents'],
                values=sunburst_data['values'],
                hovertext=sunburst_data.get('hovertext', [''] * len(sunburst_data['labels'])),
                hoverinfo='label+value+text'
            ))

            chart_html = fig.to_html(full_html=False)
            return render_template('sunburst_chart.html', chart_html=chart_html)
        else:
            return "No data available for the chart.", 404
    except Exception as e:
        current_app.logger.error(f"Error in sunburst_chart route: {e}")
        return "An internal server error occurred.", 500
