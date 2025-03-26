
import os
import math
import sys

def index_id_to_size(file_name, kmer_size):
    id_to_size = {}
    with open(file_name) as file:
        file.readline() # first line is accession,seqstats_unitigs_nbseq,seqstats_unitigs_sumlen
        for l in file:
            l = l.strip().split(',')
            cur_id = l[0]
            nb_unitigs = int(l[1])
            cumulative_size = int(l[2])
            assert cur_id not in id_to_size
            id_to_size[cur_id] = cumulative_size - ((kmer_size-1)*nb_unitigs) # k-1 kmers are excluded (at the end) from each unitig. 
    return id_to_size



# Create a class to store the file name and size.
# It contains the name of the file, the size of the file, and the full path to the file.
class File:
    def __init__(self, name, size, path):
        self.name = name
        self.size = size
        self.path = path
        
    def __str__(self):
        return f"File name: {self.name}, File size: {self.size}, File path: {self.path}"
    

# Class that contains a list of files
# Files are organized in groups.
# Inside a group files have similar sizes (all with the same log_2 number of bits)
# A group size is limited by the size of the files it contains.
# The class organizes the files in groups and returns a list of groups.
class FileList:
    def __init__(self): 
        # dictionary mapping a log2 nb kmers to max nb of files per group, with the following rules: 
        # for lognbkmers from From 0 to 27 -> b=1024
        #  lognbkmers: 28 -> b 512
        #  lognbkmers: 29 -> b 256
        #  lognbkmers: 30 -> b 128
        #  lognbkmers: 31 -> b 64
        #  lognbkmers: 32 -> b 32
        #  lognbkmers: 33 -> b 16
        #  lognbkmers: 34 -> b 8
        #  lognbkmers: 35 -> b 4
        #  lognbkmers: 36 -> b 2
        #  lognbkmers: 37 -> b 1
        #  lognbkmers>38 -> b 1
        self.max_group_size = {a: 
            2048 if 0 <= a <= 26 else 
            1024 if a == 27 else
            512 if a == 28 else 
            256 if a == 29 else 
            128 if a == 30 else 
            64 if a == 31 else
            32 if a == 32 else 
            16 if a == 33 else 
            8 if a == 34 else 
            1 if a == 35 else 
            1 if a == 36 else 
            1 for a in range(50)}
        
        self.group_sizes = {} # key: size (log2), value: a set of groups with that size. Each group is a list of files.

        
    def add_file(self, file):
        if file.size == 0:
            return
        # first time we see a file with this size
        log_size = int(math.log2(file.size))
        # bf_size = int(-math.pow(2, log_size+1)* math.log(0.25) / math.pow(math.log(2),2))
        if log_size not in self.group_sizes:
            self.group_sizes[log_size] = [[file]]
            return
        # we already have files with this size
        Nb_in_last_group = len(self.group_sizes[log_size][-1])
        # We have space in the last group. Just add the file to the last group.
        if Nb_in_last_group < self.max_group_size[log_size]:
            self.group_sizes[log_size][-1].append(file)
        # We don't have space in the last group. Create a new group.
        else:
            self.group_sizes[log_size].append([file])
            
    # An Index Path File (ipf)
    # Contains one name: unitig path per line (AWS opendata link)
    # The filename is <INDEX_ID>_<log_size>.txt
    # Create a index paths files (ipf) from the computed groups.
    def create_ipfs(self, directory_name):
        for size in self.group_sizes.keys():
            group_number = 0
            for group in self.group_sizes[size]:
                if group_number == 0:
                    ipf_name = f"{directory_name}/0s/{group_number}_{size}.txt"
                else:
                    ipf_name = f"{directory_name}/others/{group_number}_{size}.txt"
                with open(ipf_name, "w") as ipf:
                    for file in group:
                        ipf.write(f"{file.name}: {file.path}\n")
                group_number += 1
    

def main():
    if len(sys.argv) != 5:
        print("Usage: python create_fof.py accessions_file stat_file out_directory_name kmer_size")
        exit(1)
    accessions_file = sys.argv[1]
    stat_file = sys.argv[2]
    directory_name = sys.argv[3]
    kmer_size = int(sys.argv[4])
    # check that the directory exists
    if not os.path.isdir(directory_name):
        os.mkdir(directory_name) 
    if not os.path.isdir(directory_name+"/0s"):
        os.mkdir(directory_name+"/0s") 
    if not os.path.isdir(directory_name+"/others"):
        os.mkdir(directory_name+"/others") 
    fl = FileList()
    nb_files = 0
    sum_nb_kmers = 0
    print(f"indexing sizes from {stat_file}")
    id_to_size = index_id_to_size(stat_file, kmer_size)
    print(f"Load files to be fofed")
    nb_not_found = 0
    # prev_id=""
    with open(accessions_file) as file: 
        for name in file: # DRR000001
            name = name.strip()
            # print(f"Processing {name}")
            if name not in id_to_size:
                nb_not_found += 1
                if nb_not_found == 1:
                    print(f"first not found: {name}")
                continue
            nb_files += 1
            # assert name in id_to_size, f"{name} not found in {sizes_file}"
            file_size = id_to_size[name]
            sum_nb_kmers += file_size
            file_path = f"{name}.unitigs.fa.zst"
            # print(f"file {file_path}, has size {file_size}")
            fl.add_file(File(name, file_size, file_path))
        print(f"Fofing")
        fl.create_ipfs(directory_name)
    print(f"Done, fofs are in directory {directory_name}")
    print(f"There were {nb_not_found} accessions not in file {stat_file}")
    print(f"This is {round(100*nb_not_found/nb_files,2)}% of the file")
    print(f"Statistics for {directory_name}: {nb_files} accessions {sum_nb_kmers} cumulated kmers")
    
if __name__ == "__main__":
    main()

