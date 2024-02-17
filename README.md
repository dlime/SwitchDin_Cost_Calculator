# Assumptions
List of assumptions and implementation details

- total cost is the sum of `grid cost` and `battery degradation cost` for each interval
- battery degradation formula has been re-adapted to reflect that the cumulative sum has to be 1 over time:
  - `degradation = (abs(energy_flow_kwh) / capacity_in_kwh ) / (rated_cycles / 2)` 
- for costs, `Decimal` is used as data type instead of float for better rounding & arithmetics 
- energy interval is assumed always the same in the `energy flow` table
- energy tariff are the same when either using or selling grid's energy
- energy tariff are given as Weekday / Weekend and through time intervals (refer to `energy_tariff.json`)
- energy tariff are applied taking using only the start of the time interval

# Setup
```shell
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

# How to run
- complete all the steps in [setup](#setup)
- run (with default parameters)
    ```shell
    python cost_calculator.py
    ```
- to print a list of possible parameters use:
    ```shell
    python cost_calculator.py --help
    ```
