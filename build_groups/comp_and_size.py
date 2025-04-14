def read_identifiers(filename):
    """Read identifiers from a file and return them as a set."""
    identifiers = set()
    with open(filename, 'r') as file:
        file.readline() # read the header
        for line in file:
            identifier = line.split(',')[0].strip().strip("\"")  # Assuming identifiers are at the beginning of each line
            identifiers.add(identifier)
    return identifiers

def store_sra_sizes(filename):
    """Read identifiers from a file and return them as a hash table id -> size"""
    #"acc","mbases","mbytes","avgspotlen","librarylayout","instrument"
    #"SRR22087708","383","129","290","PAIRED","Illumina NovaSeq 6000"
    id_size = {}
    total_sra_size = 0
    with open(filename, 'r') as file:
        file.readline() # read the header
        for line in file:
            try:
                fields = line.split(',')
                identifier = fields[0].strip().strip("\"")  #acc
                size = int(fields[1].strip().strip("\""))  #mbases
                id_size[identifier] = size
                total_sra_size += size
            except IndexError:
                print(f"Ignored line {line}")
    return id_size, total_sra_size
    

    

def main():
    import sys

    # Check if correct number of arguments are provided
    if len(sys.argv) != 4:
        print("Usage: python script.py file_A file_B file_C(sra_09042024_public.tsv)")
        return

    file_A = sys.argv[1]
    file_B = sys.argv[2]
    file_sizes = sys.argv[3]

    print(f"Store sizes from {file_sizes}")
    id_size, total_sra_size = store_sra_sizes(file_sizes)
    print(f"Cumulative size from {file_sizes} = {total_sra_size} mbases.")

    # Read identifiers from file B and store them in a set
    print(f"Indexing identifiers from {file_B}")
    identifiers_B = read_identifiers(file_B)
    nb_entries = 0
    nb_not_found = 0
    print(f"Counting identifiers from {file_A} not in {file_B}")
    # Compare identifiers from file A with those in file B
    notfound_sum_sizes = 0
    with open(file_A, 'r') as file:
        file.readline() # read the header
        for line in file:
            nb_entries += 1
            identifier = line.split(',')[0].strip().strip("\"")  # Assuming identifiers are at the beginning of each line
            if identifier not in identifiers_B:
                nb_not_found += 1
                if nb_not_found < 20:
                    print(f"First from {file_A} not found in {file_B}: {identifier}")
                if identifier in id_size: 
                    notfound_sum_sizes += id_size[identifier]

    print(f"Entries from {file_A} not found in {file_B}:")                      
    print(f" - Number: {nb_not_found} (among {nb_entries})")
    print(f" - Percentage among  {file_A}: {round(100*nb_not_found/nb_entries, 2)} %")
    print(f" - Sum size not found: {notfound_sum_sizes} (among {total_sra_size} mbases)")
    print(f"    - This is {round(100*notfound_sum_sizes/total_sra_size, 2)} % of sra")
    print(f"    - size got from {file_sizes}")

if __name__ == "__main__":
    main()

