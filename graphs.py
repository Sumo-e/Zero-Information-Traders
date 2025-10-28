import matplotlib.pyplot as plt
# Following is used for typehinting, not necessary
# Find out a way to not have circular dependency
# from zit import Trader

def values_from_traders(list_of_traders) -> tuple:
    # Separating bidders and sellers into two different lists
    bidders = [_ for _ in list_of_traders if _.is_bidder]
    sellers = [_ for _ in list_of_traders if not _.is_bidder]

    # Throw all the costs in a list and sort them, then prepend a 0 for 
    # graphing
    costs = [
        cost
        for traders in sellers
        for cost in traders.redemptions_or_costs
    ]

    # Throw all the redemption values in a list and sort them, then append the
    # last value again for graphing
    redemptions = [
        redemption
        for traders in bidders
        for redemption in traders.redemptions_or_costs
    ]

    return (costs, redemptions)

# *args at the beginning because: if only 1 list gets inputted, we know that
# it corresponds to list_of_traders; if 2 lists get inputted we know that
# they're costs and redemptions. However, the user can still use keyword
# arguments insteadj
#def find_equilibrium(*args, costs = None, redemptions = None, list_of_traders = None) -> tuple:
#    if type(args) != list or tuple:
#        raise TypeError("Not a list")
#    if list_of_traders == None and len(args) == 0:
#        # Need at least one of both costs and redemptions
#        if type(costs) == None and type(redemptions) != None:
#            raise ValueError("Need costs as well as redemptinos")
#        if type(costs) != None and type(redemptions) == None:
#            raise ValueError("Need redemptions as well as costs")

# We could do the above, but who cares
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

def plot_supply_demand(list_of_traders, min_price=None, max_price=None, ax=None):
    # Gets the current axis, useful in order to plot this graph on its own or
    # next to another graph
    ax = ax or plt.gca()

    costs, redemptions = values_from_traders(list_of_traders)
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
    if ax == None:
        plt.show()

def plot_transactions(transaction_history, equilibrium_price: None|int|float = None, min_price = None, max_price = None, ax = None):
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
    ax.set_xlim(1, len(transaction_history))
    if min_price == None:
        min_price = min(transaction_history) - 1
    if max_price == None:
        max_price = max(transaction_history) + 1
    ax.set_ylim(min_price, max_price)
    # x range goes from 1 to len(transaction_history)+1
    ax.plot(range(1, len(transaction_history)+1), transaction_history)

    if type(period_lengths) != None:
        plt.vlines(period_lengths[:-1],
                   ymin=min_price,
                   ymax=max_price,
                   color='black',
                   linestyles='dashed')

    # If the equilibrium price is given, then graph it
    if type(equilibrium_price) != None:
        ax.hlines(y=equilibrium_price,  # Ignore dumb error
                xmin=1,
                xmax=len(transaction_history)+1,
                color='black')
    
    if ax == None:
        plt.show()

def plot_supply_demand_and_transactions(list_of_traders, prices, min_price = None, max_price = None):
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)

    plot_supply_demand(list_of_traders, min_price=min_price, max_price=max_price, ax=ax1)
    costs, redemptions = values_from_traders(list_of_traders)
    plot_transactions(prices, equilibrium_price=find_equilibrium(costs, redemptions)[1], min_price=min_price, max_price=max_price, ax=ax2)
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