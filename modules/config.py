import os
import random
import tomllib

with open('config.toml', 'rb') as f:
    # Load in the data
    config = tomllib.load(f)

    min_price = int(config['min_price'])
    max_price = int(config['max_price'])
    num_traders = int(config['num_traders'])
    periods = int(config['periods'])
    constrained = bool(config['constrained'])

    # explicit
    costs = sorted(list(config['explicit']['costs']))
    redemption_values = sorted(list(config['explicit']['redemption_values']), reverse=True)

    # misc.
    num_commodities = int(config['misc']['num_commodities'])
    timeout = int(config['misc']['timeout'])
    quiet = bool(config['misc']['quiet'])
    random_seed = config['misc']['random_seed']
    graphs = int(config['misc']['graphs'])

# Validation and setting defaults
if type(random_seed) not in  (int, float, str, bytes, bytearray):
    raise TypeError("The only supported types for random_seed are: int, float, str, bytes, and bytearray")
if random_seed == 0:
    # Need this for reproducing traders (i.e. for the big graph = 4)
    random_seed = os.urandom(256)
random.seed(random_seed)

if min_price > max_price:
    raise ValueError("min_price must be lesser than max_price")
if min_price < 0:
    raise ValueError("min_price must be greater than 0")
if max_price < 0:
    raise ValueError("max_price must be greater than 0")

if num_traders <= 0:
    raise ValueError("num_traders must be greater than 0")
if num_traders % 2 != 0:
    raise ValueError("num_traders must be even (should be the same number of buyers as bidders)")

if periods <= 0:
    raise ValueError("periods must be greater than 0")

if len(costs) != len(redemption_values):
    raise ValueError(f"The length of the costs {len(costs)} must be equal to the length of redemption_values {len(costs)}")
if len(costs) == 0:
    costs = None
if len(redemption_values) == 0:
    redemption_values = None

if graphs not in [0, 1, 2, 3, 4]:
    raise ValueError("graphs can only be either 0, 1, 2, 3, or 4")