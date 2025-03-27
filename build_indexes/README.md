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
1. get data info
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
mkdir fofs
python scripts/create_fof.py logan_infos/indexed_accesssions.txt dynamodb_tigs_stats.csv fofs 25
```
Generates fof directories


### 3. create first matrices 
```bash

export AWS_EC2_METADATA_DISABLED=true

retry() {
  local n=1
  local max=5

  while true; do
    "$@" && return 0 || {
      if [[ $n -lt $max ]]; then
        ((n++))
        echo "Command failed. Attempt $n/$max:"
      else
        echo "The command has failed after $n attempts."
        return 1
      fi
    }
  done
}

ulimit -n 98304
for index in fofs/0s/*.txt;
  do
    cat ${index} | while IFS=': ' read -r sample_identifier full_file_name;
        do
            retry aws s3 cp s3://logan-pub/u/${sample_identifier}/${sample_identifier}.unitigs.fa.zst . --no-sign-request --no-progress || {
                echo "Failed downloading ${sample_identifier}.unitigs.fa.zst" >&2
                zstd < /dev/null > ${sample_identifier}.unitigs.fa.zst
            }
            zstd --test ${sample_identifier}.unitigs.fa.zst || zstd < /dev/null > ${sample_identifier}.unitigs.fa.zst
        done
    index_basename=$(basename ${index})
    log_bf_size=$(echo ${index_basename} | cut -d'_' -f2 | cut -d'.' -f1)
    out_index_name=$(echo ${index_basename} | cut -d'.' -f1)
    nb_threads=32
    if [ "$log_bf_size" -gt 33 ]; then
        nb_threads=16
    fi


    p=0.25
    real_bf_size=$( echo "(-( 2^(${log_bf_size}+1) )* l($p) / l(2)^2) / 1" | bc -l | cut -d "." -f 1 ) 
    
    echo "log_bf_size " ${log_bf_size} " real_bf_size " ${real_bf_size} " nb_threads " ${nb_threads}

    cmd="kmtricks pipeline --file ${index}                    \
                    --run-dir ${out_index_name}               \
                    --bloom-size ${real_bf_size}              \
                    --kmer-size 25                            \
                    --mode hash:bf:bin                        \
                    --hard-min 1                              \
                    --nb-partitions 256                       \
                    --verbose error                           \
                    --cpr                                     \
                    --threads ${nb_threads}"
    echo $cmd
    $cmd || echo "failing to execute kmtricks"
    

    rm -rf ${out_index_name}/fpr \
    ${out_index_name}/filters \
    ${out_index_name}/howde_index \
    ${out_index_name}/merge_infos \
    ${out_index_name}/counts \
    ${out_index_name}/histograms \
    ${out_index_name}/partition_infos \
    ${out_index_name}/superkmers \
    ${out_index_name}/minimizers
  done
```

### 4. create other matrices 
```bash
for index in fofs/others/*.txt;
  do
    cat ${index} | while IFS=': ' read -r sample_identifier full_file_name;
    do
        retry aws s3 cp s3://logan-pub/u/${sample_identifier}/${sample_identifier}.unitigs.fa.zst . --no-sign-request --no-progress || {
            echo "Failed downloading ${sample_identifier}.unitigs.fa.zst" >&2
            zstd < /dev/null > ${sample_identifier}.unitigs.fa.zst
        }
        zstd --test ${sample_identifier}.unitigs.fa.zst || zstd < /dev/null > ${sample_identifier}.unitigs.fa.zst
    done

    log_bf_size=$(echo $(basename ${index}) | cut -d'_' -f2 | cut -d'.' -f1)
    out_index_name=$(echo ${index_basename} | cut -d'.' -f1)
    nb_threads=32
    if [ "$log_bf_size" -gt 33 ]; then
        nb_threads=16
    fi

    p=0.25
    real_bf_size=$( echo "(-( 2^(${log_bf_size}+1) )* l($p) / l(2)^2) / 1" | bc -l | cut -d "." -f 1 ) 


    ### Fetch repartition.minimRepart  
    zero_dir_group=0_${log_bf_size}
    run_dir_hash=$(grep -w ${zero_dir_group} $runid_to_hash |  head -n 1 | cut -d " " -f2)
    # repart_file = channel.fromPath( 'az://indextheplanet/${params.libking}/${run_dir_hash}/${zero_dir_group}/repartition_gatb/repartition.minimRepart' )
    
    echo cp "${repart_address}" "." | xargs azcopy 
 
    
    ##### Run kmtricks

    ulimit -n 98304
    # kmtricks_input_file is <INDEX_ID>_<BF_SIZE>.fof
    echo "log_bf_size " ${log_bf_size} " real_bf_size " ${real_bf_size} " nb_threads " ${nb_threads}
    kmtricks pipeline --file ${index}                           \
                      --run-dir ${out_index_name}               \
                      --bloom-size ${real_bf_size}             \
                      --kmer-size 25                            \
                      --mode hash:bf:bin                        \
                      --hard-min 1                              \
                      --nb-partitions 256                       \
                      --cpr                                     \
                      --threads ${nb_threads}			            \
                      --verbose error                           \
                      --repart-from ${zero_dir_group}/repartition.minimRepart

    ##### Clean the output directory
    rm -rf ${index_basename}/fpr \
    ${index_basename}/filters \
    ${index_basename}/howde_index \
    ${index_basename}/merge_infos \
    ${index_basename}/counts \
    ${index_basename}/histograms \
    ${index_basename}/partition_infos \
    ${index_basename}/superkmers \
    ${index_basename}/minimizers
  done
```
HERE, UNTESTED ON MAC
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
