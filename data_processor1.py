import time

import pandas as pd
import sys

def cleaner(filename: str) -> pd.DataFrame:
    """
    Takes nvidia-smi csv file, removes non-numeric power values, drops NaN values and
    overwrites and returns a dataframe containing the cleaned data.

    Args:
        filename: filepath pointing to nvidia-smi csv file.
    Returns:

    """

    data = pd.read_csv(f'{filename}')

    clean_data = pd.to_numeric(data[' pwr'], errors = 'coerce')
    str_time = data['#Time'].astype(str)

    final_data = pd.DataFrame({
        'Time': str_time,

        'Power': clean_data
    })

    final_data.dropna(inplace=True)

    final_data.to_csv(f'{filename}_clean.csv', index=False)

    return final_data


def tcleaner(series: pd.Series)->pd.Series:
    """Takes a HH:MM:SS string series and returns a linux epoch float representing that hour on the 10th of Oct 2025

    Args: string series with a time on HH:MM:SS format

    Returns: series with linux epoch float"""

    t = ('10 Oct 2025 ' + series).tolist()

    clean_time = []

    for i in range(len(series)):
        temp = time.strptime(t[i], '%d %b %Y %H:%M:%S')
        clean_time.append(time.mktime(temp))

    output = pd.Series(clean_time)

    return output

if __name__ == '__main__':
    print('Error')


