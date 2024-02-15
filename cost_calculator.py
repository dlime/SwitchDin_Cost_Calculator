import argparse
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, getcontext

import pandas as pd

QUANTIZE_ROUND = Decimal("0.01")
INTERVAL_TIME_IN_SECONDS = 0


def round_decimal(input: Decimal) -> Decimal:
    return input.quantize(QUANTIZE_ROUND, rounding=ROUND_HALF_UP)


def round_float_to_decimal(input: float) -> Decimal:
    return round_decimal(Decimal(input))


def create_energy_flow_df():
    # Creates a date range for 10 minutes with 1-minute intervals
    date_range = pd.date_range(
        start=datetime.now().replace(second=0, microsecond=0), periods=10, freq="min"
    )
    grid_energy_flow_kw = [5, -3, 4, -2, 5, -3, 4, -2, 5, -3]
    battery_energy_flow_kw = [-100, 2, -1.5, 2.5, -1, 2, -1.5, 2.5, -1, 2]
    df = pd.DataFrame(
        {
            "datetime": date_range,
            "grid_energy_flow_kW": grid_energy_flow_kw,
            "battery_energy_flow_kW": battery_energy_flow_kw,
        }
    )
    print("-" * 100)
    print("Energy flow values")
    print(df)
    print("-" * 100)
    return df


def create_energy_tariffs_dict():
    return {
        "Weekday": {
            "00:00-06:00": round_float_to_decimal(0.10),
            "06:01-18:00": round_float_to_decimal(0.20),
            "18:01-23:59": round_float_to_decimal(0.15),
        },
        "Weekend": {
            "00:00-23:59": round_float_to_decimal(0.05),
        },
    }


def get_day_type(date_time: datetime) -> str:
    return "Weekday" if date_time.weekday() < 5 else "Weekend"


def get_current_tariff(date_time: datetime, tariffs: dict) -> Decimal:
    day_type = get_day_type(date_time)
    time_str = date_time.strftime("%H:%M")
    for time_range, tariff in tariffs[day_type].items():
        start, end = time_range.split("-")
        if start <= time_str <= end:
            return tariff

    # print error here
    return Decimal(0)


def calculate_battery_cost(
    battery_replacement_cost: Decimal,
    battery_capacity_in_kwh: float,
    battery_rated_cycles: int,
    energy_flow_kw: float,
) -> Decimal:
    battery_energy_flow_kwh = calculate_energy_flow_in_kwh(energy_flow_kw)
    degradation = (abs(battery_energy_flow_kwh) / battery_capacity_in_kwh) / (
        battery_rated_cycles / 2
    )
    battery_cost = Decimal(degradation) * battery_replacement_cost
    return round_decimal(battery_cost)


def calculate_energy_flow_in_kwh(energy_flow: float) -> float:
    return energy_flow * (INTERVAL_TIME_IN_SECONDS / 3600)


def calculate_grid_cost(
    grid_energy_flow_kw: float, date_time: datetime, energy_tariffs: dict
) -> Decimal:
    grid_energy_flow_kwh = calculate_energy_flow_in_kwh(grid_energy_flow_kw)
    if Decimal(grid_energy_flow_kwh).is_zero():
        return Decimal(0)

    current_tariff = get_current_tariff(date_time, energy_tariffs)
    grid_cost = current_tariff * Decimal(grid_energy_flow_kwh)
    return round_decimal(grid_cost)


def main(args):
    energy_flow_df = create_energy_flow_df()
    energy_tariffs = create_energy_tariffs_dict()
    find_interval_time_from_dataframe(energy_flow_df)

    cost_by_interval_df = calculate_costs_for_each_interval(
        args, energy_flow_df, energy_tariffs
    )
    print("-" * 100)
    print("Costs per interval:")
    print(cost_by_interval_df)

    total_time_window_cost = round_float_to_decimal(
        cost_by_interval_df["total_cost"].sum()
    )
    print("")
    print(f"Total cost for the whole time window: {total_time_window_cost}")
    print("-" * 100)


def calculate_costs_for_each_interval(
    args, energy_flow_df: pd.DataFrame, energy_tariffs: dict
) -> pd.DataFrame:
    cost_by_interval_df = pd.DataFrame(
        index=energy_flow_df.index, columns=["grid_cost", "battery_cost", "total_cost"]
    )
    for idx, row in energy_flow_df.iterrows():
        grid_cost = calculate_grid_cost(
            grid_energy_flow_kw=row["grid_energy_flow_kW"],
            date_time=row["datetime"],
            energy_tariffs=energy_tariffs,
        )
        battery_cost = calculate_battery_cost(
            battery_replacement_cost=args.battery_replacement_cost,
            battery_capacity_in_kwh=args.battery_capacity_in_kwh,
            battery_rated_cycles=args.battery_rated_cycles,
            energy_flow_kw=row["battery_energy_flow_kW"],
        )
        total_cost = grid_cost + battery_cost
        cost_by_interval_df.loc[idx] = [grid_cost, battery_cost, total_cost]
    return cost_by_interval_df


def find_interval_time_from_dataframe(energy_flow_df):
    datetime_first = energy_flow_df.loc[0, "datetime"]
    datetime_second = energy_flow_df.loc[1, "datetime"]
    global INTERVAL_TIME_IN_SECONDS
    INTERVAL_TIME_IN_SECONDS = (datetime_second - datetime_first).total_seconds()


if __name__ == "__main__":
    getcontext().prec = 2  # Sets Decimal precision to 2

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--energy_flow_path",
        default="",
        help="Path for energy flow data pickle file",
    )
    parser.add_argument(
        "-t",
        "--energy_tariff_costs_path",
        default="",
        help="Path for energy tariff costs pickle file",
    )
    parser.add_argument(
        "-b",
        "--battery_replacement_cost",
        default=1000,
        type=Decimal,
        help="Cost of replacing the battery once it has reached the end of its life in AUD",
    )
    parser.add_argument(
        "-c",
        "--battery_capacity_in_kwh",
        default=1000,
        type=float,
        help="Rated capacity of the battery in kWh",
    )
    parser.add_argument(
        "-rc",
        "--battery_rated_cycles",
        default=1000,
        type=int,
        help="Number of charge/discharge cycles the battery is rated for.",
    )
    args = parser.parse_args()

    main(args)
