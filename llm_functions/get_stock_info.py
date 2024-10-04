import yfinance as yf

definition = {
    "name": "get_stock_info",
    "description": "Retrieves the current stock price info for a given stock ticker",
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "The ticker symbol of the stock"
            },
            "period": {
                "type": "string",
                "description": "The period for which to retrieve the stock data (e.g., '1d', '5d', '1mo', etc.)"
            }
        },
        "required": ["symbol", "period"]
    }
}

def get_stock_info(symbol, period):
    """
    Retrieves the stock price info for the given ticker symbol and period.

    Parameters:
        symbol (str): The ticker symbol of the stock.
        period (str): The period for which to retrieve the stock data.

    Returns:
        list: A list of dictionaries containing the stock price info for each day in the period.
    """
    stock = yf.Ticker(symbol)
    data = stock.history(period=period)
    if not data.empty:
        stock_info_list = []
        for index, row in data.iterrows():
            stock_info = {
                'Date': index.strftime('%Y-%m-%d'),
                'Open': round(float(row['Open']), 2),
                'High': round(float(row['High']), 2),
                'Low': round(float(row['Low']), 2),
                'Close': round(float(row['Close']), 2),
                'Volume': round(float(row['Volume']), 2)
            }
            stock_info_list.append(stock_info)
        return stock_info_list
    else:
        return None