import yfinance as yf
import csv
from yfinance import ticker

#open file with list of stock tickers
with open('stocks.csv') as stocks_csv:
    csv_reader = csv.DictReader(stocks_csv)
    
    #open file selected stocks will be written to
    with open("selected_stocks.csv", mode = "w") as selected_stocks_CSV:
        stocks_writer = csv.writer(selected_stocks_CSV, delimiter = ",")
        
        #write indices
        stocks_writer.writerow(['Ticker', 'RSI', 'Price', 'All Time High'])
        
        for row in csv_reader:

            stock = yf.Ticker(row["Ticker"])

            #get past month of data
            past_month = stock.history()

            #check that stock price is above $15
            try:
                if(past_month.iloc[-1, 3] < 15):
                    continue
                else:
                    price = past_month.iloc[-1, 3]
            except IndexError:
                continue

            #calculate RSI
            last_16 = past_month["Close"][-16:]
            gains = 0
            losses = 0.000001 #to avoid dividing by zero

            try:
                for x in range(14):
                    pct_change = (last_16[x+1]-last_16[x])/last_16[0]

                    if(pct_change >= 0):
                        gains += pct_change
                    else:
                        losses += abs(pct_change)

                rs = gains/losses
                rsi = 100 - 100/(1+rs)
            #filter out stocks with not enough data to calculate RSI
            except IndexError:
                continue

            #check that RSI is above 60
            if(rsi < 60):
                continue

            #check that stock is within 8% of high
            stock_monthly = stock.history(period="max", interval="1mo")

            #find max manually due to presence of NaN values
            high = 0.000001 #to avoid dividing by zero

            for value in stock_monthly["High"]:
                if (type(value) == float):
                    if(value > high):
                        high = value

            if((high-price)/high > .08):
                continue
            
            #sometimes the yfinance api is strange so the high stays at 0
            # or you have random NaN values (rare though)
            if(high == 0 or high != high or price != price):
                continue

            #write remaining stocks into file
            stocks_writer.writerow([row["Ticker"]])
