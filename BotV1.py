import time
from optibook.synchronous_client import Exchange
import logging
logger = logging.getLogger('client')
logger.setLevel('ERROR')

print("Setup was successful.")

# Connect to Exchange
instrument_id_A = 'PHILIPS_A'
instrument_id_B = 'PHILIPS_B'


# How many iterations you want the bot to do
POLLING_DURATION = 30
# How long you want the bot to wait for in each iteration
WAITING_TIME = 1
FIXED_VOLUME = 1
MAX_VALUE = 100000000
e = Exchange()
a = e.connect()



# Class to track the public bid & ask sell price
class order_level:
    def __init__(self, bidorask, price, vol):
        if bidorask == "bid":
            self.bid_volume = vol
            self.ask_volume = ""
        if bidorask == "ask":
            self.bid_volume = ""
            self.ask_volume = vol
            
        self.price_level = price

# def bidlist(instrument_id):
#     book = e.get_last_price_book(instrument_id)
#     bidslist = []
#     bids_vol = 0
    
#     for bid in book.bids:
#         bids_vol += bid.volume
#         bid_each = order_level("bid",round(bid.price,1),bid.volume)
#         bidslist.append(bid_each)
#     return , bids_vol

# def asklist(instrument_id):
#     book = e.get_last_price_book(instrument_id)
#     asklist = []
#     asks_vol = 0
#     for ask in book.asks:
#         asks_vol += ask.volume
#         ask_each = order_level("ask",round(ask.price,1),ask.volume)
#         asklist.append(ask_each)
        
    
#     return , asks_vol
        
#def asklist():
    


# Function to calculate the weighted_mid price: used for ask
def weighted_mid(instrument_id):
    book = e.get_last_price_book(instrument_id)
    bidslist = []
    asklist = []
    bids_vol = 0
    asks_vol = 0

    # bidlist,bids_vol = bidlist(instrument_id)
    # asklist, asks_vol = asklist(instrument_id)
    try:
        for bid in book.bids:
            bids_vol += bid.volume
            bid_each = order_level("bid",round(bid.price,1),bid.volume)
            bidslist.append(bid_each)
    
        for ask in book.asks:
            asks_vol += ask.volume
            ask_each = order_level("ask",round(ask.price,1),ask.volume)
            asklist.append(ask_each)
            
        bid_weight = bids_vol/(bids_vol+asks_vol)
        ask_weight = asks_vol/(bids_vol+asks_vol)
        # weighted_mid = (bidslist[0].price_level)*bid_weight+(asklist[0].price_level)*ask_weight
        weighted_mid = (bidslist[0].price_level)*bid_weight+(asklist[0].price_level)*ask_weight
        return round(weighted_mid,1)
    except:
        return MAX_VALUE



# within each iteration:
def trade():
    print("start trading")
    current_pnl = e.get_pnl()
    pnl_trend = []
    pnl_trend.append(current_pnl)
    while True:
        # Get the lowest ask price (Weighted mid?)
        t=0
        price_a = MAX_VALUE
        price_b= MAX_VALUE
        ask_price = 0
        bid_price = 0
        while True:
            while price_a == MAX_VALUE:
                price_a = weighted_mid(instrument_id_A)
            while price_b == MAX_VALUE:
                price_b = weighted_mid(instrument_id_B)
              
            # Compare philips A and B, which one is higher, we will ask the higher one
            if price_a > price_b: 
                ask_id = instrument_id_A
                bid_id = instrument_id_B
                ask_price = price_a
                bid_price = price_b
            else: 
                ask_id = instrument_id_B
                bid_id = instrument_id_A
                ask_price = price_b
                bid_price = price_a
            
            for i in range(1,6):
                ask_result = e.insert_order(ask_id,price=ask_price,volume=1*i,side='ask', order_type='limit')
                ask_price+=0.01
                print("sellorder_" + str(i))
                
            for j in range(1,6):
                bid_result = e.insert_order(bid_id,price=bid_price,volume=1*j,side='bid', order_type='limit')
                bid_price-=0.01
                print("buyorder_" + str(j))
                
            time.sleep(WAITING_TIME)
            t+=WAITING_TIME
            e.delete_orders(bid_id)
            e.delete_orders(ask_id)
            
            # new_pnl = e.get_pnl()
            print("----")
            # print(new_pnl)
            # if len(pnl_trend) < 4:
            #     pnl_trend.append(new_pnl)
            # elif len(pnl_trend) == 4 and min(pnl_trend) == new_pnl:
            #     stop_function()
            # else: 
            #     pnl_trend.pop(0)
            #     pnl_trend.append(new_pnl)
                
          

        
        

# check if function is making extended losses over time 
    def stop_function():
        print("WE ARE MAKING LOSSES!")
        exit()


trade()
