import yfinance as yf

def get_historical_eps(symbol):
    """
    Get historical EPS using income statement data.
    Returns: [{'year': '2024', 'eps': '6.41'}, ...]
    """
    ticker = yf.Ticker(symbol)
    
    # Get annual income statement (trailing twelve months, yearly)
    income_stmt = ticker.income_stmt
    if income_stmt is None or income_stmt.empty:
        print("No income statement data available.")
        return []

    # Get annual basic shares outstanding (from 'Basic Average Shares')
    shares = ticker.get_shares_full(start="2010-01-01", end=None)
    if shares is None:
        print("No shares data available.")
        return []

    # Resample shares to year-end values (annual)
    try:
        shares_annual = shares.resample('Y').last()  # Last reported shares per year
    except:
        # Fallback: take the last N values if resample fails
        shares_annual = shares.iloc[-len(income_stmt.columns):]

    # Align years
    eps_list = []
    for col_idx, date in enumerate(income_stmt.columns):
        year = date.year

        # Get Net Income (before minority interest, etc.)
        net_income = income_stmt.loc['Net Income'].iloc[col_idx]

        # Match year with shares
        try:
            share_count = shares_annual.get(year)
            if share_count is None:
                # Try fallback: use previous year or skip
                continue
        except:
            continue

        if net_income and share_count:
            eps = net_income / share_count
            eps_list.append({
                'year': str(year),
                'eps': f"{eps:.2f}"  # Format as string with 2 decimals
            })

    # Sort from newest to oldest (like your example)
    eps_list.sort(key=lambda x: x['year'], reverse=True)
    return eps_list

# 🔍 Test
if __name__ == "__main__":
    symbol = "AAPL"
    eps_data = get_historical_eps(symbol)
    
    if eps_data:
        for item in eps_data:
            print(item)
    else:
        print("No EPS data retrieved. Check symbol or internet.")
