# Assumptions
List of assumptions and implementation details

- total cost is the sum of 'grid cost' and 'battery degradation cost'
- for costs, Decimal is used as data type instead of float for better rounding & arithmetics 
- energy interval is always the same in the 'energy flow' table
- energy tariff are the same when either using or selling the energy from the grid
- energy tariff are given as Weekday / Weekend and through time intervals
- energy tariff are applied taking in account the start of the time interval (example: ....)

# Setup
```shell
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install requirements.txt
```

# How to run
- complete all the steps in [setup](#setup)
- run
```shell
python cost_calculator.py
```
