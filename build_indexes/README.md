# build indexes from logan data

## IOs

**IN**

* SRA, nov 2023.
  
  * 43P compressed data,
  * 23,404,547 documents 

**OUT**

* A general index able to detect where (without abundances) a query occurs.


## Full indexing pipeline
Support slides can be found here: https://docs.google.com/presentation/d/1RuqcpMkTfnLv1DmW3Z1mbS5gw9MQhdUOSL5Fcm_3KBg


### Steps:
0. Prepare the VM
1. get the link to data
2. generate groups
3. generate fofs
4. create first matrices for each group
5. create other matrices for each group
6. merge matrices
7. clean matrices


### 1. get data infos
Stats about logan accessions 
```bash
aws s3 cp s3://serratus-rayan/tmp/dynamodb_tigs_stats.csv . --no-sign-request

head -n 3 dynamodb_tigs_stats.csv 
accession,seqstats_unitigs_nbseq,seqstats_unitigs_sumlen
ERR12325358,249,18065
SRR19715583,209594,8266318
```

All indexed logan accessions are in `logan_info` directory

### 2. generate file of files
```bash
# example
python scripts/create_fof.py logan_infos/indexed_accesssions_clean.txt dynamodb_tigs_stats.csv /tmp/ 25
```
Generates fof directories

HERE!!
### 3. create first matrices for each group
```bash
sh scripts/launch_0s_all.sh
```
This script calls `run_kmtricks.sh` with option `-f` (first) for each group that are in directory `0s_to_finish`.
In turn, this scripts calls run0s.nf nexflow script.
Succesful groups are moved to directory `others_to_do`.

### 5. create other matrices for each group
```bash
sh scripts/launch_others.sh
```
This script calls `run_kmtricks.sh` with option `-o` (others) for each group that are in directory `others_to_do`.
In turn, this scripts calls run_others.nf nexflow script.
Succesful groups are moved to directory `to_merge`.

### 6. merge matrices
```bash
sh scripts/launch_merges.sh
```
This script calls `run_kmtricks.sh` with option `-m` (merge) for each group that are in directory `to_merge`.
In turn, this scripts calls run_merge.nf nexflow script.
Succesful groups are moved to directory `merged`.

### 7. clean matrices
```bash
sh scripts/launch_cleans.sh
```
This script calls `clean_merged_indexes.py` for each group that are in directory `merged`.
Succesful groups are moved to directory `cleaned`.



## Perform a query
```bash
mount_point=/tmp/data
GROUP=TRANSCRIPTOMIC_VRT
sudo kmindex query -i ${mount_point}/${GROUP}/index_${GROUP} -q query.fa -o output_query_${GROUP} -z 5 -r 0.1
```
Show best hits: 
```bash
grep -v "{" output_query_${GROUP}/*.json | grep -v "}" | sort -k 3 -gr
or
find . -name "*.json" -type f -size +50c -exec grep -v "\{"  \{\} \; | grep -v "\}" | sort -k 2 -gr | head
```

Validation usint back_to_sequences: 
```bash
accession=SRR14660268
aws s3 cp s3://logan-pub/u/${accession}/${accession}.unitigs.fa.zst . --no-sign-request
zstd -d ${accession}.unitigs.fa.zst
back_to_sequences --in-kmers query_VC-like_18s.fa --in-sequences ${accession}.unitigs.fa --out-sequences out_${accession}_query_VC-like_18s.fa --out-kmers out_${accession}_query_VC-like_18s_kmers.txt -m 5
```

## Query against all groups: 
```bash
for name in `ls -Sr /home/azureuser/kmsra/groups/group_*`; do 
	GROUP=`echo $name | cut -d "." -f 1 | cut -d "_" -f 2,3`; 
	echo $GROUP; 
	sudo ./kmindex query -i ${mount_point}/${GROUP}/index_${GROUP} -q query.fa -o output_query_${GROUP} -z 5 -r 0.4  > log_$GROUP.txt 2>&1 || break
done
```

Find non empty results: 
```bash
find . -name *.json -type f -size +40c -exec ls -l \{} \;
```
