import os
import sys
import argparse
import re

def parse_arguments():
    parser = argparse.ArgumentParser(description="List created indexes")
    
    parser.add_argument("--only-0s", action="store_true", help="Enable this option to restrict operation to 0s indexes")
    parser.add_argument("--parent-directory", required=True, type=str, help="Specify the parent directory")
    parser.add_argument("--root-dir", type=str, help="Specify the root directory")
    
    return parser.parse_args()

# Check if the directory path argument is provided
if len(sys.argv) < 2:
    print("Please provide the path to the parent directory as an argument.")
    sys.exit(1)

# Function to extract the integer part from the key
def extract_integer(key):
    return int(key.split('_')[0])

def main():
    args = parse_arguments()
    only_0s = args.only_0s
    parent_directory = args.parent_directory
    root_dir = args.root_dir
    if root_dir != None: 
        root_dir = root_dir.rstrip("/") + "/" # be sure we have only one '/' on the right of the root_dir
    else:
        root_dir = ""
    
    ssubdirectory_path = {}
    
    # Traverse all directories and subdirectories
    for directory in os.listdir(parent_directory): # eg. /tmp/data/GENOMIC_VRL/fe
        if not os.path.isdir(f"{parent_directory}/{directory}"): continue
        for subdirectory in os.listdir(f"{parent_directory}/{directory}"): # eg. /tmp/data/GENOMIC_VRL/fe/02ac2275ab22e25ef04f15d3dbdb0e/
            if not os.path.isdir(f"{parent_directory}/{directory}/{subdirectory}"): continue
            error_file=f"{parent_directory}/{directory}/{subdirectory}/.command.err"
            # the error_file should exist 
            if not os.path.exists(error_file): continue
            # its size can be non null even in case of succes. Happens when several attempts were made during download of unitigs
            # COMMENTED on purpose: if os.path.getsize(error_file) > 0: continue
            for ssubdirectory in os.listdir(f"{parent_directory}/{directory}/{subdirectory}"): # eg  /tmp/data/GENOMIC_VRL/fe/02ac2275ab22e25ef04f15d3dbdb0e/1_21
                if not os.path.isdir(f"{parent_directory}/{directory}/{subdirectory}/{ssubdirectory}"): continue
                if not re.match(r'[0-9]*_[0-9]*', ssubdirectory): continue # the name is not respected
                if only_0s and not ssubdirectory.startswith("0_"): continue # avoid already created non 0_* indexes
                if ssubdirectory in ssubdirectory_path: # do not duplicate 
                    print(f'Warning, {ssubdirectory} is duplicated', file=sys.stderr)
                    continue 
                
                # Store the association
                # print(f"{ssubdirectory} {root_dir}{directory}/{subdirectory}")  
                ssubdirectory_path[ssubdirectory] = f"{root_dir}{directory}/{subdirectory}"
    
    sorted_keys = sorted(ssubdirectory_path.keys(), key=extract_integer)
    # prints sorted directories 
    for key in sorted_keys:
        print(f"{key} {ssubdirectory_path[key]}")



if __name__ == "__main__":
    main()
