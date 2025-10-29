import modules.config as config
import modules.market as market
import modules.graphs as graphs
import random

# If config.random_seed is None, then it just won't do anything
random.seed(config.random_seed)

# Makes the traders
traders = []
# Bidders
for _ in range(config.num_traders//2):

    # If no redemptions are given, we can just make them up
    if config.redemption_values == None:
        redemption_values = [random.randint(config.min_price, config.max_price) for _ in range(config.num_commodities)]
    else:
        redemption_values = config.redemption_values
    
    t = market.Trader(
        name=f"b{_}",
        bidder=True,
        redemptions_or_costs=redemption_values,
        constrained=config.constrained)
    traders.append(t)
# Sellers
for _ in range(config.num_traders//2):
    # If no costs are given, we can just make them up
    if config.costs == None:
        costs = [random.randint(config.min_price, config.max_price) for _ in range(config.num_commodities)]
    else:
        costs = config.costs

    t = market.Trader(
        name=f"s{_}",
        bidder=False,
        redemptions_or_costs=costs,
        constrained=config.constrained)

    traders.append(t)

transaction_prices = market.market(traders, timeout=config.timeout, periods=config.periods, quiet=config.quiet)
graphs.plot_supply_demand_and_transactions(list_of_traders=traders, prices=transaction_prices, min_price=config.min_price, max_price=config.max_price)

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
