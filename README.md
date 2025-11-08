# Todo:
- [x] Rename `zit.py` to `main.py`
- [ ] Make sure that `config.py` is validating everything for any scenario (try putting weird values in `config.toml` and check that `config.py` handles them correctly)
- [x] In `config.py`, there's no good reason to use `os.urandom(256)` instead of a random value from the `random` module to assign a value to `random_seed` (line 31) so we should just get rid of the `os` module
- [ ] Check that what happens when `graphs = 4` makes sense (I think we might be running the market function one too many times, or switching between constrained and unconstrained traders one too many times)
    - [ ] Code it will always put the unconstrained traders at the top row and constrained traders on the bottom row? (Right now whatever the user configured is on the bottom row and the opposite is on the top row, I think)
- [ ] Add costs and redemption values that mimic the figures in the paper into `config.toml`
- [ ] Figure out a way to solve the mutability problem in `market.py` (line 98) so that we can get rid of the copy module?
- [ ] Check if the `plot_supply_demand()` and `plot_transactions()` functions actually need to check whether the equilibrium price exists (if the equilibrium price didn't exist, the equilibrium lines would just be plot in a place where nobody's looking). If we actually do need to check for it:
    - [ ] For the `plot_transactions()` function in `graphs.py`, line 139 checks whether the equilibrium price is -1 instead of None, which is bad, since when the `find_equilibrium()` function doesn't find an equilibrium it returns an equilibrium price of -1. The solution to this is either making `find_equilibrium()` return None when it can't find an equilibrium (remember to change the typehint for the function's output!) or making `plot_transactions()` check for -1 instead of None.
    - [ ] Make the `plot_supply_demand()` check whether the equilibrium exists before plotting it
- [ ] Check which functions have parameters that don't need to be there (some of the functions in `market.py` look pretty suspect)


Graph from Gode & Sunder:

<img width="640" height="480" alt="Screenshot 2025-10-30 000612" src="https://github.com/user-attachments/assets/72b8919f-a769-4dd1-b8db-c0c9b7bb3af0" />

Graph from code:

<img width="640" height="480" alt="Figure_1" src="https://github.com/user-attachments/assets/74a460c7-5087-46a9-8b3c-534a2d38addb" />
