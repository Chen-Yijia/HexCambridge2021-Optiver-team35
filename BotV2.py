# more iliquid market indicated by wider bid ask spread

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

class order_level:
    def __init__(self, bidorask, price, vol):
        if bidorask == "bid":
            self.bid_volume = vol
            self.ask_volume = ""
        if bidorask == "ask":
            self.bid_volume = ""
            self.ask_volume = vol
            
        self.price_level = price


def weighted_mid(instrument_id):
    book = e.get_last_price_book(instrument_id)
    bidslist = []
    asklist = []
    bids_vol = 0
    asks_vol = 0

    
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
        
        print(weighted_mid)

        return round(weighted_mid,2), bidslist, asklist
    except:

        return MAX_VALUE, bidslist, asklist
        

# function to find bid ask spread

## if bid ask spread bigger, more iliquid
def bid_ask_spread():
    try:
        price_a,bidslist_a,asklist_a = weighted_mid(instrument_id_A)
        price_b,bidslist_b,asklist_b = weighted_mid(instrument_id_B)
        bid_ask_spread_a = abs(bidslist_a[0].price_level - asklist_a[0].price_level)
        bid_ask_spread_b = abs(bidslist_b[0].price_level - asklist_b[0].price_level)
        if bid_ask_spread_a > bid_ask_spread_b:
            return instrument_id_A
        else:
            return instrument_id_B
    except:
        return instrument_id_A
    
    
def stop_function():
    print("WE ARE MAKING LOSSES!")
    exit()


# hedge the exact same number in the more liquid market
## find how many transaction orders go through for iliquid
def hedge(transaction, illiquid_instrument, a, b):
    if transaction==0:
        pass
    
    else:
        if transaction < 0:
            action = 'bid'
            price_lel = 10000
        else:
            action = 'ask'
            price_lel = 1
            
        if illiquid_instrument == instrument_id_A:
            
            hedge_result = e.insert_order(instrument_id_B,price=price_lel,volume=abs(transaction), side=action, order_type='ioc')
        if illiquid_instrument == instrument_id_B:
            hedge_result = e.insert_order(instrument_id_A,price=price_lel, volume=abs(transaction), side=action, order_type='ioc')
            
        # if illiquid_instrument == instrument_id_A:
        #     if a == 'overvalued':
        #         for i in range(1,6):
        #             hedge_result = e.insert_order(instrument_id_B,price=1,volume=abs(transaction), side='bid', order_type='ioc')
    
        #     if a == 'undervalued':
        #         for i in range(1,6):
        #             hedge_result = e.insert_order(instrument_id_B,price=10000,volume=abs(transaction), side='ask', order_type='ioc')
                       
        
        # if illiquid_instrument == instrument_id_B:
        #     if b == 'overvalued':
        #         for i in range(1,6):
        #             hedge_result = e.insert_order(instrument_id_A,price=1, volume=abs(transaction), side='bid', order_type='ioc')
                   
        #     if b == 'undervalued':
        #         for i in range(1,6):
        #             hedge_result = e.insert_order(instrument_id_A,price=10000, volume=abs(transaction), side='ask', order_type='ioc')
                    
                        
    
    
def trade():
    print("start trading")
    current_pnl = e.get_pnl()
    pnl_trend = []
    pnl_trend.append(current_pnl)
    
    while True:
        
    
        price_a = MAX_VALUE
        price_b= MAX_VALUE
        ask_price = 0
        bid_price = 0
            
        
            
        while True:    
            while price_a == MAX_VALUE:
                price_a, bidslist_a, asklist_a = weighted_mid(instrument_id_A)
            while price_b == MAX_VALUE:
                price_b, bidslist_b, asklist_b = weighted_mid(instrument_id_B)
        
            illiquid_instrument = bid_ask_spread()
            print("illiquid: ", illiquid_instrument)
            
            inipos_dic= e.get_positions()
            init_pos = inipos_dic[illiquid_instrument]
            
                
            
            if price_a > price_b: 
                a = 'overvalued'
                b = 'undervalued'
                ask_price = price_a
                bid_price = price_b
            if price_b > price_a:
                a = 'undervalued'
                b = 'overvalued'
                ask_price = price_b
                bid_price = price_a
        
            
            if illiquid_instrument == instrument_id_A:
                if a == 'overvalued':
                    for i in range(1,6):
                        ask_result = e.insert_order(instrument_id_A,price=ask_price,volume=1*i,side='ask', order_type='limit')
                        ask_price+=0.01
                if a == 'undervalued':
                    for i in range(1,6):
                        bid_result = e.insert_order(instrument_id_A,price=bid_price,volume=1*i,side='bid', order_type='limit')
                        bid_price-=0.01
            
            if illiquid_instrument == instrument_id_B:
                if b == 'overvalued':
                    for i in range(1,6):
                        ask_result = e.insert_order(instrument_id_B,price=ask_price,volume=1*i,side='ask', order_type='limit')
                        ask_price+=0.01
                if b == 'undervalued':
                    for i in range(1,6):
                        bid_result = e.insert_order(instrument_id_B,price=bid_price,volume=1*i,side='bid', order_type='limit')
                        bid_price-=0.01
                        
                        
            time.sleep(WAITING_TIME)
            positions = e.get_positions()
            for p in positions:
                print(p, positions[p])
            e.delete_orders(illiquid_instrument)
            print("----")
                
            
            final_posdic= e.get_positions()
            final_pos= final_posdic[illiquid_instrument]
            transaction= final_pos-init_pos
            
            print("transaction",transaction)
            
            positions = e.get_positions()
            for p in positions:
                print(p, positions[p])
            #hedge(transaction,illiquid_instrument,a,b)
            
            
            # new_pnl = e.get_pnl()
            # print("----")
            # print(new_pnl)
            # if len(pnl_trend) < 4:
            #     pnl_trend.append(new_pnl)
            # elif len(pnl_trend) == 4 and min(pnl_trend) == new_pnl:
            #     stop_function()
            # else: 
            #     pnl_trend.pop(0)
            #     pnl_trend.append(new_pnl)
            
            
    
trade() 