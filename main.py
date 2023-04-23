from fastapi import FastAPI, HTTPException,Query
from typing import List ,Optional
# list for db

from datetime import datetime

from pydantic import BaseModel, Field, validator
# to use basemodel "Basemodel" is imported 

from typing import Optional
# to use optional for optional str

# class models
class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")
    price: float = Field(description="The price of the Trade.")
    quantity: int = Field(description="The amount of units traded.")

class Trade(BaseModel):
    asset_class: Optional[str] = Field( description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")
    counterparty: Optional[str] = Field(description="The counterparty the trade was executed with. May not always be available")
    instrument_id: str = Field( description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")
    instrument_name: str = Field( description="The name of the instrument traded.")
    trade_date_time: datetime = Field( description="The date-time the Trade was executed")

    trade_details: TradeDetails = Field( description="The details of the trade, i.e. price, quantity")

    trade_id: int = Field(description="The unique ID of the trade")
    trader: str = Field(description="The name of the Trader")


class TradesList(BaseModel):
    trades: List[Trade]
    total_count: int

def apply_pagination(data: List[Trade], page: int, page_size: int) -> TradesList:
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paged_data = data[start_index:end_index]
    return TradesList(trades=paged_data, total_count=len(data))

def apply_sorting(data: List[Trade], sort_by: str, sort_order: Optional[str] = 'asc') -> List[Trade]:
    reverse = sort_order == 'desc'
    sorted_data = sorted(data, key=lambda x: getattr(x, sort_by), reverse=reverse)
    return sorted_data

# main application
app = FastAPI(title="SteelEye API Developer Assessment",
    description="Endpoints for retrieving a list of Trades, retrieving a single Trade by ID, searching against Trades, and filtering Trades",
    contact={
        "name": "Rahul Rakesh",
        "email": "rahulrakesh0842@gmail.com",
    },)

# end point for List of trades 
@app.get("/trades")
async def list_of_trades_with_paging_and_sorting(
    page: Optional[int] = Query(1, gt=0),
    page_size: Optional[int] = Query(10, gt=0, le=100),
    sort_by: Optional[str] = Query('trade_id', description='field to sort by', regex=r'^[a-zA-Z_]+$'),
    sort_order: Optional[str] = Query('asc', description='sort order (asc or desc)', regex=r'^(asc|desc)$')
):
    sorted_data = apply_sorting(db, sort_by=sort_by, sort_order=sort_order)
    paged_data = apply_pagination(sorted_data, page=page, page_size=page_size)
    return paged_data



# end point for single trade by id 
@app.get("/trades/trade_id/{id}")
async def Single_Trade_By_Id(trade_id: int):
    for trade in db:
        if trade.trade_id == trade_id:
            return trade
    return {"error": "Trade not found"}

# end points for searching trades 
@app.get("/trades/counter_party/{search}")
async def counter_party(search: Optional[str] = None):
    if search:
        search_text = search.lower()
        filtered_trades = [trade for trade in db if (
            search_text in trade.counterparty.lower()
            )]
        return filtered_trades
    else:
        return db
    
@app.get("/trades/instrument_ID/{search}")
async def instrument_ID(search: Optional[str] = None):
    if search:
        search_text = search.lower()
        filtered_trades = [trade for trade in db if (
            search_text in trade.instrument_id.lower() 
            )]
        return filtered_trades
    else:
        return db

@app.get("/trades/instrument_Name/{search}")
async def instrument_Name(search: Optional[str] = None):
    if search:
        search_text = search.lower()
        filtered_trades = [trade for trade in db if (
            search_text in trade.instrument_name.lower() 
             )]
        return filtered_trades
    else:
        return db
    
@app.get("/trades/trader/{search}")
async def trader(search: Optional[str] = None):
    if search:
        search_text = search.lower()
        filtered_trades = [trade for trade in db if (
            search_text in trade.trader.lower()
            )]
        return filtered_trades
    else:
        return db


# End points for Advanced filtering
@app.get("/trades/advance_filtering")
async def Filtering_Trades(
    assetClass: Optional[str] = None,
    end: Optional[datetime] = None,
    maxPrice: Optional[float] = None,
    minPrice: Optional[float] = None,
    start: Optional[datetime] = None,
    tradeType: Optional[str] = None
):
    filtered_trades = db

    # Filter by assetClass
    if assetClass:
        filtered_trades = [trade for trade in filtered_trades if trade.asset_class == assetClass]

    # Filter by tradeDateTime range
    if start:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_date_time >= start]
    if end:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_date_time <= end]

    # Filter by tradeDetails.price range
    if minPrice:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_details.price >= minPrice]
    if maxPrice:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_details.price <= maxPrice]

    # Filter by tradeDetails.buySellIndicator
    if tradeType:
        filtered_trades = [trade for trade in filtered_trades if trade.trade_details.buy_sell_indicator == tradeType]

    return filtered_trades



# Mock database

db:List[Trade]=[
    
Trade(asset_class="Equity", counterparty="XYZ Bank", instrument_id="AAPL", instrument_name="Apple Inc.", 
      trade_date_time=datetime(2022, 4, 1, 12, 30), trade_details=TradeDetails(buySellIndicator="BUY", price=150.0, quantity=100),
        trade_id=1, trader="John Smith"), 
                
Trade(asset_class="FX", counterparty="ABC Bank", instrument_id="EURUSD", instrument_name="Euro/US Dollar", 
      trade_date_time=datetime(2022, 3, 31, 9, 45), trade_details=TradeDetails(buySellIndicator="SELL", price=1.1750, quantity=5000), 
      trade_id=2, trader="Jane Doe"),

Trade(asset_class="Bond", counterparty="DEF Bank", instrument_id="US00123ABC45", instrument_name="US Treasury 10-year Bond",
       trade_date_time=datetime(2022, 4, 2, 14, 15), trade_details=TradeDetails(buySellIndicator="BUY", price=98.5, quantity=1000), 
       trade_id=3, trader="Bob Johnson"),

Trade(asset_class="Equity", counterparty="XYZ Bank", instrument_id="AAPL", instrument_name="Apple Inc.", 
      trade_date_time=datetime(2022, 4, 1, 12, 30), trade_details=TradeDetails(buySellIndicator="BUY", price=150.0, quantity=100),
        trade_id=4, trader="John Smith"), 

Trade(asset_class="FX", counterparty="ABC Bank", instrument_id="EURUSD", instrument_name="Euro/US Dollar", 
      trade_date_time=datetime(2022, 3, 31, 9, 45), trade_details=TradeDetails(buySellIndicator="SELL", price=1.1750, quantity=5000),
        trade_id=5, trader="Jane Doe"),

Trade(asset_class="Bond", counterparty="DEF Bank", instrument_id="US00123ABC45", instrument_name="US Treasury 10-year Bond",
       trade_date_time=datetime(2022, 4, 2, 14, 15), trade_details=TradeDetails(buySellIndicator="BUY", price=98.5, quantity=1000), 
       trade_id=6, trader="Bob Johnson"),
    
Trade(asset_class="FX", counterparty="ABC Bank", instrument_id="GBPUSD", instrument_name="British Pound/US Dollar",
       trade_date_time=datetime(2022, 4, 5, 10, 30), trade_details=TradeDetails(buySellIndicator="BUY", price=1.3800, quantity=3000), 
       trade_id=7, trader="John Smith"),
    
Trade(asset_class="Equity", counterparty="XYZ Bank", instrument_id="GOOGL", instrument_name="Alphabet Inc.",
       trade_date_time=datetime(2022, 4, 6, 16, 45), trade_details=TradeDetails(buySellIndicator="SELL", price=2300.0, quantity=50), 
       trade_id=8, trader="Jane Doe"),

Trade(asset_class="Bond", counterparty="DEF Bank", instrument_id="US00459GQT52", instrument_name="US Treasury 5-year Bond", 
      trade_date_time=datetime(2022, 4, 7, 13, 15), trade_details=TradeDetails(buySellIndicator="SELL", price=98.25, quantity=500),
        trade_id=9, trader="Bob Johnson"),

Trade(asset_class="Equity", counterparty="XYZ Bank", instrument_id="MSFT", instrument_name="Microsoft Corporation", 
      trade_date_time=datetime(2022, 4, 8, 14, 0), trade_details=TradeDetails(buySellIndicator="BUY", price=260.0, quantity=75),
        trade_id=10, trader="John Smith"),

Trade(asset_class="FX", counterparty="ABC Bank", instrument_id="AUDUSD", instrument_name="Australian Dollar/US Dollar", 
      trade_date_time=datetime(2022, 4, 9, 11, 30), trade_details=TradeDetails(buySellIndicator="SELL", price=0.7500, quantity=10000), 
      trade_id=11, trader="Jane Doe"),
    
Trade(asset_class="Bond", counterparty="DEF Bank", instrument_id="US912828M645", instrument_name="US Treasury 30-year Bond", 
      trade_date_time=datetime(2022, 4, 12, 9, 0), trade_details=TradeDetails(buySellIndicator="BUY", price=100.0, quantity=500), 
      trade_id=12, trader="Bob Johnson"),

Trade(asset_class="FX", counterparty="XYZ Bank", instrument_id="GBPUSD", instrument_name="British Pound/US Dollar", 
      trade_date_time=datetime(2022, 4, 3, 14, 30), trade_details=TradeDetails(buySellIndicator="BUY", price=1.3900, quantity=10000),
        trade_id=13, trader="John Smith"),

Trade(asset_class="Equity", counterparty="DEF Bank", instrument_id="MSFT", instrument_name="Microsoft Corporation", 
      trade_date_time=datetime(2022, 4, 4, 10, 15), trade_details=TradeDetails(buySellIndicator="SELL", price=300.0, quantity=200), 
      trade_id=14, trader="Jane Doe"),

Trade(asset_class="FX", counterparty="ABC Bank", instrument_id="USDJPY", instrument_name="US Dollar/Japanese Yen", 
      trade_date_time=datetime(2022, 4, 5, 9, 0), trade_details=TradeDetails(buySellIndicator="SELL", price=110.50, quantity=10000), 
      trade_id=15, trader="Bob Johnson") 

]
