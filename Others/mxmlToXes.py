import pm4py
import pandas as pd

mxml_file = "deliveroo_test_2023.mxml"

log = mxml_importer.apply(mxml_file)
dataframe = pd.DataFrame(log)

# Access the event data in the DataFrame
print(dataframe.head())