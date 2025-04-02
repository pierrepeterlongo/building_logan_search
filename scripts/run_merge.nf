#!/usr/bin/env nextflow



params.blob_config = """
logging:
    type: syslog
    level: log_debug

components:
  - libfuse
  - block_cache
  - attr_cache
  - azstorage

libfuse:
  attribute-expiration-sec: 120
  entry-expiration-sec: 120
  negative-entry-expiration-sec: 240

block_cache:
  block-size-mb: 32
  mem-size-mb: 4096
  prefetch: 80

attr_cache:
  timeout-sec: 7200

azstorage:
  type: block
  account-name: XXX
  account-key: XXX
  endpoint: XXX
  mode: key
  container: XXX
"""

process mergeIndexes {
    
  container 'tlemane/kmindex:azu' 
  containerOptions '--cap-add=SYS_ADMIN --device=/dev/fuse --security-opt apparmor:unconfined --shm-size=50gb'
  errorStrategy 'ignore'
  memory 64.GB
  tag "merge $pu $params.subindex"
  machineType = "Standard_D*d_v5" 
  
  input:
    tuple val(pu), val(to_merge)

  output:
    path "merged_${pu}_${params.subindex}.txt"

  script:
  
  """
  mkdir /tmp/data
  echo "$params.blob_config" > ./config.yaml
  blobfuse2 mount /tmp/data/ --config-file ./config.yaml --tmp-path=/mnt/resource/blobfusetmp2 --default-working-dir /tmp 
  index_location=.
  original_index=.

  if [ -z "$params.subindex" ]; then
    subindex=""
  else
    subindex="_$params.subindex"
  fi

  cmd="kmindex merge -i \${index_location}/\${original_index}_${pu} -n pow_${pu}\${subindex} -m ${to_merge} -p \${index_location}/merged_index_${pu}\${subindex} -t 8"
  echo \$cmd
  \$cmd

  sync
  sleep 120 ## check md on local and blob. 

  touch merged_${pu}_${params.subindex}.txt
  """    
}


workflow {

    list_indexes = file(params.list_indexes)

    // for each possible nb of kmers 
    ch_pu = Channel.from(1..45)

    // reads the list file and finds lines matching the pattern for each pu. It collects and joins these values into a comma-separated string.
    ch_tomerge = ch_pu.map { pu ->
        def to_merge = list_indexes.text.split('\n')
                                .findAll { it =~ /^[0-9]+_${pu}\b/ }
                                .collect { it.split(' ')[0] }
                                .join(',')
        return [pu, to_merge]
    }

    // Filters out entries where to_merge is empty or does not contain a comma (i.e., only one group).
    ch_tomerge.filter { it[1] }.filter { it[1].contains(',') }.set { ch_filtered }
    

    // run the merge
    ch_filtered | mergeIndexes | view { it }
}
