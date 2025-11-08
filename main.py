import modules.config as config
import modules.market as market
import modules.graphs as graphs
import random

random.seed(config.random_seed)

traders = market.gen_traders(config.constrained)
transaction_prices = market.market(traders, timeout=config.timeout, periods=config.periods, quiet=config.quiet)

# Checks which graphs to plot based off of config.graphs
if config.graphs == 1:
    costs, redemptions = graphs.values_from_traders(traders)
    graphs.plot_supply_demand(costs, redemptions, min_price=config.min_price, max_price=config.max_price)
if config.graphs == 2:
    costs, redemptions = graphs.values_from_traders(traders)
    equilibrium_price = graphs.find_equilibrium(costs, redemptions)[1]
    graphs.plot_transactions(transaction_prices, equilibrium_price=equilibrium_price, min_price=config.min_price, max_price=config.max_price)
if config.graphs == 3:
    costs, redemptions = graphs.values_from_traders(traders)
    graphs.plot_supply_demand_and_transactions(list_of_traders=traders, prices=transaction_prices, min_price=config.min_price, max_price=config.max_price)
if config.graphs == 4:
    random.seed(config.random_seed)

    traders = market.gen_traders(not config.constrained)
    costs, redemptions = graphs.values_from_traders(traders)
    graphs.big_graph(list_of_traders=traders, prices=transaction_prices, min_price=config.min_price, max_price=config.max_price)


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
