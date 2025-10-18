from ENG110_python import get_eng110_data
import pandas as pd
import time
import sys

def savedata(timeout: int = 10, identifier: str = 'totalpower')->pd.DataFrame:


    watts = []
    seconds = []
    for i in range(timeout):

        values = get_eng110_data()
        watts.append(values[2])
        clock = time.localtime()

        seconds.append(f'{clock[3]}:{str(clock[4]).zfill(2)}:{str(clock[5]).zfill(2)}')
        print(f'Time is now {clock[3]}:{str(clock[4]).zfill(2)}:{str(clock[5]).zfill(2)}')
        print(f'Watts value is {values[2]}. {i}/{timeout}')

        time.sleep(1)



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

