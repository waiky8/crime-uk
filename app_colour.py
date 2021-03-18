import pandas as pd
import datetime
import time
import glob
import os

'''
====================================
ADD COLOUR COLUMN FOR MAPBOX MARKERS
====================================
'''

serious_crime_1 = ["Robbery", "Violence and sexual offences"]
serious_crime_2 = ["Burglary", "Vehicle crime"]

crime_files = glob.glob(os.path.join("*street*.csv"))


def main():
    start_time = time.time()

    for f in crime_files:
        print("*** ", f)
        df = pd.read_csv(f)

        if {"COLOUR"}.issubset(df.columns):
            df.drop("COLOUR", inplace=True, axis=1)

        colour = []

        for r in range(0, len(df)):

            ctype = df["Crime type"][r]

            if ctype in serious_crime_1:
                c = "red"
            elif ctype in serious_crime_2:
                c = "orangered"
            else:
                c = "dodgerblue"

            colour.append(c)

            print(r, ctype, ">", c)

        df["COLOUR"] = colour
        df.to_csv(f, index=False, encoding="utf-8")

    elapsed_time = time.time() - start_time
    print("\n", datetime.timedelta(seconds=elapsed_time))


if __name__ == "__main__":
    main()
