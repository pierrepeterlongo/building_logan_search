def read_identifiers(filename):
    """Read identifiers from a file and return them as a set."""
    identifiers = set()
    with open(filename, 'r') as file:
        for line in file:
            identifier = line.split(',')[0].strip().strip("\"")  # Assuming identifiers are at the beginning of each line
            identifiers.add(identifier)
    return identifiers

def main():
    import sys

    # Check if correct number of arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python script.py file_A file_B")
        return

    file_A = sys.argv[1]
    file_B = sys.argv[2]

    # Read identifiers from file B and store them in a set
    print(f"Indexing identifiers from {file_B}")
    identifiers_B = read_identifiers(file_B)
    nb_entries = 0
    nb_not_found = 0
    print(f"Counting identifiers from {file_A} not in {file_B}")
    # Compare identifiers from file A with those in file B
    with open(file_A, 'r') as file:
        for line in file:
            nb_entries += 1
            identifier = line.split(',')[0].strip().strip("\"")  # Assuming identifiers are at the beginning of each line
            if identifier not in identifiers_B:
                nb_not_found += 1
                if nb_not_found < 2:
                    print(f"First from {file_A} not found in {file_B}: {identifier}")

    print(f"Entries from {file_A} not found in {file_B}:")                      
    print(f" - Number: {nb_not_found} (among {nb_entries})")
    print(f" - Percentage among  {file_A}: {round(100*nb_not_found/nb_entries)} %")

if __name__ == "__main__":
    main()

