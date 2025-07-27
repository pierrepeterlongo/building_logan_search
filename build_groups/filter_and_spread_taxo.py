import gc

def index_superkingdom():
    # first store the division names 
    division_name = {}
    with open ("division.dmp") as file: 
        for l in file: 
            fields = l.split("\t|\t")
            division_name[fields[0]] = fields[1]
    
    taxid_superkingdom = {}
    with open ("nodes.dmp") as file: 
        for l in file: 
            fields = l.split("\t|\t")
            taxid_superkingdom[fields[0]] = division_name[fields[4]]
    
    ## HUMAN and MICE exceptions. See https://github.com/pierrepeterlongo/kmsra/issues/12
    ## HUMAN EXCEPTION 
    taxid_superkingdom["9604"] = "HUMAN"
    ## MICE EXCEPTION
    taxid_superkingdom["10066"] = "MICE"
    return taxid_superkingdom
        
def get_accessions(in_file):
    """Read identifiers from a file and return them as a set."""
    identifiers = set()
    with open(in_file, 'r') as file:
        file.readline() # read the header
        for line in file:
            identifier = line.split(',')[0].strip().strip("\"")  # Assuming identifiers are at the beginning of each line
            identifiers.add(identifier)
    return identifiers 
    
            

def process_file(input_file, taxid_superkingdom, to_index_accessions, public_file, logan_stats, logan_dispo):
    output_files = {}
    cpt = 0
    nb_distinct = 0
    nb_unknown = 0
    nb_not_indexed = 0
    nb_indexed = 0
    print(f"\nParsing file {input_file}")
    with open(input_file, 'r') as file:
        file.readline() # read the header
        line1 = file.readline() # read the first line
        while line1 != None: 
            cpt += 1
            if cpt % 1000000 == 0:
                print(f"\r{cpt} entry done", end='')
            
            fields1 = line1.split(',')    
            # get the next line for the same accession
            line2 = file.readline() 
            # should not occur, but just in case (if last line is unique)
            if line2 == None or line2 == "":
                abundance2 = 1
                future_line1 = None # prepare the next iteration
            # general case, have a look to the next line
            else:
                fields2 = line2.split(',')
                try:
                    abundance2 = int(fields2[4].strip().strip("\""))
                except IndexError:
                    print(f"IndexError occurred at line {line2}") # a few lines are not well formated
                    abundance2 = 1
                
                if fields1[0] != fields2[0]: # accession of line1 is unique. 
                    abundance2 = 1 # shoud be zero but it avoids a division by zero.
                    future_line1 = line2 # prepare the next iteration
                

                else: # read all lines (from third) for the same accession. 
                    while True: 
                        line3 = file.readline()
                        if line3 == None or line3 == "":
                            future_line1 = None
                            break
                        fields3 = line3.split(',')
                        if fields1[0] != fields3[0]:
                            future_line1 = line3 # prepare the next iteration
                            break
            
            try:
                cur_id = fields1[0].strip("\"")
                nb_distinct += 1
                
                if cur_id not in to_index_accessions: 
                    nb_not_indexed += 1
                    line1 = future_line1
                    continue
                nb_indexed += 1
                librarysource = fields1[1].strip("\"").replace(' ', '') # remove spaces from librarysource (VIRAL RNA -> VIRALRNA)
                taxid = fields1[3].strip("\"")
            
            except IndexError:
                print(f"IndexError occurred at line {line1}") # a few lines are not well formated
                line1 = future_line1
                continue 
            if taxid not in taxid_superkingdom:
                #### Commented : I do not try to save those entries anymore. 
                # print(f"NOT FOUND, id {taxid}")
                # full_superkingdom = get_superkingdom(taxid)
                # if full_superkingdom in superkingdom_mapping:
                #     taxid_superkingdom[taxid] = superkingdom_mapping[full_superkingdom]
                # else: 
                #     taxid_superkingdom[taxid] = "UNKNOWN"
                ####
                taxid_superkingdom[taxid] = "UNKNOWN"
                
            
            superkingdom = taxid_superkingdom[taxid]
            if superkingdom == "UNKNOWN":
                nb_unknown += 1
                
            
            # special non bacterial nor viral metag: check if is env
            if librarysource == "METAGENOMIC":
                if superkingdom != "BCT" and superkingdom != "VIR": 
                    abundance1 = int(fields1[4].strip().strip("\""))
                    assert abundance1 >= abundance2, f"abundance1: {abundance1}, abundance2: {abundance2}, \nline1 {fields1}, \nline2{fields2}"
                    ratio = abundance1/abundance2
                    if ratio < 100:
                        superkingdom = "ENV"
                    
                    
            output_filename = input_file.replace('.tsv', f'_{librarysource}_{superkingdom}.tsv')
            
            if output_filename not in output_files:
                output_files[output_filename] = open(output_filename, 'w')
            
            assert cur_id == line1.split(",")[0].strip("\""), f"accession is {cur_id} while line1 is {line1}"
            output_files[output_filename].write(line1)
            line1 = future_line1
    
    for file in output_files.values():
        file.close()
        
    print(f"\nDone. I treated {nb_distinct} distinct accessions from file {input_file}")
    print(f"Among them, {nb_not_indexed} accession are discarded ({round(100 * nb_not_indexed/nb_distinct, 2)}%) either because they are not in {public_file} or {logan_stats} or {logan_dispo}.")
    print(f"Among the {nb_indexed} remaining, {nb_unknown} have no superkingdom ({round(100*nb_unknown/nb_indexed, 2)}%). They are in {input_file}, but not in nodes.dmp")
    
    ## Show the librarysources and superkingdoms
    set_librarysource = set()
    set_superkingdom = set()
    
    for file_name in output_files.keys():
        # xxx_librarysource_superkingdom.tsv
        fields = file_name.strip(".tsv").split("_")
        set_librarysource.add(fields[-2])
        set_superkingdom.add(fields[-1])
    print(f"Distinct library sources {set_librarysource}")
    print(f"Distinct superkingdoms {set_superkingdom}")

def main():
    import sys

    # Check if correct number of arguments are provided
    if len(sys.argv) != 5:
        print("Usage: python script.py sra_XXX_acc_librarysource_mbases_tax_id_total_count sra_XXX_public.tsv pub-u.acc.txt dynamodb_tigs_stats.csv")
        print("wget https://serratus-rayan.s3.amazonaws.com/kmindex/sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv")
        print("wget https://serratus-rayan.s3.amazonaws.com/kmindex/sra_09042024_public.tsv")
        print("aws s3 cp s3://serratus-rayan/tmp/pub-u.acc.txt . --no-sign-request")
        print("aws s3 cp s3://serratus-rayan/tmp/dynamodb_tigs_stats.csv . --no-sign-request")
        print("Also Requires uncompressed files from wget https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz in the current working dir")
        return
    
    input_file = sys.argv[1] # accession -> library and most probable taxids
    public_file = sys.argv[2] # public accession (avoid to deal with private accessions)
    logan_dispo = sys.argv[3] # files indeed in the logan directory
    logan_stats = sys.argv[4] # accession -> size of the unitig file
    taxid_superkingdom = index_superkingdom()
    
    print(f"Indexing accessions from {public_file}")
    to_index_accessions = get_accessions(public_file)
    
    print(f"Indexing accessions from {logan_stats}")
    limited_accessions = get_accessions(logan_stats)
    
    print(f"Compute intersection")
    to_index_accessions = limited_accessions.intersection(to_index_accessions)
    

    
    del limited_accessions
    gc.collect()
    
    print(f"Indexing accessions from {logan_dispo}")
    limited_accessions = get_accessions(logan_dispo)
    
    print(f"Compute 2nd intersection")
    to_index_accessions = limited_accessions.intersection(to_index_accessions)
    

    
    del limited_accessions
    gc.collect()
    
    
    print(f"Create sub lists")
    process_file(input_file, taxid_superkingdom, to_index_accessions, public_file, logan_stats, logan_dispo)


if __name__ == "__main__":
    main()

