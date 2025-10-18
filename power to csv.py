from ENG110_python import get_eng110_data
import pandas as pd
import time
import sys

def savedata(timeout: int = 10, identifier: str = '')->pd.DataFrame:


    watts = []
    seconds = []
    for i in range(timeout):
        values = get_eng110_data()
        watts.append(values[2])
        clock = time.localtime()
        seconds.append(f'{clock[3]}:{clock[4]}:{clock[5]}}')
        time.sleep(1)
        print(f'Watts value is {values[2]}')
        print(f'Time is now {clock[3]}:{clock[4]}:{clock[5]}')

    data = pd.DataFrame({
        'Watts': watts,
        'Time': seconds
    })

    data.to_csv(f'{identifier}.csv')

    return data

if __name__=='__main__':
    times = int(sys.argv[1])
    identifier = str(sys.argv[2])
    data = savedata(timeout=times)
