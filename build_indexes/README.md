# build indexes from logan data


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
    done

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


    
    ##### Run kmtricks

    # kmtricks_input_file is <INDEX_ID>_<BF_SIZE>.fof
    echo "log_bf_size " ${log_bf_size} " real_bf_size " ${real_bf_size} " nb_threads " ${nb_threads}
    cmd="kmtricks pipeline --file ${index}                           \
                      --run-dir ${out_index_name}               \
                      --bloom-size ${real_bf_size}             \
                      --kmer-size 25                            \
                      --mode hash:bf:bin                        \
                      --hard-min 1                              \
                      --nb-partitions 256                       \
                      --cpr                                     \
                      --threads ${nb_threads}			            \
                      --verbose error                           \
                      --repart-from ${zero_dir_group}/repartition_gatb/repartition.minimRepart"
    echo $cmd
    $cmd 

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


### 5. merge matrices
Run register/merge/register:
```bash
  
if sudo [ -d index ]; then
  echo "WARNING a previous registered index existed in index" >&2
  echo "I remove it"
  sudo rm -rf index
fi

echo "\t Prepare a list to register by size"
cmd="sudo python3  scripts/path_maker.py  --parent-directory . --root-dir ."
echo $cmd  > list.txt
$cmd > list.txt
if [ $? -ne 0 ]; then
  echo "Creation of the list for registering failed"
fi

echo "\t Register by size"
cmd="sh scripts/register_per_size.sh -i . -f list.txt"
echo $cmd
$cmd
if [ $? -ne 0 ]; then
  echo "Register by size failed"
fi

echo "\t Merge by sizes"
cmd="nextflow -log log_merge_${now} run scripts/run_merge.nf -w . --list_indexes list.txt"
echo $cmd
$cmd
if [ $? -ne 0 ]; then
  echo "Merge by sizes failed"
fi


echo "\t Register merged files in a unique index (few seconds)"
cmd="sh scripts/register_merged.sh -i ."
echo $cmd
$cmd
if [ $? -ne 0 ]; then
  echo "Register merged files failed"
  exit 1
fi

```

### 7. clean matrices
Make a script for cleaning the merged matrices. Please lool at script "clean_merged_indexes.py" for an example on the logan data



## Perform a query
```bash
kmindex query -i index -q query.fa -o output_query -z 5 -r 0.1
