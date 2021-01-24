import time
import math
from optibook.synchronous_client import Exchange
import logging
logger = logging.getLogger('client')
logger.setLevel('ERROR')

print("Setup was successful.")

# Connect to Exchange
instrument_id_A = 'PHILIPS_A'
instrument_id_B = 'PHILIPS_B'

WAITING_TIME = 1
FIXED_VOLUME = 1
MAX_VALUE = 100000000
e = Exchange()
a = e.connect()

class order_level:
    def __init__(self, bidorask, price, vol):
        if bidorask == "bid":
            self.bid_volume = vol
            self.ask_volume = ""
        if bidorask == "ask":
            self.bid_volume = ""
            self.ask_volume = vol
            
        self.price_level = price
        
def bid_ask_ls(instrument_id):
    book = e.get_last_price_book(instrument_id)
    bidslist = []
    asklist = []
    bids_vol = 0
    asks_vol = 0
    
    for bid in book.bids:
            bids_vol += bid.volume
            bid_each = order_level("bid",round(bid.price,1),bid.volume)
            bidslist.append(bid_each)
            # print(bidslist)
    
    for ask in book.asks:
        asks_vol += ask.volume
        ask_each = order_level("ask",round(ask.price,1),ask.volume)
        asklist.append(ask_each)
        # print(askslist)

    return bidslist[0].price_level, asklist[0].price_level

    

    # try:
    #     for bid in book.bids:
    #         bids_vol += bid.volume
    #         bid_each = order_level("bid",round(bid.price,1),bid.volume)
    #         bidslist.append(bid_each)
    #         # print(bidslist)
    
    #     for ask in book.asks:
    #         asks_vol += ask.volume
    #         ask_each = order_level("ask",round(ask.price,1),ask.volume)
    #         asklist.append(ask_each)
    #         # print(askslist)
 
    #     return bidslist[-1].price_level, asklist[-1].price_level
    
    # except:
    #     return len(bidslist),len(asklist)
    
# function to find bid ask spread


## if bid ask spread bigger, more iliquid
def bid_ask_spread():
    try:
        bid_a, ask_a = bid_ask_ls(instrument_id_A)
        bid_b, ask_b = bid_ask_ls(instrument_id_B)
        # print(bid_a,ask_a)
        bid_ask_spread_a = abs(bid_a - ask_a)
        bid_ask_spread_b = abs(bid_b - ask_b)
        if bid_ask_spread_a > bid_ask_spread_b:
            return instrument_id_A
        else:
            return instrument_id_B
    except:
        return instrument_id_A
        

def trade():
    print("start trade")
    while True:
        # print("start while loop")
        illiquid_instrument = bid_ask_spread()
        
        if illiquid_instrument == instrument_id_A:
            # print("after line 97")
             # sell to A at best ask price
            bid_a, ask_a = bid_ask_ls(instrument_id_A)
            bid_b, ask_b = bid_ask_ls(instrument_id_B)
            
            # if ask_a >= bid_b:
            #     ask_result = e.insert_order(instrument_id_A,price=ask_a,volume=1,side='ask', order_type='limit')
            #     sell= True
            # else:
            #     time.sleep(WAITING_TIME)
            #     continue
            
            # # buy from B at best bid price
            # if sell== True:
            #     bid_result = e.insert_order(instrument_id_B,price=bid_b,volume=1,side='bid', order_type='limit')
                
                
            ask_result = e.insert_order(instrument_id_A,price=ask_a,volume=7,side='ask', order_type='limit')
            spending = 3*ask_a
            vol_in = math.ceil(spending/bid_b) - 1
            bid_result = e.insert_order(instrument_id_B,price=bid_b,volume=vol_in,side='bid', order_type='limit') 
           

        if illiquid_instrument == instrument_id_B:
             
             # sell to B at best ask price
            bid_a, ask_a = bid_ask_ls(instrument_id_A)
            bid_b, ask_b = bid_ask_ls(instrument_id_B)
            
            # if ask_b >= bid_a:
            #     ask_result = e.insert_order(instrument_id_B,price=ask_b,volume=3,side='ask', order_type='limit')
            #     sell= True
            # else:
            #     time.sleep(WAITING_TIME)
            #     continue
            
            
            # # buy from A at best bid price
            # if sell== True:
            #     bid_result = e.insert_order(instrument_id_A,price=bid_a,volume=,side='bid', order_type='limit')
                
                
            ask_result = e.insert_order(instrument_id_B,price=ask_b,volume=3,side='ask', order_type='limit')
            spending = 3*ask_b
            vol_in = math.ceil(spending/bid_a) - 1
            bid_result = e.insert_order(instrument_id_A,price=bid_a,volume=vol_in,side='bid', order_type='limit')    
                
           
            # print("before printing")
        time.sleep(WAITING_TIME)
        positions = e.get_positions()
        for p in positions:
            print(p, positions[p])
        e.delete_orders(instrument_id_A)
        e.delete_orders(instrument_id_B)
        print("----")

trade()