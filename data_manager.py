import pandas as pd
import yfinance as yf
import asyncio


class DataManager:
    def __init__(self):
        self._selected_tickers = []
        self._ticker_raw_data = {}
        self._ticker_data_dict = {}

    def calculate_or_fetch_index(self, period):
        missing_tickers = self._check_for_missing_data()
        self._fetch_tickers_raw_data(missing_tickers)
        return self._process_and_combine_data(period)

    def set_tickers(self, tickers):
        self._selected_tickers = tickers

    def _check_for_missing_data(self):
        ticker_missing_data = []
        for ticker in self._selected_tickers:
            if ticker not in self._ticker_raw_data:
                ticker_missing_data.append(ticker)

        return ticker_missing_data

    def _fetch_tickers_raw_data(self, tickers):
        if tickers:
            tickers_data = self._fetch_tickers_data(tickers)
            for ticker in tickers:
                self._ticker_raw_data[ticker] = tickers_data[ticker]

    def _process_and_combine_data(self, period: int):
        for ticker in self._selected_tickers:
            ticker_period_format = ticker + "_" + str(period)
            if ticker_period_format not in self._ticker_data_dict:
                raw_data = self._ticker_raw_data[ticker].copy()
                monthly_data = self._cut_months(period, raw_data)
                ticker_data = self._create_wealth_index(monthly_data)
                self._ticker_data_dict[ticker_period_format] = ticker_data

        wealth_index = pd.concat(
            [self._ticker_data_dict[ticker + "_" + str(period)] for ticker in self._selected_tickers],
            axis=1)
        wealth_index.columns = self._selected_tickers

        return wealth_index

    @staticmethod
    def _fetch_tickers_data(tickers):
        raw_data = asyncio.run(asyncio.to_thread(
            yf.download, tickers, period="max", interval="1mo"
        ))
        if raw_data.empty:
            raise ValueError("Empty! -- placeholder")
        raw_data.index = raw_data.index.to_period("M")
        return raw_data["Close"]

    @staticmethod
    def _create_wealth_index(raw_data):
        ticker_data = raw_data
        ticker_data["wealth_index"] = ticker_data.pct_change()
        ticker_wealth_index = (1 + ticker_data["wealth_index"]).cumprod()
        ticker_wealth_index = ticker_wealth_index.dropna()

        first_row = pd.Series(index=(ticker_wealth_index.index.shift(-1)[0],), data=(1,))
        ticker_wealth_index = pd.concat((first_row, ticker_wealth_index), axis=0)
        return ticker_wealth_index

    @staticmethod
    def _ticker_analysis(wealth_index):
        ticker = wealth_index.columns[0]
        wealth_index["peaks"] = wealth_index[ticker].cummax()
        wealth_index["downturn"] = wealth_index[ticker] / wealth_index["peaks"] - 1
        return wealth_index

    @staticmethod
    def _cut_months(months_to_cut: int | None, data: pd.DataFrame):
        cut_data = data.loc[data.index >= data.index.max() - months_to_cut] if months_to_cut else data
        return cut_data


if __name__ == "__main__":
    pass
