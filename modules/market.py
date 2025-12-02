import random
import time
import copy
import modules.config as config

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
            self.offer = random.randrange(config.min_price, current_value + 1)
        elif self.constrained and not self.is_bidder:
            self.offer = random.randrange(current_value, config.max_price + 1)
        else:
            self.offer = random.randrange(config.min_price, config.max_price + 1)
        return self.offer

    def transact(self, price):
        # The redemption value/cost associated with the commodity traded
        current_value = self.redemptions_or_costs[ len(self.profits) ]

        if self.is_bidder:
            self.profits.append(current_value - price)
        else:
            self.profits.append(price - current_value)
        return self.profits

# All the other parameters get handled by the config file
# Need for displaying 4 graphs
def gen_traders(constrained: bool) -> list[Trader]:
    # Makes the traders
    traders = []
    # Bidders
    for _ in range(config.num_traders//2):
        # If no redemptions are given, we can just make them up
        if config.redemption_values == None:
            redemption_values = [random.randint(config.min_price, config.max_price) for _ in range(config.num_commodities)]
        else:
            redemption_values = config.redemption_values
        
        t = Trader(
            name=f"b{_}",
            bidder=True,
            redemptions_or_costs=redemption_values,
            constrained=constrained)
        traders.append(t)

    # Sellers
    for _ in range(config.num_traders//2):
        # If no costs are given, we can just make them up
        if config.costs == None:
            costs = [random.randint(config.min_price, config.max_price) for _ in range(config.num_commodities)]
        else:
            costs = config.costs

        t = Trader(
            name=f"s{_}",
            bidder=False,
            redemptions_or_costs=costs,
            constrained=constrained)

        traders.append(t)

    return traders


def market(traders: list[Trader] = [], timeout: int = 30, periods: int = 1, quiet: bool = True) -> list:
    if traders == []:
        raise ValueError("Empty list")

    # This is eventually the output of this function
    transaction_prices = []

    for p in range(periods):
        # I hate mutability
        # Need to do this in order to not keep using the original traders over and over again
        list_of_traders = copy.deepcopy(traders)

        if quiet != True:
            print(f"Transaction ledger {p+1}:")
            print("Bid\tBidder\tAsk\tSeller\tPrice\tBidder profit\tSeller profit")

        # Initializing these values
        bid = config.min_price - 1 # All bids will be higher than this
        ask = config.max_price + 1 # All asks will be lower than this
        price = 0
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
                bid = config.min_price - 1
                ask = config.max_price + 1
                price = 0
            
        # Check why the auction finished
        if quiet != True:
            if time.time() > start + timeout:
                print(TimeoutError(f"Timed out at {timeout} seconds."))
            else:
                print("Buyers/Sellers exhausted their supports")

        # This is so if all the bidders and sellers are exhausted prices still get recorded
        transaction_prices.append(period_prices)
    return transaction_prices
