import yfinance as yf
def get_stock_data(ticker, start_date, end_date):
    """
    Fetch historical stock data for a given ticker symbol between specified dates.

    Parameters:
    ticker (str): The stock ticker symbol.
    start_date (str): The start date in 'YYYY-MM-DD' format.
    end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
    pandas.DataFrame: A DataFrame containing the stock data.
    """
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data
print("Yfinance module loaded successfully.")
print("Function get_stock_data is ready to use.")
# Example usage:
data = get_stock_data('AAPL', '2022-01-01', '2024-12-31')
print(data)
