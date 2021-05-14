import pandas as pd
import datetime
import time
import glob
import os

'''
====================================
ADD ICON COLUMN FOR MAPBOX MARKERS
====================================
'''

crime_files = glob.glob(os.path.join('*street*.csv'))


def main():
    start_time = time.time()

    for f in crime_files:
        print('*** ', f)
        df = pd.read_csv(f)

        if {'ICON'}.issubset(df.columns):
            df.drop('ICON', inplace=True, axis=1)

        icon = []

        for r in range(0, len(df)):

            ctype = df['Crime type'][r]

            if ctype == 'Anti-social behaviour':
                c = '😈'
            elif ctype == 'Bicycle theft':
                c = '🚲'
            elif ctype == 'Burglary':
                c = '🏠'
            elif ctype == 'Criminal damage and arson':
                c = '🔥'
            elif ctype == 'Drugs':
                c = '💊'
            elif ctype == 'Other crime':
                c = '😲'
            elif ctype == 'Other theft':
                c = '😲'
            elif ctype == 'Possession of weapons':
                c = '🔫'
            elif ctype == 'Public order':
                c = '😈'
            elif ctype == 'Robbery':
                c = '👊'
            elif ctype == 'Shoplifting':
                c = '🏪'
            elif ctype == 'Theft from the person':
                c = '😲'
            elif ctype == 'Vehicle crime':
                c = '🚗'
            elif ctype == 'Violence and sexual offences':
                c = '👊'

            icon.append(c)

            print(r, ctype, '>', c)

        df['ICON'] = icon
        df.to_csv(f, index=False, encoding='utf-8')

    elapsed_time = time.time() - start_time
    print('\n', datetime.timedelta(seconds=elapsed_time))


if __name__ == '__main__':
    main()
