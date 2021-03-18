import pandas as pd
import datetime
import time
import glob
import os

'''
=================================
MAP LSOA TO MORE DESCRIPTIVE MSOA
=================================
'''

crime_files = glob.glob(os.path.join("*street*.csv"))

pcode_files = glob.glob(os.path.join("*new*.csv"))
df_pcode = pd.concat((pd.read_csv(f, dtype="str") for f in pcode_files))


def main():
    start_time = time.time()

    for f in crime_files:
        print("*** ", f)
        df = pd.read_csv(f)

        if {"MSOA"}.issubset(df.columns):
            continue

        msoa = []

        for r in range(0, len(df)):

            try:
                lsoa = df["LSOA name"][r]

                m = get_msoa(lsoa)
                msoa.append(m)

            except Exception as e:
                m = ""
                msoa.append(m)
                print(e)

            print(r, lsoa, ">", m)

        df["MSOA"] = msoa
        df.to_csv(f, index=False, encoding="utf-8")

    elapsed_time = time.time() - start_time
    print("\n", datetime.timedelta(seconds=elapsed_time))


def get_msoa(lsoa):
    df1 = df_pcode[df_pcode["Lower layer super output area"].isin([lsoa])]

    if df1.empty:
        return ""
    else:
        return df1["Middle layer super output area"].iloc[0]


if __name__ == "__main__":
    main()
