import pandas as pd

# Path to the large Resume.csv file
input_path = r'd:/Cv Project/Resumes/Resume.csv'
# Path to save the sample
output_path = r'd:/Cv Project/Resumes/Resume_sample.csv'

# Number of rows to extract (excluding header)
N = 1000

# Read and write the sample
with pd.read_csv(input_path, chunksize=N) as reader:
    chunk = next(reader)
    chunk.to_csv(output_path, index=False)

print(f"Sample of {N} rows saved to {output_path}")
