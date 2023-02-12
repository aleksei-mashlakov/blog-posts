import os
import time
from datetime import datetime
from typing import Callable, Dict, List, Optional

import pandas as pd
from tqdm.notebook import tqdm
from functools import partial


# adapted from https://learndataanalysis.org/source-code-download-historical-stock-data-from-yahoo-finance-using-python/
def download_tickers_historical_data(
    tickers: List[str],
    from_date: datetime = pd.to_datetime("2018-01-01"),
    to_date: datetime = pd.Timestamp.today(),
    interval: str = "1d",
    directory: str = "data",
    save: bool = False,
) -> Dict[str, pd.DataFrame]:
    """
    Returns a dict of dataframes with historical values
    """
    from_date = int(time.mktime(from_date.timetuple()))
    to_date = int(time.mktime(to_date.timetuple()))
    tickers_data = dict()
    for ticker in tqdm(tickers[:]):
        try:
            query_string = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={from_date}&period2={to_date}&interval={interval}&events=history&includeAdjustedClose=true"
            data = pd.read_csv(
                query_string, index_col=0, parse_dates=[0], infer_datetime_format=True
            )
            tickers_data[ticker] = data
            if save:
                data.reset_index().to_csv(
                    os.path.join(directory, f"{ticker}_{interval}.csv")
                )
        except Exception as e:
            print(f"Exception {e}")
            continue
    return tickers_data


def calculate_pct_returns(x: pd.Series, periods: int) -> pd.Series:
    return 1 + x.pct_change(periods=periods)


def apply_to_dataframe(
    df: pd.DataFrame, func: Callable[..., pd.DataFrame], axis: int = 0
):
    """Compute full-sample column-wise autocorrelation for a DataFrame."""
    return df.apply(lambda col: func(col), axis=axis, result_type="expand")


def reindex_weekdays(
    df: pd.DataFrame,
    drop_weekends: bool = True,
    start_index: pd.Timestamp = None,
    end_index: pd.Timestamp = None,
    fill_method: str = "ffill",
    extra_fill_method: Optional[str] = "bfill",
    freq: str = "D",
) -> pd.DataFrame:
    if start_index is None:
        start_index = df.index[0]
    if end_index is None:
        end_index = df.index[-1]

    df = df.reindex(pd.date_range(start=start_index, end=end_index, freq=freq))
    # df = df.fillna(method=fill_method).fillna(method=extra_fill_method)
    if drop_weekends:
        return df.loc[~df.index.day_name().isin(["Saturday", "Sunday"]), :]
    return df


def transform_to_target(
    tickers_data: Dict[str, pd.DataFrame], start_index: pd.Timestamp, periods: int
) -> pd.DataFrame:
    for k, df in tickers_data.items():
        tickers_data[k] = reindex_weekdays(df, start_index=start_index)
    df = pd.DataFrame.from_dict({k: v["Adj Close"] for k, v in tickers_data.items()})
    df_prc_returns = df.apply(calculate_pct_returns, periods=periods, axis=0)
    return df_prc_returns


def calculate_na_per_column(df: pd.DataFrame) -> pd.DataFrame:
    percent_of_non_na = ((df.shape[0] - df.isna().sum().T) / df.shape[0]) * 100
    return 100 - percent_of_non_na
