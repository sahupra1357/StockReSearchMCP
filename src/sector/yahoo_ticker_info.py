import yfinance as yf

def get_yahhoo_sector_info(ticker_symbol: str):
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    return info

if __name__ == "__main__":
    ticker_info = get_yahhoo_sector_info("AAPL")
    #info = ticker.info

    #Pritn it in json format with indentation
    import json
    print(json.dumps(ticker_info, indent=2))
    print(ticker_info["sector"])
    print(ticker_info["industry"])
    #print(info)