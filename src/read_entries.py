import pandas as pd
import numpy as np
import os
import pytest

path_to_entries = "/mnt/c/Users/Kyle/GoogleDrive/firstrade/entries"


def get_ach_dataframe():
    """Get entries involving ACH only.

    Returns:
        ach_df(pd.DataFrame): A dataframe containing ACH entries.
    """
    filenames = os.listdir(path_to_entries)

    for filename in filenames:

        df = pd.read_csv(os.path.join(path_to_entries, filename))
        ach_df = df.loc[(df["Action"] == "Other") & (
            df["Description"].str.contains("ACH"))][["SettledDate", "Amount"]]

    return ach_df


def main():
    print(get_ach_dataframe().info)


if __name__ == "__main__":
    main()
