import datetime as dt
from flask import Flask, render_template, request
import numpy_financial as npf
import yfinance as yf
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def Average(lst):
    return sum(lst) / len(lst) if len(lst) > 0 else 0.0


# ------------------------------
# Financial Data Fetching Functions
# ------------------------------

def get_eps_history(ticker):
    t = yf.Ticker(ticker)
    eps_list = []
    try:
        income_stmt = t.income_stmt
        if income_stmt is None or 'Diluted EPS' not in income_stmt.index:
            return []
        eps_series = income_stmt.loc['Diluted EPS']
        for date, eps in eps_series.items():
            if pd.notna(eps):
                eps_list.append({'year': str(date.year), 'eps': f"{eps:.2f}"})
        eps_list.sort(key=lambda x: int(x['year']), reverse=True)
    except Exception as e:
        print(f"EPS Error: {e}")
    return eps_list


def get_dividend_history(ticker):
    t = yf.Ticker(ticker)
    current_year = datetime.now().year
    try:
        dividends = t.dividends
        if dividends.empty:
            start_year = current_year - 9
            return [{'year': str(y), 'dividend': '0.00'} for y in range(current_year, start_year - 1, -1)]
        if dividends.index.tz is not None:
            dividends.index = dividends.index.tz_localize(None)
        dividends_by_year = dividends.groupby(dividends.index.year).sum()
        first_year = int(dividends_by_year.index.min())
        dividend_list = []
        for year in range(current_year, first_year - 1, -1):
            total = dividends_by_year.get(year, 0.0)
            dividend_list.append({'year': str(year), 'dividend': f"{total:.2f}"})
        return dividend_list
    except Exception as e:
        print(f"Dividend Error: {e}")
        start_year = current_year - 9
        return [{'year': str(y), 'dividend': '0.00'} for y in range(current_year, start_year - 1, -1)]


def get_net_income_history(ticker):
    t = yf.Ticker(ticker)
    current_year = datetime.now().year
    net_income_data = {}
    try:
        income_stmt = t.income_stmt
        if income_stmt is None or 'Net Income' not in income_stmt.index:
            return []
        ni_series = income_stmt.loc['Net Income']
        for date, val in ni_series.items():
            if pd.notna(val):
                net_income_data[date.year] = str(int(round(val, 0)))
    except Exception as e:
        print(f"Net Income Error: {e}")
    start_year = min(net_income_data.keys()) if net_income_data else current_year - 9
    return [
        {'year': str(y), 'net_income': net_income_data.get(y, '0.00')}
        for y in range(current_year, start_year - 1, -1)
    ]


def get_current_liabilities_history(ticker):
    t = yf.Ticker(ticker)
    current_year = datetime.now().year
    data = {}
    try:
        bs = t.balance_sheet
        if bs is None or 'Current Liabilities' not in bs.index:
            return []
        row = bs.loc['Current Liabilities']
        for date, val in row.items():
            if pd.notna(val):
                data[date.year] = str(int(round(val, 0)))
    except Exception as e:
        print(f"Current Liabilities Error: {e}")
    start_year = min(data.keys()) if data else current_year - 9
    return [
        {'year': str(y), 'current_liabilities': data.get(y, '0.00')}
        for y in range(current_year, start_year - 1, -1)
    ]


def get_cash_and_cash_equivalents_history(ticker):
    t = yf.Ticker(ticker)
    current_year = datetime.now().year
    data = {}
    try:
        bs = t.balance_sheet
        if bs is None or 'Cash Cash Equivalents And Short Term Investments' not in bs.index:
            return []
        row = bs.loc['Cash Cash Equivalents And Short Term Investments']
        for date, val in row.items():
            if pd.notna(val):
                data[date.year] = str(int(round(val, 0)))
    except Exception as e:
        print(f"Cash Error: {e}")
    start_year = min(data.keys()) if data else current_year - 9
    return [
        {'year': str(y), 'cash_and_cash_equivalents': data.get(y, '0.00')}
        for y in range(current_year, start_year - 1, -1)
    ]


def get_total_liabilities_history(ticker):
    t = yf.Ticker(ticker)
    current_year = datetime.now().year
    data = {}
    try:
        bs = t.balance_sheet
        if bs is None or 'Total Liabilities Net Minority Interest' not in bs.index:
            return []
        row = bs.loc['Total Liabilities Net Minority Interest']
        for date, val in row.items():
            if pd.notna(val):
                data[date.year] = str(int(round(val, 0)))
    except Exception as e:
        print(f"Total Liabilities Error: {e}")
    start_year = min(data.keys()) if data else current_year - 9
    return [
        {'year': str(y), 'total_liabilities': data.get(y, '0.00')}
        for y in range(current_year, start_year - 1, -1)
    ]


def get_total_assets_history(ticker):
    t = yf.Ticker(ticker)
    current_year = datetime.now().year
    data = {}
    try:
        bs = t.balance_sheet
        if bs is None or 'Total Assets' not in bs.index:
            return []
        row = bs.loc['Total Assets']
        for date, val in row.items():
            if pd.notna(val):
                data[date.year] = str(int(round(val, 0)))
    except Exception as e:
        print(f"Total Assets Error: {e}")
    start_year = min(data.keys()) if data else current_year - 9
    return [
        {'year': str(y), 'total_assets': data.get(y, '0.00')}
        for y in range(current_year, start_year - 1, -1)
    ]


def get_price_history(ticker, years_back=5):
    t = yf.Ticker(ticker)
    current_year = datetime.now().year
    price_list = []
    try:
        start_date = f"{current_year - years_back - 1}-01-01"
        end_date = f"{current_year + 1}-01-01"
        hist = t.history(start=start_date, end=end_date)
        if hist.empty:
            raise ValueError("No price data")
        for year in range(current_year - years_back + 1, current_year + 1):
            dec = hist[(hist.index.year == year) & (hist.index.month == 12)]
            price = dec['Close'].iloc[-1] if not dec.empty else 0.0
            price_list.append({'year': str(year), 'price': f"{price:.2f}"})
        price_list.sort(key=lambda x: int(x['year']), reverse=True)
    except Exception as e:
        print(f"Price Error: {e}")
        for y in range(current_year, current_year - years_back, -1):
            price_list.append({'year': str(y), 'price': '0.00'})
    return price_list


# ------------------------------
# Core Fundamentals Calculator
# ------------------------------

def fundamentals(symbol, nb_shares, RealDiscountRate, AverageInflation, price_5_years_ago):
    try:
        eps_data = get_eps_history(symbol)
        dividends_data = get_dividend_history(symbol)
        net_income_data = get_net_income_history(symbol)
        price_data = get_price_history(symbol, years_back=5)

        if len(eps_data) < 4 or len(dividends_data) < 4 or len(net_income_data) < 4 or len(price_data) < 1:
            raise ValueError("Insufficient data")

        # RORE 5 Years
        #total_eps_5 = sum(float(eps_data[i]['eps']) for i in range(5))
        #total_div_5 = sum(float(dividends_data[i]['dividend']) for i in range(5))
        #retained_5 = total_eps_5 - total_div_5
        #eps_now = float(eps_data[0]['eps'])
        #eps_5ago = float(eps_data[4]['eps'])
        #RORE_5years = ((eps_now - eps_5ago) / retained_5) * 100 if retained_5 != 0 else 0.0

        # RORE 3 Years
        if len(eps_data) >= 3 and len(dividends_data) >= 3:
            total_eps_3 = sum(float(eps_data[i]['eps']) for i in range(3))
            total_div_3 = sum(float(dividends_data[i]['dividend']) for i in range(3))
            retained_3 = total_eps_3 - total_div_3
            eps_lastyear = float(eps_data[0]['eps'])
            eps_4yago = float(eps_data[2]['eps'])
            RORE_3years = ((eps_lastyear - eps_4yago) / retained_3) * 100 if retained_3 != 0 else 0.0
        else:
            RORE_3years = 0.0

        # CAGR & Growth
        ni_1yago = float(net_income_data[1]['net_income'])
        ni_3yago = float(net_income_data[3]['net_income'])
        cagr5years = (((ni_1yago / ni_5yago) ** 0.2) - 1) * 100
        NetIncomeGrouth_5years = ((ni_1yago - ni_3yago) / ni_3yago) * 100
        NetIncomeGrouth_Average = Average([
            (float(net_income_data[i]['net_income']) - float(net_income_data[i+1]['net_income'])) / float(net_income_data[i+1]['net_income']) * 100
            for i in range(2)
        ])

        EPSGrouth_3years = ((float(eps_data[0]['eps']) - float(eps_data[2]['eps'])) / float(eps_data[2]['eps'])) * 100
        EPSGrouth_Average = Average([
            (float(eps_data[i]['eps']) - float(eps_data[i+1]['eps'])) / float(eps_data[i+1]['eps']) * 100
            for i in range(2)
        ])

        PaidDividends_5years = round(sum(float(dividends_data[i]['dividend']) for i in range(3)), 2)

        # Liquidity & Leverage
        current_liab = get_current_liabilities_history(symbol)
        cash_equiv = get_cash_and_cash_equivalents_history(symbol)
        total_liab = get_total_liabilities_history(symbol)
        total_ast = get_total_assets_history(symbol)

        latest_current_liab = float(current_liab[0]['current_liabilities']) if current_liab else 1
        latest_cash = float(cash_equiv[0]['cash_and_cash_equivalents']) if cash_equiv else 1
        current_liabilities_to_cash_factor = (latest_current_liab / latest_cash) * 100 if latest_cash != 0 else 0.0

        latest_total_liab = float(total_liab[0]['total_liabilities']) if total_liab else 1
        latest_total_ast = float(total_ast[0]['total_assets']) if total_ast else 1
        total_liabilities_to_assets_factor = (latest_total_liab / latest_total_ast) * 100 if latest_total_ast != 0 else 0.0

        # P/E Ratio
        latest_price = float(price_data[0]['price'])
        latest_eps = float(eps_data[0]['eps'])
        pe_ratio = latest_price / latest_eps if latest_eps != 0 else 0.0

        # Overpriced Calculation
        investment = nb_shares * price_5_years_ago
        RetainedErnings = []
        for i in range(5):
            if i < len(eps_data) and i < len(dividends_data):
                retained = nb_shares * (float(eps_data[i]['eps']) - float(dividends_data[i]['dividend']))
                RetainedErnings.append(retained)

        NominalDiscountRate = RealDiscountRate + AverageInflation
        NetPresentValue = npf.npv(NominalDiscountRate, RetainedErnings) if RetainedErnings else 0

        fv_npv = npf.fv(-AverageInflation, 5, 0, -NetPresentValue)
        fv_investment = npf.fv(-AverageInflation, 5, 0, -investment)
        TotalValueYears = fv_npv + fv_investment
        EstimatedPrice = TotalValueYears / nb_shares if nb_shares > 0 else 0
        overpriced_float = round(100 * (latest_price / EstimatedPrice - 1), 2) if EstimatedPrice != 0 else 0.0

        return (
            round(pe_ratio, 2), round(RORE_5years, 2), round(RORE_3years, 2),
            round(cagr5years, 2), round(NetIncomeGrouth_5years, 2), round(NetIncomeGrouth_Average, 2),
            round(EPSGrouth_5years, 2), round(EPSGrouth_Average, 2),
            round(current_liabilities_to_cash_factor, 2), round(total_liabilities_to_assets_factor, 2),
            PaidDividends_5years, round(overpriced_float, 2)
        )
    except Exception as e:
        print(f"Fundamentals error for {symbol}: {e}")
        return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


# ------------------------------
# Flask Routes
# ------------------------------

@app.route('/')
def student():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        nb_shares = int(request.form['Number_Shares'])
        RealDiscountRate = float(request.form['RealDiscountRate'])
        AverageInflation = float(request.form['AverageInflation'])

        # Table Header
        t = [['Stock', 'P/E', 'RORE 5y', 'RORE 3y', 'CAGR 5y', 'NI Growth 5y', 'NI Avg', 'EPS Growth 5y', 'EPS Avg',
              'Curr Liab/Cash %', 'Tot Liab/Assets %', 'Div 5y', 'Overpriced %']]

        now = dt.datetime.now()
        graphdata = [['Year']] + [[now.year - i] for i in range(6)]  # Initialize once

        for i in range(6):
            symbol_key = f'Stock_symbol{i+1}'
            price_key = f'price_5_years_ago{i+1}'
            if request.form.get(symbol_key):
                symbol = request.form[symbol_key].strip().upper()
                try:
                    price_5_years_ago = float(request.form[price_key])
                    r = fundamentals(symbol, nb_shares, RealDiscountRate, AverageInflation, price_5_years_ago)

                    stockname = symbol
                    table_data = [
                        stockname,
                        f"{r[0]:.2f}",
                        f"{r[1]:.2f}%",
                        f"{r[2]:.2f}%",
                        f"{r[3]:.2f}%",
                        f"{r[4]:.2f}%",
                        f"{r[5]:.2f}%",
                        f"{r[6]:.2f}%",
                        f"{r[7]:.2f}%",
                        f"{r[8]:.2f}%",
                        f"{r[9]:.2f}%",
                        r[10],
                        f"{r[11]:.2f}%"
                    ]
                    t.append(table_data)

                    if r[11] > 0:
                        graphdata[0].append(stockname)
                        for j in range(6):
                            graphdata[j+1].append(r[11])

                except Exception as e:
                    print(f"Error processing {symbol}: {e}")

        # Clean table
        t = [row for row in t if all(str(cell) != 'nan' and 'inf' not in str(cell) for cell in row)]
        columnNames = t[0]
        rows = t[1:]

        return render_template("result2.html", columnNames=columnNames, rows=rows, graphdata=graphdata)


if __name__ == '__main__':
    app.run(debug=True)
