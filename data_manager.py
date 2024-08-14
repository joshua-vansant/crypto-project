import requests
from datetime import datetime
import app.database as database
import logging

logging.basicConfig(level=logging.INFO)

def fetch_crypto_data(crypto_id):
    # CoinGecko API, no API key needed
    base_url = 'https://api.coingecko.com/api/v3'
    endpoint = f'/coins/{crypto_id}/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': '30',
        'localization': 'false',
    }
    response = requests.get(base_url + endpoint, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f'Error reading from API: {response.status_code}')
        return None

def store_data(data, model_class):
    session = database.Session()
    for timestamp, price in data['prices']:
        date = datetime.fromtimestamp(timestamp / 1000.0)
        record = model_class(date=date, price=price)
        session.add(record)
        # logging.info(f'Adding record: Date={date}, Price={price}')
    session.commit()
    logging.info(f'Committed {len(data["prices"])} records to the database.')
    session.close()

# def fetch_market_data():
#     # Fetches market data for a list of cryptocurrencies
#     base_url = 'https://api.coingecko.com/api/v3/coins/markets'
#     params = {
#         'vs_currency': 'usd',
#         'order': 'market_cap_desc',
#         'per_page': 10,  # Fetch top 10 cryptos by market cap
#         'page': 1,
#         'sparkline': False
#     }
#     response = requests.get(base_url, params=params)
    
#     if response.status_code == 200:
#         data = response.json()
#         return data
#     else:
#         print(f'Error reading from API: {response.status_code}')
#         return None


if __name__ == '__main__':
    bitcoin_data = fetch_crypto_data('bitcoin')
    store_data(bitcoin_data, database.BitcoinPriceData)

    ethereum_data = fetch_crypto_data('ethereum')
    store_data(ethereum_data, database.EthereumPriceData)

    tether_data = fetch_crypto_data('tether')
    store_data(tether_data, database.TetherPriceData)

    # # Fetch market data for Sunburst chart
    # market_data = fetch_market_data()
    # if market_data:
    #     # Example of processing the data for a Sunburst chart
    #     sunburst_data = {
    #         'labels': ['Crypto Market'],
    #         'parents': [''],
    #         'values': [sum(coin['market_cap'] for coin in market_data)]
    #     }
    #     categories = {
    #         'Top 3': ['bitcoin', 'ethereum', 'tether'],
    #         'Others': [coin['id'] for coin in market_data if coin['id'] not in ['bitcoin', 'ethereum', 'tether']]
    #     }
    #     for category, coins in categories.items():
    #         sunburst_data['labels'].append(category)
    #         sunburst_data['parents'].append('Crypto Market')
    #         sunburst_data['values'].append(sum(coin['market_cap'] for coin in market_data if coin['id'] in coins))

    #         for coin_id in coins:
    #             coin_data = next(coin for coin in market_data if coin['id'] == coin_id)
    #             sunburst_data['labels'].append(coin_data['name'])
    #             sunburst_data['parents'].append(category)
    #             sunburst_data['values'].append(coin_data['market_cap'])

    #     # Now `sunburst_data` can be passed to a Plotly Sunburst chart
    #     print(sunburst_data)  # For debugging or further processing