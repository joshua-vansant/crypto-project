import requests
from datetime import datetime
import app.database as database
import logging

logging.basicConfig(level=logging.INFO)

def fetch_crypto_data(crypto_id):
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
    session = database.Session()  # Create a session instance
    for timestamp, price in data['prices']:
        date = datetime.fromtimestamp(timestamp / 1000.0)
        record = model_class(date=date, price=price)
        session.add(record)
        logging.info(f'Adding record: Date={date}, Price={price}')
    session.commit()
    logging.info(f'Committed {len(data["prices"])} records to the database.')
    session.close()  # Close the session when done



if __name__ == '__main__':
    # Fetch and store Bitcoin data
    bitcoin_data = fetch_crypto_data('bitcoin')
    store_data(bitcoin_data, database.BitcoinPriceData)

    # Fetch and store Ethereum data
    ethereum_data = fetch_crypto_data('ethereum')
    store_data(ethereum_data, database.EthereumPriceData)

    # Fetch and store Tether data
    tether_data = fetch_crypto_data('tether')
    store_data(tether_data, database.TetherPriceData)