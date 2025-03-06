import csv

# Input and output file paths
input_file = 'labels_LD_rc_t40_t50.csv'
output_file = 'labels_LD_rc_t40_t50_fixed.csv'

# Step 1: Determine the maximum number of columns
max_columns = 0
with open(input_file, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) > max_columns:
            max_columns = len(row)

# Step 2: Pad rows with fewer columns
with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    for row in reader:
        # Pad the row with empty strings if it has fewer columns
        padded_row = row + [''] * (max_columns - len(row))
        writer.writerow(padded_row)

# Step 3: Read the preprocessed file using pandas
import pandas as pd
df = pd.read_csv(output_file)
print(df)
