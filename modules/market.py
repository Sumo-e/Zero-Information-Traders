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

    # Initializing these values
    bid = config.min_price - 1 # All bids will be higher than this
    ask = config.max_price + 1 # All asks will be lower than this
    price = 0
    transaction_prices = []

    for p in range(periods):
        # I hate mutability
        # Need to do this in order to not keep using the original traders over and over again
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
    


# Avoiding the use of copy
import random
import time
import modules.config as config
from typing import Optional


class Trader:
    def __init__(self, name: str = "", bidder: bool = True,
                 redemptions_or_costs: list[int] | tuple[int, ...] | None = None,
                 constrained: bool = True):
        self.name = name
        self.constrained = constrained
        self.is_bidder = bidder

        # Create a new list every time to avoid sharing mutable defaults
        # If no list/tuple is passed → start empty
        # If a list/tuple is passed → make a shallow copy for isolation
        roc = [] if redemptions_or_costs is None else list(redemptions_or_costs)

        # Sort depending on the trader type:
        # bidders (buyers) → descending redemption values
        # sellers → ascending costs
        if self.is_bidder:
            roc.sort(reverse=True)
        else:
            roc.sort()

        # Convert to tuple to make the sequence immutable.
        # This prevents accidental modifications and eliminates the need for deepcopy.
        self.redemptions_or_costs = tuple(roc)

        self.profits: list[int] = []

        # Guard against empty schedules to avoid IndexError in gen_offer
        if len(self.redemptions_or_costs) == 0:
            self.offer = None  # type: Optional[int]
        else:
            self.offer = self.gen_offer()
    
    def gen_offer(self) -> int:
        # Safe if schedule exhausted: caller must check before calling
        idx = len(self.profits)
        current_value = self.redemptions_or_costs[idx]
        # Constrained buyers → cannot bid above their redemption value
        # Constrained sellers → cannot ask below their cost
        # Unconstrained → can choose any price within market range
        if self.constrained and self.is_bidder:
            self.offer = random.randrange(config.min_price, current_value + 1)
        elif self.constrained and not self.is_bidder:
            self.offer = random.randrange(current_value, config.max_price + 1)
        else:
            self.offer = random.randrange(config.min_price, config.max_price + 1)
        return self.offer

    def transact(self, price: int) -> list[int]:
        idx = len(self.profits)
        # Compute profit for this transaction and append it
        current_value = self.redemptions_or_costs[idx]
        if self.is_bidder:
            self.profits.append(current_value - price)
        else:
            self.profits.append(price - current_value)
        return self.profits

    def fresh_instance(self) -> "Trader":
        # Create a new Trader with the same structural parameters (immutable tuple)
        # but reset all mutable state (profits, offers)
        t = Trader(
            name=self.name,
            bidder=self.is_bidder,
            redemptions_or_costs=self.redemptions_or_costs,
            constrained=self.constrained,
        )
        return t
        
# Remove parameter; read from config ---
def gen_traders() -> list[Trader]:
    traders: list[Trader] = []
    constrained = config.constrained

    for i in range(config.num_traders // 2):

        # Only generate random redemption values if not provided in config
        # Prevents overwriting explicit data from config.toml
        if config.redemption_values is None:
            redemption_values = [
                random.randint(config.min_price, config.max_price)
                for _ in range(config.num_commodities)
            ]
        else:
            redemption_values = list(config.redemption_values)  # Defensive copy to avoid shared mutable state

        # Convert to tuple → immutable structural data, no accidental mutation
        t = Trader(
            name=f"b{i}",                          # Consistent buyer naming convention (b0, b1, ...)
            bidder=True,
            redemptions_or_costs=tuple(redemption_values),
            constrained=constrained,              # Propagate constrained flag explicitly
        )
        traders.append(t)

    for i in range(config.num_traders // 2):

        # Only generate random costs if not provided in config
        if config.costs is None:
            costs = [
                random.randint(config.min_price, config.max_price)
                for _ in range(config.num_commodities)
            ]
        else:
            costs = list(config.costs)  # Defensive copy to prevent aliasing with config data

        # Convert to tuple (immutable)
        t = Trader(
            name=f"s{i}",                          # Consistent seller naming convention (s0, s1, ...)
            bidder=False,
            redemptions_or_costs=tuple(costs),
            constrained=constrained,              # Pass constraint flag to every trader
        )
        traders.append(t)

    # Return a complete, independent trader population (half buyers, half sellers)
    return traders
    
def market(traders: Optional[list[Trader]] = None,
           timeout: Optional[int] = None,
           periods: Optional[int] = None,
           quiet: Optional[bool] = None) -> list[list[int]]:

    if traders is None:
        traders = gen_traders()
    if timeout is None:
        timeout = config.timeout
    if periods is None:
        periods = config.periods
    if quiet is None:
        quiet = config.quiet
    # Avoid mutable default; enforce non-empty input
    if not traders:
        raise ValueError("traders must be a non-empty list of Trader instances")

    transaction_prices: list[list[int]] = []

    for p in range(periods):
        # Replace deepcopy with per-period fresh instances -> immutable structural data + reset mutable state
        list_of_traders = [t.fresh_instance() for t in traders]

        if not quiet:
            print(f"Transaction ledger {p+1}:")
            print("Bid\tBidder\tAsk\tSeller\tPrice\tBidder profit\tSeller profit")

        period_prices: list[int] = []

        # Initialize bid/ask inside each period (not once before all periods)
        bid = config.min_price - 1
        ask = config.max_price + 1
        price = 0
        last_bidder: Optional[Trader] = None
        last_seller: Optional[Trader] = None

        start = time.monotonic()  # monotonic clock avoids wall-clock jumps
        deadline = start + timeout

        while time.monotonic() < deadline:
            # filter out exhausted traders before selection
            list_of_traders = [t for t in list_of_traders if len(t.profits) < len(t.redemptions_or_costs)]
            
            if not list_of_traders:
                break    # No active traders remain
            
            # Fast availability check
            if (not any(t.is_bidder for t in list_of_traders)    # No active buyers
                    or not any((not t.is_bidder) for t in list_of_traders)):  # No active sellers
                break  
                
            trader = random.choice(list_of_traders)

            offer = trader.gen_offer()

            if trader.is_bidder:
                if offer > bid:
                    bid = offer
                    price = ask
                    last_bidder = trader
            else:
                if offer < ask:
                    ask = offer
                    price = bid
                    last_seller = trader

            if bid >= ask and last_bidder is not None and last_seller is not None:
                last_bidder.transact(price)
                last_seller.transact(price)
                period_prices.append(price)

                if not quiet:
                    print(f"{bid:3}\t"
                          f"{last_bidder.name[:7]:^7}\t"
                          f"{ask:3}\t"
                          f"{last_seller.name[:7]:^7}\t"
                          f"{price:4}\t"
                          f"{last_bidder.profits[-1]:7}\t\t"
                          f"{last_seller.profits[-1]:7}")

                # Reset quotes after each trade within the period
                bid = config.min_price - 1
                ask = config.max_price + 1
                price = 0
                last_bidder = None
                last_seller = None

        if not quiet:
            if time.monotonic() >= deadline:
                print(TimeoutError(f"Timed out at {timeout} seconds."))
            else:
                print("Buyers/Sellers exhausted their supports")

        transaction_prices.append(period_prices)

    return transaction_prices
