import grequests
import requests
import math


class Boll:
    def get_pair_price_history(self):
        api = 'https://api.binance.com/api/v3/klines?symbol={}&interval={}&limit={}'.format(
            self.symbol, self.interval, self.N)
        self.price_history = requests.get(api).json()
        return self.price_history

    def get_typical_price(self):
        # typical price = (high + low + close)/3
        self.price_history_tp = list(map(lambda data: (
            float(data[2]) + float(data[3]) + float(data[4]))/3, self.price_history))
        return self.price_history_tp

    def get_sma(self):
        self.sma = sum(self.price_history_tp)/self.N
        return self.sma

    def get_variance(self):
        self.variance = sum(
            map(lambda price: (price-self.sma)**2, self.price_history_tp))/(self.N-1)
        return self.variance

    def get_sd(self):
        self.sd = math.sqrt(self.variance)
        return self.sd

    def __init__(self, symbol='', price_history=None, N=20, M=2, interval='1h'):
        self.N = N
        self.M = M
        self.interval = interval
        self.symbol = symbol
        self.price_history = price_history
        self.calculate_boll()

    def calculate_boll(self):
        if self.price_history is None:
            self.get_pair_price_history()
        self.get_typical_price()
        self.get_sma()
        self.get_variance()
        self.get_sd()
        self.bolu = self.sma + self.M*self.sd
        self.bold = self.sma - self.M*self.sd
        self.current_price = float(self.price_history[-1][4])

    def get_status(self):
        if self.current_price < self.bold:
            return -1
        elif self.current_price > self.bolu:
            return 1
        else:
            return 0


class SymbolsWithBoll:
    def __init__(self, N=20, M=2, interval='1h'):
        self.N = N
        self.M = M
        self.interval = interval

    def get_all_symbols(self):
        api = 'https://api.binance.com/api/v3/exchangeInfo'
        self.symbols = list(filter(lambda pair: pair.endswith('USDT') or pair.endswith(
            'BTC'), map(lambda data: data['symbol'], requests.get(api).json()['symbols'])))
        return self.symbols

    def get_price_hitory_of_all_symbols(self):
        price_histories = (grequests.get('https://api.binance.com/api/v3/klines?symbol={}&interval={}&limit={}'.format(
            symbol, self.interval, self.N)) for symbol in self.get_all_symbols())
        self.price_histories = grequests.map(price_histories)
        return self.price_histories

    def get_status_of_symbols(self):
        self.symbols_with_movements = []
        self.get_price_hitory_of_all_symbols()

        for i, symbol in enumerate(self.symbols):
            price_history = self.price_histories[i].json()
            status = Boll(symbol, price_history).get_status()
            if status != 0:
                self.symbols_with_movements.append((symbol, status, price_history[-1][4]))

        return self.symbols_with_movements

    def generate_msg(self):
        flag = 0
        self.txt = ''
        for symbol, status, current_price in sorted(self.get_status_of_symbols(),key= lambda data: data[1] ):
            if flag != status:
                self.txt += 'Down ->\n' if status==-1 else ('' if status==0 else '\n\n')+'Up ->\n'
                flag = status
            self.txt += "{} {}\n".format(symbol, current_price)
        return self.txt


