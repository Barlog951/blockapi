from blockapi.services import (
    BlockchainAPI
)

from datetime import datetime

class BinanceAPI(BlockchainAPI):
    """
    coins: binance coin
    API docs: https://docs.binance.org/api-reference/dex-api/paths.html
    Explorer: 
    """

    active = True

    currency_id = 'binance-coin'
    base_url = 'https://dex.binance.org/api/v1'
    rate_limit = 0
    coef = 1
    max_items_per_page = None
    page_offset_step = None
    confirmed_num = None

    supported_requests = {
        'get_balance': '/account/{address}',
        'get_txs': '/transactions?address={address}&offset={offset}&limit={limit}'
    }

    def get_balance(self):
        response = self.request('get_balance',
                                address=self.address)
        if not response:
            return 0

        try:
            return [{
                'symbol': bal['symbol'],
                'amount': float(bal['free']) * self.coef
            } for bal in response['balances']]
        except ValueError:
            return 0

    def get_txs(self, offset=None, limit=None, unconfirmed=False):
        response = self.request('get_txs',
                                address=self.address,
                                offset=offset,
                                limit=limit)

        return [ self.parse_tx(t) for t in response['tx'] ]

    def parse_tx(self,tx):
        from_address = tx['fromAddr']
        to_address = tx['toAddr']
        amount = tx['value']
        fee = tx['txFee']
        txhash = tx['txHash']
        timestamp = tx['timeStamp']

        if from_address == self.address:
            direction = 'outgoing'
        else:
            direction = 'incoming'

        return {
            'date': datetime.strptime(timestamp,'%Y-%m-%dT%H:%M:%S.%fZ'),
            'from_address': from_address,
            'to_address': to_address,
            'amount': amount * self.coef,
            'fee': fee * self.coef,
            'gas': {},
            'hash': txhash,
            'confirmed': None,
            'is_error': False,
            'type': 'normal',
            'kind': 'transaction',
            'direction': direction,
            'raw': tx
        }
