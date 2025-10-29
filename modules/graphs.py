import matplotlib.pyplot as plt

def values_from_traders(list_of_traders) -> tuple:
    # Separating bidders and sellers into two different lists
    bidders = [_ for _ in list_of_traders if _.is_bidder]
    sellers = [_ for _ in list_of_traders if not _.is_bidder]

    # Throw all the costs in a list and sort them
    costs = [
        cost
        for traders in sellers
        for cost in traders.redemptions_or_costs
    ]

    # Throw all the redemption values in a list and sort them
    redemptions = [
        redemption
        for traders in bidders
        for redemption in traders.redemptions_or_costs
    ]

    return (costs, redemptions)

def find_equilibrium(costs, redemptions) -> tuple:
    if type(costs) != list:
        raise ValueError("Costs must be a list")
    if type(redemptions) != list:
        raise ValueError("Redemptions must be a list")

    costs = sorted(costs)
    redemptions = sorted(redemptions, reverse=True)

    for i in range(len(redemptions)):
        # When the values overlap normally
        if redemptions[i] == costs[i]:
            eq_p = redemptions[i]
            eq_q = i
            return (eq_q, eq_p)
            
        # Of the lowest rungs, price becomes the highest (highest price limits)
        if redemptions[i] < costs[i]:
            eq_p = max(redemptions[i], costs[i-1])
            eq_q = i
            return (eq_q, eq_p)

    # If an equilibrium can't be found, this should hide that
    return (-1, -1)

def plot_supply_demand(costs, redemptions, min_price=None, max_price=None, ax=None):
    # Is this being graphed on its own?
    single_graph = True if ax == None else False

    # Gets the current axis, useful in order to plot this graph on its own or
    # next to another graph
    ax = ax or plt.gca()

    equilibrium_quantity, equilibrium_price = find_equilibrium(costs, redemptions)

    # Funny stuff to graph things correctly
    costs.sort()
    costs.insert(0, costs[0])
    redemptions.sort(reverse=True)
    redemptions.insert(0, redemptions[0])

    # List of index of costs list, should also be able to use the redemptions
    # list
    enum = [_ for _ in range(len(costs))]

    # Making the graph a little fancier
    ax.set_title("Supply and Demand Schedules")
    ax.step(enum, costs, color = 'blue')
    ax.step(enum, redemptions, color = 'red')
    ax.set_xlim(0, len(enum)-1)
    if min_price == None:
        min_price = min(costs.append + redemptions)
    if max_price == None:
        max_price = max(costs + redemptions)
    ax.set_ylim(min_price, max_price)

    # Dashed equilibrium lines
    ax.hlines(y=equilibrium_price,
            xmin=0,
            xmax=equilibrium_quantity,
            color='black',
            linestyles="dashed")
    ax.vlines(x=equilibrium_quantity,
            ymin=min_price,
            ymax=equilibrium_price,
            color='black',
            linestyles='dashed')

    # Prevents plotting too early when doing the side-by-side plot
    if single_graph == True:
        plt.show()

def plot_transactions(transaction_history, equilibrium_price: None|int = None, min_price = None, max_price = None, ax = None):
    # Is this being graphed on its own?
    single_graph = True if ax == None else False

    # Gets the current axis, useful in to plot this graph on its own or
    # next to another graph
    ax = ax or plt.gca()

    # If a list of lists is given, we know that we're graphing more than 1 period
    if type(transaction_history[0]) == list:
        enum = enumerate(transaction_history)
        # Flatten the list of lists of transactions
        transaction_history = [
            price
            for period in transaction_history
            for price in period
        ]
        # Find the length of the periods (0.5 makes line go between end/beginning of two periods)
        period_lengths = [len(periods) + 0.5 for _, periods in enum]

        for i in range(1, len(period_lengths)):
            period_lengths[i] += period_lengths[i-1]
    
    # Making the graph a little prettier
    ax.set_title("Transaction Prices")
    ax.set_xlim(1, len(transaction_history))
    if min_price == None:
        min_price = min(transaction_history) - 1
    if max_price == None:
        max_price = max(transaction_history) + 1
    ax.set_ylim(min_price, max_price)
    # x range goes from 1 to len(transaction_history)+1
    ax.plot(range(1, len(transaction_history)+1), transaction_history, zorder=3)

    if type(period_lengths) != None:
        ax.vlines(period_lengths[:-1],
                   ymin=min_price,
                   ymax=max_price,
                   color='black',
                   linestyles='dashed')

    # If the equilibrium price is given, then graph it
    if type(equilibrium_price) != None:
        ax.hlines(y=equilibrium_price,  # Ignore dumb error # type: ignore
                xmin=1,
                xmax=len(transaction_history)+1,
                color='black')
    
    if single_graph == True:
        plt.show()

def plot_supply_demand_and_transactions(list_of_traders, prices, min_price = None, max_price = None, axs = None):
    # Is this being graphed on its own?
    single_graph = True if axs == None else False

    if single_graph:
        fig = plt.figure(constrained_layout=True)
        (ax1, ax2) = fig.subplots(nrows=1, ncols=2)
    else:
        ax1, ax2 = axs # Ignore dumb error, ax should be passed as a tuple # type: ignore


    plt.title(f"ZI traders {'with' if list_of_traders[0].constrained else 'without'} Budget Constraint")

    costs, redemptions = values_from_traders(list_of_traders)
    plot_supply_demand(costs, redemptions, min_price=min_price, max_price=max_price, ax=ax1)
    equilibrium_price = find_equilibrium(costs, redemptions)[1]
    plot_transactions(prices, equilibrium_price=equilibrium_price, min_price=min_price, max_price=max_price, ax=ax2)

    if single_graph == True:
        plt.show()

def big_graph(list_of_traders, prices, min_price = None, max_price = None):
    import random
    import modules.market as market
    import modules.config as config

    fig = plt.figure(constrained_layout=True)
    (top, bottom) = fig.subfigures(nrows=2, ncols=1)
    top.suptitle("ZI Traders without Budget Constraint")
    bottom.suptitle("ZI Traders with Budget Constraint")

    # This logic always puts the unconstrained on top
    if list_of_traders[0].constrained:
        ax1, ax2 = top.subplots(nrows=1, ncols=2)
        ax3, ax4 = bottom.subplots(nrows=1, ncols=2)
    else:
        ax3, ax4 = top.subplots(nrows=1, ncols=2)
        ax1, ax2 = bottom.subplots(nrows=1, ncols=2)

    # Normal traders
    plot_supply_demand_and_transactions(list_of_traders, prices, min_price, max_price, axs=(ax1, ax2))

    # Opposite traders
    random.seed(config.random_seed)
    traders = market.gen_traders(not config.constrained)
    transaction_prices = market.market(traders, timeout=config.timeout, periods=config.periods, quiet=config.quiet)

    plot_supply_demand_and_transactions(traders, transaction_prices, min_price, max_price, axs=(ax3, ax4))

    plt.show()





# Examples
#from zit import Trader
#b1 = Trader(name = 'b1', bidder = True, redemptions_or_costs = [110, 100, 90])
#b2 = Trader(name = 'b2', bidder = True, redemptions_or_costs = [115, 105, 95])
#s1 = Trader(name = 's1', bidder = False, redemptions_or_costs = [80, 85, 90])
#s2 = Trader(name = 's2', bidder = False, redemptions_or_costs = [75, 80, 85])
#
#traders = [b1, b2, s1, s2]
#prices = [83, 102, 38, 92]
#
#plot_supply_demand(traders, min_price=0, max_price=200)
#costs, redemptions = values_from_traders(traders)
#equilibrium_price = find_equilibrium(costs, redemptions)[1]
#plot_transactions(prices, equilibrium_price=equilibrium_price)
#
#plot_supply_demand_and_transactions(traders, prices, min_price=0, max_price=200)