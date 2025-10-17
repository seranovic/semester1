import pandas as pd
import sys

def data_processing(filename: str) -> pd.DataFrame:

    data = pd.read_csv(f'{filename}')

    clean_data = pd.to_numeric(data[' pwr'], errors = 'coerce') #add a line to remove #NaN values
    clean_time = data['#Time'] #fix the random strings and convert into purely HH:MM:SS later.

    final_data = pd.DataFrame({
        'Time': clean_time,
        'Power': clean_data
    })

    final_data.to_csv(f'{filename}_clean.csv', index=False)

    return final_data

if __name__ == '__main__':
    filename = sys.argv[1]
