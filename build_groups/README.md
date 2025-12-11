
# Building Logan Search Groups

This is how we created the groups used in Logan search.

> **Note**: The group divisions are based on the STAT annotation. For each accession up to three distinct taxonomic IDs are proposed. We chose the first of them, that is the one corresponding to the most probable.

## 1. Get the Link to Data

```bash
mkdir unitigs_logan 
cd unitigs_logan

# List of public accessions
aws s3 cp s3://serratus-rayan/kmindex/sra_09042024_public.tsv . --no-sign-request
#or
#wget https://serratus-rayan.s3.amazonaws.com/kmindex/sra_09042024_public.tsv

# Download SRA metadata from logan
wget https://serratus-rayan.s3.amazonaws.com/kmindex/sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv

# Data for which we have stats
aws s3 cp s3://serratus-rayan/tmp/dynamodb_tigs_stats.csv . --no-sign-request

# Link from tax_id to superkingdom
wget https://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
tar -xzf taxdump.tar.gz  # decompress

# Accessions available on Logan: 
s5cmd --no-sign-request ls s3://logan-pub/u/* | awk '{print $4}' | cut -d '/' -f 1 > pub_u.txt

# Concrete list from all Logan unitig files
aws s3 cp s3://serratus-rayan/tmp/pub-u.acc.txt . --no-sign-request
```

## 2. Prepare the data

```bash 
# Get data for which one has metadata
python3 compare_identifiers.py sra_09042024_public.tsv sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv     
```

**Obtained output:**
```
First from sra_09042024_public.tsv not found in sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv: SRR19123670
Entries from sra_09042024_public.tsv not found in sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv:
 - Number: 3,536,185 (among 29,085,077)
 - Percentage among sra_09042024_public.tsv: 12%
```

```bash
# Check data coverage in Logan unitigs (in dynamodb_tigs_stats)
python3 compare_identifiers.py sra_09042024_public.tsv dynamodb_tigs_stats.csv 
```

**Obtained output:**
```
First from sra_09042024_public.tsv not found in dynamodb_tigs_stats.csv: SRR24073558
Entries from sra_09042024_public.tsv not found in dynamodb_tigs_stats.csv:
 - Number: 2,306,520 (among 29,085,077)
 - Percentage among sra_09042024_public.tsv: 8%
```

```bash
# Calculate cumulative size of missing data
python3 comp_and_size.py dynamodb_tigs_stats.csv sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv sra_09042024_public.tsv
```

**Obtained output:**
```
 - Number: 3,294,131 (among 26,857,911)
 - Percentage among dynamodb_tigs_stats.csv: 12.27%
 - Sum size not found: 3,175,529,706 (among 54,789,149,329 mbases)
   - This is 5.8% of SRA
   - Size data from sra_09042024_public.tsv
```

## 3. Generate Groups

```bash
python3 filter_and_spread_taxo.py \
    sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv \
    sra_09042024_public.tsv \
    pub-u.acc.txt \
    dynamodb_tigs_stats.csv
```

**Obtained output:**
```
Done. I treated 25,549,078 distinct accessions from file sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv
Among them, 2,144,423 accessions are discarded (8.39%) either because they are not in sra_09042024_public.tsv or dynamodb_tigs_stats.csv or pub-u.acc.txt.
Among the 23,404,655 remaining, 77,070 have no superkingdom (0.33%). They are in sra_09042024_acc_librarysource_mbases_tax_id_total_count.tsv, but not in nodes.dmp

Distinct library sources: {'TRANSCRIPTOMICSINGLECELL', 'GENOMIC', 'OTHER', 'VIRALRNA', 'METAGENOMIC', 'GENOMICSINGLECELL', 'TRANSCRIPTOMIC', 'METATRANSCRIPTOMIC', 'SYNTHETIC'}

Distinct superkingdoms: {'VRT', 'MAM', 'VRL', 'UNKNOWN', 'BCT', 'MICE', 'ROD', 'HUMAN', 'ENV', 'PRI', 'INV', 'PHG', 'PLN'}
```

## 4. Generate File-of-Files (FOFs)

Generates FOF directories in `fof_dir`:

```bash
sh make_all_fofs.sh
```

This creates organized file lists for each combination of library source and superkingdom for efficient batch processing.
