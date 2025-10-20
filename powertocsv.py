from ENG110_python import get_eng110_data
import pandas as pd
import time
import sys

def savedata(timeout: int = 10, identifier: str = 'totalpower')->pd.DataFrame:
    """
    Saves data from ENG110 device into csv and dataframe with two columns. A time column in HH:MM:SS format
    and another column containing the power data in W, Watts.

    Args:
        timeout: delay between data points
        identifier: name of csv file to be saved

    Returns: DataFrame containing the data.

    """

    watts = []
    seconds = []
    for i in range(timeout):

        values = get_eng110_data()
        watts.append(values[2])
        clock = time.localtime() #get local time

        seconds.append(f'{clock[3]}:{str(clock[4]).zfill(2)}:{str(clock[5]).zfill(2)}') #saves local time in HH:MM:SS format
        print(f'Time is now {clock[3]}:{str(clock[4]).zfill(2)}:{str(clock[5]).zfill(2)}')
        print(f'Watts value is {values[2]}. {i}/{timeout}')

        while clock[5] == time.localtime()[5]: # while time is same waits 0.1 secs
            time.sleep(0.1)



    data = pd.DataFrame({
        'Watts': watts,
        'Time': seconds
    })

    data.to_csv(f'{identifier}.csv')
    print(f'Data saved to {identifier}.csv')

    return data

if __name__=='__main__':
    times = int(sys.argv[1])
    identifier = str(sys.argv[2])
    data = savedata(timeout = times, identifier = identifier)

