import random
import matplotlib.pyplot as plt
import graphs
import time
import copy

###############################  Config  ###############################
with open("config.txt", 'r') as f:
    config = f.readlines()
    config = [line.strip() for line in config]
    # Create a dictionary where key is a variable and value is last
    # words (i.e. value of respective variable) from that line
    f_dict = {line.split()[0]: line.split()[-1] for line in config}

max_price = int(f_dict['max_price'])
min_price = int(f_dict['min_price'])
num_traders = int(f_dict['num_traders'])
num_commodities = int(f_dict['num_commodities'])
constrained = bool(f_dict['constrained'])
print(f_dict)

if num_traders % 2 != 0:
    raise ValueError("The number of traders must be even (should be the same number of buyers as bidders). Change 'num_traders'")
###########################  End of Config  ############################

class Trader:
    def __init__(self, name: str = '', bidder: bool = True, redemptions_or_costs: list[int] = [], constrained: bool = True):
        self.name = name
        self.constrained = constrained
        self.is_bidder = bidder

        # If it's a bidder, then redemption values are decreasing for each additional unit
        if self.is_bidder:
            self.redemptions_or_costs = sorted(redemptions_or_costs, reverse=True)
        # If it's a seller, then costs are increasing for each additional unit
        else:
            self.redemptions_or_costs = sorted(redemptions_or_costs)

        self.profits: list[int] = []
        self.offer = self.gen_offer()


    # `len(self.profits)` is a good proxy for # of commodities bought/sold
    def gen_offer(self):
        # The redemption value/cost associated with the commodity traded
        current_value = self.redemptions_or_costs[ len(self.profits) ]

        if self.constrained and self.is_bidder:
            self.offer = random.randrange(min_price, current_value + 1)
        elif self.constrained and not self.is_bidder:
            self.offer = random.randrange(current_value, max_price + 1)
        else:
            self.offer = random.randrange(min_price, max_price + 1)
        return self.offer

    def transact(self, price):
        # The redemption value/cost associated with the commodity traded
        current_value = self.redemptions_or_costs[ len(self.profits) ]

        if self.is_bidder:
            self.profits.append(current_value - price)
        else:
            self.profits.append(price - current_value)
        return self.profits

def market(traders: list[Trader] = [], timeout: int = 30, periods: int = 1, quiet: bool = True) -> list:
    if traders == []:
        raise ValueError("Empty list")

    # Initializing these values
    bid = min_price - 1 # All bids will be higher than this
    ask = max_price + 1 # All asks will be lower than this
    price = 0
    transaction_prices = []

    for p in range(periods):
        # I hate mutability
        # Need to do this in order to not keep using the original traders
        list_of_traders = copy.deepcopy(traders)

        if quiet != True:
            print(f"Transaction ledger {p+1}:")
            print("Bid\tBidder\tAsk\tSeller\tPrice\tBidder profit\tSeller profit")

        # Keep track of prices in each period
        period_prices = []

        start = time.time()

        # Checking if there's at least one bidder and at least one seller
        bidders =  [i.is_bidder for i in list_of_traders]
        while (True in bidders and False in bidders) and (time.time() < start + timeout):

            # Random draw
            trader = random.choice(list_of_traders)

            # Check if trader has exhausted their support
            if len(trader.profits) == len(trader.redemptions_or_costs):
                # Removes the specific trader from the pool
                list_of_traders.remove(trader)
                if quiet != True:
                    print(f"~~~{trader.name} was removed with {trader.profits=}")
                # There is one less bidder (or seller) in the pool
                bidders.pop(trader.is_bidder)
                continue

            # Generate a new offer
            trader.gen_offer()

            # Is the new offer better than the already-recorded one?
            # If so, replace them
            if trader.is_bidder:
                if trader.offer > bid:
                    bid = trader.offer
                    price = ask
                    last_bidder = trader
            else:
                if trader.offer < ask:
                    ask = trader.offer
                    price = bid
                    last_seller = trader

            # Check if offers cross
            if bid >= ask:
                last_bidder.transact(price)
                last_seller.transact(price)
                period_prices.append(price)

                if quiet != True:
                    print(f"{bid:3}\t"
                        f"{last_bidder.name[:7]:^7}\t"
                        f"{ask:3}\t"
                        f"{last_seller.name[:7]:^7}\t"
                        f"{price:4}\t"
                        f"{last_bidder.profits[-1]:7}\t\t"
                        f"{last_seller.profits[-1]:7}"
                    )

                # Re-initializing the values
                bid = min_price - 1
                ask = max_price + 1
                price = 0
            
        # Check why the auction finished
        if quiet != True:
            if time.time() > start + timeout:
                print(TimeoutError(f"Timed out at {timeout} seconds."))
            else:
                print("Buyers/Sellers exhausted their supports")

        # This is so if all the bidders and sellers are exhausted prices still get recorded
        transaction_prices.append(period_prices)
        print(f"Period {p + 1} {transaction_prices=}")
    return transaction_prices

# Makes the traders
traders = []
# Bidders
for _ in range(num_traders//2):
    redemptions = [random.randint(min_price, max_price) for _ in range(num_commodities)]
    t = Trader(
        name=f"b{_}",
        bidder=True,
        redemptions_or_costs=redemptions,
        constrained=constrained)
    traders.append(t)
# Sellers
for _ in range(num_traders//2):
    costs = [random.randint(min_price, max_price) for _ in range(num_commodities)]
    t = Trader(
        name=f"s{_}",
        bidder=False,
        redemptions_or_costs=costs,
        constrained=constrained)
    traders.append(t)

transaction_prices = market(traders, timeout=1, periods=6, quiet=False)
graphs.plot_supply_demand_and_transactions(list_of_traders=traders, prices=transaction_prices, min_price=min_price, max_price=max_price)

##################################  Example  ##################################
#b1 = Trader(name = 'b1', bidder = True, redemptions_or_costs = [110, 100, 90])
#b2 = Trader(name = 'b2', bidder = True, redemptions_or_costs = [115, 105, 95])
#s1 = Trader(name = 's1', bidder = False, redemptions_or_costs = [80, 85, 90])
#s2 = Trader(name = 's2', bidder = False, redemptions_or_costs = [75, 80, 85])
#
#b1 = Trader(name = 'b1', bidder = True, redemptions_or_costs = [_ for _ in range(110, 110-10, -1)])
#b2 = Trader(name = 'b2', bidder = True, redemptions_or_costs = [_ for _ in range(115, 115-10, -1)])
#s1 = Trader(name = 's1', bidder = False, redemptions_or_costs = [_ for _ in range(80, 80+10)])
#s2 = Trader(name = 's2', bidder = False, redemptions_or_costs = [_ for _ in range(75, 75+10)])
#
#traders = [b1, b2, s1, s2] 
#
#b1 = Trader(name='b1', bidder=True, redemptions_or_costs=[100, 50, 50, 25])
#s1 = Trader(name='s1', bidder=False, redemptions_or_costs=[23, 49, 51, 75])
#
#traders = [b1, s1]
#
#transaction_prices = market(traders, timeout=1, periods=3, quiet = False)
#print(f"{transaction_prices=}")
#
## Graphs
#graphs.plot_transactions(transaction_prices)
#plt.show()
#graphs.plot_supply_demand_and_transactions(list_of_traders=traders, prices=transaction_prices, min_price=min_price, max_price=max_price)
