import os
import sys
import argparse

# ---------------------------------------------------------------------------- #
# Title: Clean Merged Indexes
# Author: Pierre Peterlongo
# Date: 2024 07 09
# Description: 
# This script is designed to clean merged index files. 
# Once merged a directory contains the merged indexes looks like: 
# ll index_TRANSCRIPTOMIC_VRT
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 10 -> /tmp/data/TRANSCRIPTOMIC_VRT/8c/b88375940c27c659c16d1cdf9bb119/0_10//
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 11 -> /tmp/data/TRANSCRIPTOMIC_VRT/50/36577715ffccd550269e37d9a00382/0_11//
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 12 -> /tmp/data/TRANSCRIPTOMIC_VRT/d6/c2e276996a3c3466f7d62aaf5bc4ef/0_12//
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 13 -> /tmp/data/TRANSCRIPTOMIC_VRT/65/054b1383a7517f2afdab28e6f7ffd7/0_13//
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 14 -> /tmp/data/TRANSCRIPTOMIC_VRT/4d/68e55be06d08197efb2bc90be21ecc/0_14//
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 15 -> /tmp/data/TRANSCRIPTOMIC_VRT/84/cf3ed59d4c2a3081081fd70e742f5e/0_15//
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 16 -> /tmp/data/TRANSCRIPTOMIC_VRT/90/ee5ea408d4086a06888370a1fe9cc8/0_16//
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 17 -> /tmp/data/TRANSCRIPTOMIC_VRT/1b/c9731257c39279b9206eef3880be04/0_17//
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 18 -> /tmp/data/TRANSCRIPTOMIC_VRT/79/33703ca2dbf80fa8c8a09c0d56e271/0_18//
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 19 -> /tmp/data/TRANSCRIPTOMIC_VRT/8c/6ab10522096559f9295c0b650aa9eb/0_19//
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 20 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_20/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 21 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_21/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 22 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_22/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 23 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_23/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 24 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_24/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 25 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_25/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 26 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_26/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 27 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_27/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 28 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_28/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 29 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_29/
# lrwxr-xr-x 1 root root      67 Jun 18 15:34 3 -> /tmp/data/TRANSCRIPTOMIC_VRT/84/12a975835aae435078c2e620d88a79/0_3//
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 30 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_30/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 31 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_31/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 32 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_32/
# lrwxr-xr-x 1 root root      44 Jun 18 15:34 33 -> /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_33/
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 34 -> /tmp/data/TRANSCRIPTOMIC_VRT/85/5901ce2954c47d0ac7a0a25e292824/0_34//
# lrwxr-xr-x 1 root root      68 Jun 18 15:34 35 -> /tmp/data/TRANSCRIPTOMIC_VRT/8d/2b079252855543fe294506fb652658/0_35//
# lrwxr-xr-x 1 root root      67 Jun 18 15:34 5 -> /tmp/data/TRANSCRIPTOMIC_VRT/24/c6609082230adfd24b2f70142cec1a/0_5//
# lrwxr-xr-x 1 root root      67 Jun 18 15:34 6 -> /tmp/data/TRANSCRIPTOMIC_VRT/7f/94a3da37b170c7e502017a3bb970e4/0_6//
# lrwxr-xr-x 1 root root      67 Jun 18 15:34 7 -> /tmp/data/TRANSCRIPTOMIC_VRT/e5/fe8237465eb3693222789177c7c64f/0_7//
# lrwxr-xr-x 1 root root      67 Jun 18 15:34 8 -> /tmp/data/TRANSCRIPTOMIC_VRT/3d/b5228a74e328a43ee325296cd04bec/0_8//
# lrwxr-xr-x 1 root root      67 Jun 18 15:34 9 -> /tmp/data/TRANSCRIPTOMIC_VRT/b5/7ab732f0c939b4039affe5ab9d2213/0_9//
# -rwxr-xr-x 1 root root 5041623 Jun 18 15:34 index.json*

# The directory contains additional sub directories that were merged and 
# that need to be removed. 
# Those are for instance: fa/87e02d212c279766981758fc7b7b77/
# As fa/87e02d212c279766981758fc7b7b77/ doest not appear as used in the index_TRANSCRIPTOMIC_VRT directory
# We can remove it
# In the other hand for instance 8c/6ab10522096559f9295c0b650aa9eb must not be removed 
# as it is used in the index_TRANSCRIPTOMIC_VRT directory (symbolic link 19)
# ---------------------------------------------------------------------------- #
def absoluteFilePaths(directory, only_directory = False):
    abspaths = set()
    directory = directory.rstrip("/") # be sure to keep only one '/'
    for filename in os.listdir(path = directory):
        abspath = f"{directory}/{filename}"
        if only_directory and not os.path.isdir(abspath): continue
        abspaths.add(abspath)
    return abspaths

def index_used_non_merged_indexes(libking):
    """In the directory (eg /tmp/data/TRANSCRIPTOMIC_VRT/index_TRANSCRIPTOMIC_VRT), find the indexes that are used, and index them
    
    They are those whose symbolic link target are not in the format /tmp/data/TRANSCRIPTOMIC_VRT/merged_index_*/
    """
    to_keep_indexes = set()
    directory = f"/tmp/data/{libking}/index_{libking}"
    # print(f"checking {directory}")
    merged_prefix = f"/tmp/data/{libking}/merged_index_" # files that start with this prefix are merged indexes
    # list all files in the directory
    for file in absoluteFilePaths(directory):
        if not os.path.islink(file): continue
        target = os.readlink(file)
        if not target.startswith(merged_prefix):
            # add the tartget to the set of indexes to keep, removing the last "/[0-9][0-9]/" part
            to_keep_indexes.add(target.rstrip("/").rsplit("/", 1)[0])
            

    # In some of the index by sizes (eg /tmp/data/{libking}/index_{libking}_18)
    # There are some non merged groups. 
    # Not to be removed: 
    for size in range (36):
        directory = f"/tmp/data/{libking}/index_{libking}_{size}"
        if not os.path.isdir(directory): 
            continue
        # print(f"checking {directory}")
        for file in absoluteFilePaths(directory):
            if not os.path.islink(file): continue
            target = os.readlink(file)
            if not target.startswith(merged_prefix):
                # add the tartget to the set of indexes to keep, removing the last "/[0-9][0-9]/" part
                if target.rstrip("/").rsplit("/", 1)[0] not in to_keep_indexes:
                    print(f"add {target.rstrip('/').rsplit('/', 1)[0]}")
                to_keep_indexes.add(target.rstrip("/").rsplit("/", 1)[0])
    
    return to_keep_indexes



def remove_non_used_indexes(libking, to_keep_indexes):
    """ In the /tmp/data/{libking} directory, find the indexes that are not in to_keep_indexes"""
    directory = f"/tmp/data/{libking}"
    merged_prefix = f"/tmp/data/{libking}/merged_index_" # files that start with this prefix are merged indexes
    index_prefix = f"/tmp/data/{libking}/index_{libking}" # files that start with this prefix are merged indexes
    useless = f"/tmp/data/{libking}/."
    nb_removed_directories = 0
    for file in absoluteFilePaths(directory, only_directory = True):
        if file.startswith(merged_prefix): continue
        if file.startswith(index_prefix): continue
        # if file.startswith(useless): continue
        # here we have a "*/??/"" directory, we double check if this is the case: 
        # get last value of the path
        last_value = file.rsplit("/", 1)[-1]
        if len(last_value) != 2: 
            print(f"Warning, dir {file} is not in the format ??/*, skipped")
        
        # now we explore the file directory. It contains for instance:
        # 21cdb2ad70b428718ee1b324eeab14	a0e4903eceaa2f9cbad186fef5cbf1	f915420df461ad282e5d4141cb51fb
        # for each subdir we check if {file}/{subdire} belongs to to_keep_indexes
        # print(f"Checking {file}")
        subdirs = absoluteFilePaths(file)
        for subdir in subdirs:
            if subdir not in to_keep_indexes: 
                print(f"Directory {subdir} is useless, I remove it")
                os.system(f"rm -rf {subdir}")
                # os.system(f"ls {subdir}")
                nb_removed_directories += 1
    return nb_removed_directories
                
        
        


def main():
    parser = argparse.ArgumentParser(description="Find and print the non-merged indexes that are used.")
    parser.add_argument("libking", type=str, help="The library key to specify which index directory to check.")
    
    args = parser.parse_args()
    print(f"Size before: ")
    os.system(f"du -bhs /tmp/data/{args.libking}")

    # Call the function and get the set of used non-merged indexes
    used_non_merged_indexes = index_used_non_merged_indexes(args.libking)
    
    # for used_non_merged_indexe in used_non_merged_indexes:
    #     print(f"used_non_merged_indexe: {used_non_merged_indexe}")
    
    # Call the function to remove the non-used indexes
    nb_removed_directories = remove_non_used_indexes(args.libking, used_non_merged_indexes)
    
    print(f"Removed {nb_removed_directories} directories")
    if nb_removed_directories > 0:
        print(f"Size After: ")
        os.system(f"du -bhs /tmp/data/{args.libking}")
    

if __name__ == "__main__":
    main()

    
    