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
    # Clear existing data
    session.query(model_class).delete()
    for timestamp, price in data['prices']:
        date = datetime.fromtimestamp(timestamp / 1000.0)
        record = model_class(date=date, price=price)
        session.add(record)
        # logging.info(f'Adding record: Date={date}, Price={price}')
    session.commit()
    logging.info(f'Committed {len(data["prices"])} records to the database.')
    session.close()

def fetch_sunburst_data():
    base_url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 10,
        'page': 1,
        'sparkline': False
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f'Error fetching sunburst data: {response.status_code}')
        return None

def store_sunburst_data(data):
    session = database.Session()
    # Clear existing sunburst data
    session.query(database.SunburstData).delete()
    # Define top-level and second-level categories for sunburst data
    sunburst_entries = []

    # Create the top-level categories
    sunburst_entries.append({
        'label': 'Crypto Market',
        'parent': '',
        'value': sum(coin['market_cap'] for coin in data),
        'hovertext': 'Total market capitalization of top 10 cryptocurrencies'
    })

    # Add top 3 and other categories
    categories = {
        'Top 3': ['bitcoin', 'ethereum', 'tether'],
        'Others': [coin['id'] for coin in data if coin['id'] not in ['bitcoin', 'ethereum', 'tether']]
    }

    top_3_value = sum(coin['market_cap'] for coin in data if coin['id'] in categories['Top 3'])
    others_value = sum(coin['market_cap'] for coin in data if coin['id'] not in categories['Top 3'])

    sunburst_entries.append({
        'label': 'Top 3',
        'parent': 'Crypto Market',
        'value': top_3_value,
        'hovertext': 'Combined market cap of Bitcoin, Ethereum, and Tether'
    })
    
    sunburst_entries.append({
        'label': 'Others',
        'parent': 'Crypto Market',
        'value': others_value,
        'hovertext': 'Combined market cap of other cryptocurrencies'
    })

    # Add individual coins
    for coin in data:
        if coin['id'] in categories['Top 3'] or coin['id'] in categories['Others']:
            sunburst_entries.append({
                'label': coin['name'],
                'parent': 'Top 3' if coin['id'] in categories['Top 3'] else 'Others',
                'value': coin['market_cap'],
                'hovertext': f"Market cap of {coin['name']}"
            })

    # Store entries in the database
    for entry in sunburst_entries:
        record = database.SunburstData(
            label=entry['label'],
            parent=entry['parent'],
            value=entry['value'],
            hovertext=entry['hovertext']
        )
        session.add(record)

    session.commit()
    logging.info(f'Committed {len(sunburst_entries)} sunburst records to the database.')
    session.close()

if __name__ == '__main__':
    bitcoin_data = fetch_crypto_data('bitcoin')
    store_data(bitcoin_data, database.BitcoinPriceData)

    ethereum_data = fetch_crypto_data('ethereum')
    store_data(ethereum_data, database.EthereumPriceData)

    tether_data = fetch_crypto_data('tether')
    store_data(tether_data, database.TetherPriceData)
    
    sunburst_data = fetch_sunburst_data()
    if sunburst_data:
        store_sunburst_data(sunburst_data)
