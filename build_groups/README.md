
This is how we created the groups used in logan search. 

- Note: the group divisions are based on the STAT annotation. For each accession up to three distinct taxonomic ids are proposed. We chose the first of them, that is the one corresponding to the most probable. 

### 1. get the link to data
```bash
mkdir unitigs_logan 
cd unitigs_logan
wget https://serratus-rayan.s3.amazonaws.com/kmindex/sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv # DO NOT USE ALL (Contains Private accessions)

# Data for which we have stats
aws s3 cp s3://serratus-rayan/tmp/dynamodb_tigs_stats.csv . --no-sign-request

# Public data 
wget https://serratus-rayan.s3.amazonaws.com/kmindex/sra_09042024_public.tsv

# Link from tax_id to superkingdom
wget https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz (+decompress)

# Accessions dispo on logan: 
s5cmd --no-sign-request ls s3://logan-pub/u/* | awk '{print $4}' | cut -d '/' -f 1 > pub_u.txt

# concrete ls made by Rayan
aws s3 cp s3://serratus-rayan/tmp/pub-u.acc.txt . --no-sign-request
```

#### Validation and stats: 
```bash 
# Public data not in sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv

python3 compare_identifiers.py sra_09042024_public.tsv sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv     

First from sra_09042024_public.tsv not found in sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv: SRR19123670
Entries from sra_09042024_public.tsv not found in sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv:

 - Number: 3536185 (among 29085077)
 - Percentage among  sra_09042024_public.tsv: 12%

# Public data not in logan unitigs (in dynamodb_tigs_stats)

python3 compare_identifiers.py sra_09042024_public.tsv dynamodb_tigs_stats.csv 

First from sra_09042024_public.tsv not found in dynamodb_tigs_stats.csv: SRR24073558
Entries from sra_09042024_public.tsv not found in dynamodb_tigs_stats.csv:
 - Number: 2306520 (among 29085077)
 - Percentage among  sra_09042024_public.tsv: 8 %

# Cumulative size of data from dynamodb_tigs_stats.csv not found in sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv:

python3 comp_and_size.py dynamodb_tigs_stats.csv sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv sra_09042024_public.tsv
- Number: 3294131 (among 26857911)
 - Percentage among dynamodb_tigs_stats.csv: 12.27 %
 - Sum size not found: 3175529706 (among 54789149329 mbases)
  - This is 5.8 % of sra
  - size got from sra_09042024_public.tsv
```

### 2. Generate groups: 
```bash
python3 filter_and_spread_taxo.py sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv sra_09042024_public.tsv pub-u.acc.txt  dynamodb_tigs_stats.csv

Done. I treated 25549078 distinct accessions from file sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv
Among them, 2144423 accession are discarded (8.39%) either because they are not in sra_09042024_public.tsv or dynamodb_tigs_stats.csv or pub-u.acc.txt.
Among the 23404655 remaining, 77070 have no superkingdom (0.33%). They are in sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv, but not in nodes.dmp
Distinct library sources {'TRANSCRIPTOMICSINGLECELL', 'GENOMIC', 'OTHER', 'VIRALRNA', 'METAGENOMIC', 'GENOMICSINGLECELL', 'TRANSCRIPTOMIC', 'METATRANSCRIPTOMIC', 'SYNTHETIC'}
Distinct superkingdoms {'VRT', 'MAM', 'VRL', 'UNKNOWN', 'BCT', 'MICE', 'ROD', 'HUMAN', 'ENV', 'PRI', 'INV', 'PHG', 'PLN'}
```

### 3. generate fofs

Generates fof directories in `fof_dir`
```bash
sh make_all_fofs.sh
```