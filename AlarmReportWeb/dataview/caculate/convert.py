# Convert Dataframe to HTML Table
# input: pandas dataframe --> {"Date": [date1, date2], "M1601": [0.5, 0.3] ....}
# output: dict table --> {'th': ["Date", "M1601"]
#                          'tr':[
#                                [date1, 0.5]
#                                [date2, 0.3]
# ]

from .const import dateCol
import pandas as pd

def convert_df_to_table(df):
    # Datetime --> String format
    # df[dateCol] = df[dateCol].dt.strftime('%Y-%m-%d')
    # df[dateCol] = pd.to_datetime(df[dateCol].astype(str), format='%Y-%m-%d')
    # df = pd.DataFrame(df)
    # df.style.format({dateCol: lambda t: t.strftime('%Y-%n-%d')})
    df[dateCol] = df[dateCol].astype(str)
    # print(df[dateCol])
    th = list(df.keys())
    table = {
        'th': th,
        'tr': []
    }
    for index, row in df.iterrows():
        oneRow = [row[col] for col in th]
        table['tr'].append(oneRow)
    return table