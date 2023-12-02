import pandas as pd
import numpy as np
import locale
from datetime import datetime, timedelta
from scipy.optimize import fsolve

from get_balance import get_all_balances
from read_entries import get_ach_dataframe

INITIAL_MONTH = "2022-01"
# set up locale for currency display
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def calculate_npv(rate, cashflows, present_balance, num_trading_days=252):
    """Calculate NPV value equation.

    Args:
        rate(float): Discount rate (the unknown) for NPV.
        cashflows(list): A list of tuple (cashflow_amount, days).
        present_balance(float): Present balance.
        num_trading_days(int): Number of trading days per year.

    Returns:
        (equation): An equation for fsolve to solve.
    """

    # Sum of the PV of each initial_balance/deposit/withdrawal will be present_balance
    cashflow_pv = np.sum([cf * (1 + rate)**(days/num_trading_days)
                         for cf, days in cashflows])

    return cashflow_pv - present_balance


def get_normalized_return(start_month, end_month=None):
    """Get normalized (yearly) return within the given month range.

    Args:
        start_month(str): YYYY-MM.
        end_month(str): YYYY-MM, default = last month.
    """
    # Default end month is last month from now
    minus_two_months = datetime.now().month - 2
    last_month = f"{datetime.now().year if minus_two_months > 0 else datetime.now().year - 1}" \
        f"-{minus_two_months if minus_two_months > 0 else minus_two_months + 12}"

    if end_month is None:
        end_month = last_month

    next_month = int(end_month[-2:]) + 1
    next_year = int(end_month[:4]) + 1
    end_month_add_1 = f"{end_month[:4] if next_month < 13 else next_year}-{(next_month if next_month < 13 else 1):02d}"

    # Sanity check of time range
    if start_month < INITIAL_MONTH:
        print("Invalid start month: minimal start month is 202201.")
        return

    if end_month > last_month:
        print("Invalid end month: a future month was given.")
        return

    # Get start and end balances
    dict_balances = get_all_balances()
    # get rid of $ sign and commas
    start_balance = float(
        dict_balances[start_month][0].replace('$', '').replace(',', ''))
    end_balance = float(
        dict_balances[end_month][1].replace('$', '').replace(',', ''))

    # First business day in start_month (not accounting for holidays)
    # format "2023-11-24"
    start_date = str(np.busday_offset(start_month, 0, roll='forward'))
    # Last business day in end_month (not accounting for holidays)
    end_date = str(np.busday_offset(end_month_add_1, -1, roll='forward'))

    # Get ACH entries
    df = get_ach_dataframe()
    # Select entries within start and end dates
    df = df.loc[(df["SettledDate"] >= start_date)
                & (df["SettledDate"] <= end_date)]

    amounts = df["Amount"].to_list()
    amounts = [start_balance] + amounts  # prepend start balance
    dates = df["SettledDate"].to_list()  # format 2022-03-25
    dates = [start_date] + dates  # prepend start date

    # Get 'days': number of business days between start and end dates
    lst_start_end_tuples = list(zip(dates, [end_date] * len(dates)))
    days = list(map(lambda x: np.busday_count(*x), lst_start_end_tuples))
    cashflows = list(zip(amounts, days))

    # Get the discount rate r by solving the equation
    discount_rate = fsolve(calculate_npv, x0=0.1,
                           args=(cashflows, end_balance))[0]
    rate = round(discount_rate * 100, 1)  # Convert to % and round

    # Create summary dataframe
    summary_df = pd.DataFrame({'Amount': amounts, 'Date': dates, 'Days': days})
    summary_df['Amount'] = summary_df['Amount'].apply(
        lambda val: locale.currency(val, grouping=True))
    summary_df.index.name = 'EntryID'

    # Print result and summary
    print('===============================================')
    print(f"Normalized return ({start_month} to "
          f"{end_month}) is {rate}%.")
    print('-----------------------------------------------')
    print(summary_df)
    print('-----------------------------------------------')
    print(f"Start Balance: {start_balance}")
    print(f"End Balance: {end_balance}")
    print('===============================================')


if __name__ == "__main__":
    # print("Calculate return...")
    start = input("Starting month (YYYY-MM): ")
    end = input("Ending month (YYYY-MM): ")
    get_normalized_return(start, end if end != '' else None)
