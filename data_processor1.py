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
    clean_time = data['#Time'].astype(str)

    final_data = pd.DataFrame({
        'Time': clean_time,
        'Power': clean_data
    })

    final_data.dropna(inplace=True)

    final_data.to_csv(f'{filename}_clean.csv', index=False)

    return final_data

if __name__ == '__main__':
    filename = sys.argv[1]
    data_processing(filename)


