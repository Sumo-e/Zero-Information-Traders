import random
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
periods = int(f_dict['periods'])
timeout = int(f_dict['timeout'])
constrained = bool(f_dict['constrained'])
random_seed = int(f_dict['random_seed'])

if f_dict['quiet'].lower() == 'true':
    quiet = True
elif f_dict['quiet'].lower() == 'false':
    quiet = False

if num_traders % 2 != 0:
    raise ValueError("The number of traders must be even (should be the same number of buyers as bidders). Change 'num_traders'")
###########################  End of Config  ############################