import random

with open("config.txt", 'r') as f:
    config = f.readlines()
    config = [line.strip() for line in config]
    # Create a dictionary where key is a variable and value is last words 
    # (i.e. value of respective variable) from that line
    f_dict = {line.split()[0]: int(line.split()[-1]) for line in config}
    print(f_dict)

max_price = f_dict['max_price']
min_price = f_dict['min_price']

class Trader:
    def __init__(self, name: str = '', bidder: bool = True, redemptions_or_costs: list[int] = [], constrained: bool = True):
        self.name = name
        self.constrained = constrained
        self.is_bidder = bidder
        self.redemptions_or_costs = redemptions_or_costs
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

def market(list_of_traders: list[Trader] = []):
    if list_of_traders == []:
        print("Empty list")
        return

    # Initializing these values
    bid = min_price - 1 # All bids will be higher than this
    ask = max_price + 1 # All asks will be lower than this
    price = 0

    # Checking if there's at least one bidder and at least one seller
    bidders =  [i.is_bidder for i in list_of_traders]

    while True in bidders and False in bidders:
        # Random draw
        trader = random.choice(list_of_traders)

        # Check if trader has exhausted their support
        if len(trader.profits) == len(trader.redemptions_or_costs):
            # Removes the specific trader from the pool
            list_of_traders.remove(trader)
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
            print(f"{bid:3}\t"
                  f"{last_bidder.name[:7]:^7}\t"
                  f"{ask:3}\t"
                  f"{last_seller.name[:7]:^7}\t"
                  f"{price:4}\t"
                  f"{last_bidder.profits[-1]:7}\t\t"
                  f"{last_seller.profits[-1]:7}"
            )

            # Re-initializing the values
            bid = 0
            ask = 201
            price = 0


b1 = Trader(name = 'b1', bidder = True, redemptions_or_costs = [110, 100, 90])
b2 = Trader(name = 'b2', bidder = True, redemptions_or_costs = [115, 105, 95])
s1 = Trader(name = 's1', bidder = False, redemptions_or_costs = [80, 85, 90])
s2 = Trader(name = 's2', bidder = False, redemptions_or_costs = [75, 80, 85])

print("Transaction ledger:")
print("Bid\tBidder\tAsk\tSeller\tPrice\tBidder profit\tSeller profit")


market([b1, b2, s1, s2])
