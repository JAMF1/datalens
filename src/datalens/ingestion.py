import pandas as pd 

# Accept a path or file-like object.
# Read a CSV with pandas and return the complete DataFrame.
# Handle a completely empty file deliberately.
# Decide how to handle malformed CSV input.
# Preserve useful diagnostic information when an error is wrapped.
# Keep Flask, HTML, preview logic, and duplicate detection out of this module.

def load_data(file):
    df = pd.read_csv(filepath_or_buffer=file
                     )
    print(df.columns)
    #print(df.info())
    #print(df.describe())
    #print(df.head(10))


load_data("tests/Social_media_impact_on_life.csv")

