import pandas as pd
import sys

def convert(line):
    return line.replace('/', '|')

df = pd.read_csv(sys.argv[1], sep=',')
df['choices'] = df['choices'].apply(convert)

df.to_csv(sys.argv[1], index=False)
