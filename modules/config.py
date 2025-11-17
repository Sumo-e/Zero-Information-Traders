import random
import os
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

cfg_path = Path(os.environ.get("ZIT_CONFIG_PATH", Path(__file__).with_name("config.toml")))  # No CWD fragility
if not cfg_path.exists():
    raise FileNotFoundError(f"Missing config file: {cfg_path}")  # Explicit, actionable error

with cfg_path.open('rb') as f:
    # Load in the data
    config = tomllib.load(f)

    # tolerate missing subsections
    explicit = config.get('explicit', {})
    misc = config.get('misc', {})

    # required top-level keys with strict casting
    min_price = int(config['min_price'])
    max_price = int(config['max_price'])
    num_traders = int(config['num_traders'])
    periods = int(config['periods'])
    constrained = bool(config['constrained'])

    # explicit lists: accept missing -> [], validate numeric, sort only if non-empty
    _costs = explicit.get('costs') or []
    if not all(isinstance(x, (int, float)) for x in _costs):
        raise ValueError("explicit.costs must be numbers")
    _costs = [int(x) for x in _costs]  # ensure integer price grid consistency
    costs = sorted(_costs) if _costs else [] # avoid pointless sort on empty

    _reds = explicit.get('redemption_values') or []
    if not all(isinstance(x, (int, float)) for x in _reds):
        raise ValueError("explicit.redemption_values must be numbers")
    _reds = [int(x) for x in _reds]
    redemption_values = sorted(_reds, reverse=True) if _reds else []

    # misc with safe defaults and strict casting
    num_commodities = int(misc.get('num_commodities', 1))
    timeout = int(misc.get('timeout', 1))
    quiet = bool(misc.get('quiet', False))
    random_seed = misc.get('random_seed', 0)
    graphs = int(misc.get('graphs', 0))

# Validation and setting defaults
if not isinstance(random_seed, (int, float, str, bytes, bytearray, type(None))):
    raise TypeError(f"random_seed must be int/float/str/bytes/bytearray/None, got {type(random_seed).__name__}")

if random_seed == 0:
    # Need this for reproducing traders (i.e. for the big graph = 4)
    random_seed = random.randint(0, 2**32 - 1)
random.seed(random_seed)

if min_price < 1:
    raise ValueError(f"min_price must be ≥ 1, got {min_price}")
if max_price < 1:
    raise ValueError(f"max_price must be ≥ 1, got {max_price}")
if min_price > max_price:
    raise ValueError(f"min_price ({min_price}) must be ≤ max_price ({max_price})")

if num_traders < 2 or num_traders % 2 != 0:
    raise ValueError("num_traders must be an even integer ≥ 2")

if periods <= 0:
    raise ValueError(f"periods must be > 0, got {periods}")

if num_commodities <= 0:
    raise ValueError(f"num_commodities must be > 0, got {num_commodities}")

if len(costs) != len(redemption_values):
    raise ValueError(f"The length of the costs {len(costs)} must be equal to the length of redemption_values {len(redemption_values)}")

# keep explicit schedules within the declared price grid
if costs and any(c < min_price or c > max_price for c in costs):
    raise ValueError("explicit.costs contain values outside [min_price, max_price]")
if redemption_values and any(v < min_price or v > max_price for v in redemption_values):
    raise ValueError("explicit.redemption_values contain values outside [min_price, max_price]")

# normalize empties to None
if not costs:
    costs = None
if not redemption_values:
    redemption_values = None

if graphs not in (0, 1, 2, 3, 4):
    raise ValueError(f"graphs must be one of 0,1,2,3,4, got {graphs}")


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
    random_seed = random.randint(0, 2**32 - 1)
random.seed(random_seed)

if min_price > max_price:
    raise ValueError("min_price must be less than max_price")
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
    raise ValueError(f"The length of the costs {len(costs)} must be equal to the length of redemption_values {len(redemption_values)}")
if len(costs) == 0:
    costs = None
if len(redemption_values) == 0:
    redemption_values = None

if graphs not in [0, 1, 2, 3, 4]:
    raise ValueError("graphs can only be either 0, 1, 2, 3, or 4")
def validate_config(config: dict):
    required_keys = ["graphs", "market_type", "num_traders", "random_seed"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

    if not isinstance(config["graphs"], int) or config["graphs"] <= 0:
        raise ValueError("`graphs` must be a positive integer")

    if config["market_type"] not in ["constrained", "unconstrained", "mixed"]:
        raise ValueError("`market_type` must be one of: 'constrained', 'unconstrained', 'mixed'")

    if not isinstance(config["num_traders"], int) or config["num_traders"] <= 0:
        raise ValueError("`num_traders` must be a positive integer")

    if not isinstance(config["random_seed"], int):
        raise ValueError("`random_seed` must be an integer")
