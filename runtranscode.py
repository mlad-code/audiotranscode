#!/usr/bin/env python3

import os
import subprocess
import time

#time to wait before next split
pause_time = 360 #6 min
# Set the starting file
start_file = "split_aau"  # Replace with the desired starting file

# Get a list of files starting with 'filesplit*'
files = [f for f in os.listdir(".") if f.startswith("split_*")]
files.sort()  # Sort the files alphabetically  

# Iterate through the files, starting from the specified file
for i, file in enumerate(files):
    if file == start_file:
        print(f"Starting from file: {file}")
        break

for file in files[i:]:
    print(f"Executing file: {file}")
    # Execute the file with '/bin/sh'
    subprocess.run(["/bin/sh", file])

