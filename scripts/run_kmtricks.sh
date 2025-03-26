#!/bin/bash

# Help message function
display_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -r               Enable resume mode"
    echo "  -f               Run kmtricks on first groups"
    echo "  -o               Run kmtricks on other groups"
    echo "  -m               Register per size and merge and registered indexes (needs -o option)"
    echo "  -h               Display this help message"
    exit 1
}

# Set default values
resume=false
firsts=false
others=false
merge=false
kmer_size=25
resume_cmd=""
root_fof_dir=""
dir=$(echo $(cd $(dirname $0); pwd);) # script location

# Parse command-line arguments
while getopts ":rfomh" opt; do
  case ${opt} in
    r )
      resume=true
      resume_cmd="-resume"
      ;;
    f )
      firsts=true
      ;;
    o )
      others=true
      ;;
    m )
      merge=true
      ;;
    h )
      display_help
      ;;
    \? )
      echo "Invalid option: $OPTARG" 1>&2
      display_help
      ;;
    : )
      echo "Option -$OPTARG requires an argument." 1>&2
      display_help
      ;;
  esac
done
shift $((OPTIND -1))

# Check if both firsts and others are false
if [ "$firsts" = false ] && [ "$others" = false ]; then
    echo "    WARNING: Firsts and others are false. Nothing to do"
    exit 0
fi

fof_directory="/tmp/FOF/"
if sudo [ ! -d ${fof_dir} ]; then
  echo "WARNING: Directory ${fof_dir} does not exist. I create it." >&2
  sudo mkdir -p ${fof_dir}
fi

log_dir="/tmp/logs/"
if sudo [ ! -d ${log_dir} ]; then
  echo "WARNING: Directory ${log_dir} does not exist. I create it." >&2
  sudo mkdir -p ${log_dir}
fi


now=$(date +"%Y_%m_%d_%H_%M_%S")


# Run 0s: 
if [ "$firsts" = true ]; then 
  echo "run first groups"
  cmd="nextflow -log log_0s_${now} run $dir/run0s.nf -w ${fof_directory}  ${resume_cmd} -name run_0s_${now}"
  echo $cmd
  $cmd
  cmd="sudo mv log_0s_${now} ${log_dir}"
  echo $cmd
  $cmd
  
  sudo python3  $dir/path_maker.py  --parent-directory /tmp/data/${library}_${superkingdom} --only-0s > runid_to_hash.txt
  echo "replace ${fof_dir}${library}_${superkingdom}/runid_to_hash.txt"
  sudo mv runid_to_hash.txt ${fof_dir}${library}_${superkingdom}/; 
fi


# Run others:
if [ "$others" = true ]; then
  echo "run other groups"
  cmd="nextflow -log log_${library}_${superkingdom}_others_${now} run $dir/run_others.nf -w az://indextheplanet/${library}_${superkingdom} --libking ${library}_${superkingdom} ${resume_cmd} -name run_${library}_${superkingdom}_others_${now}"
  echo $cmd
  $cmd
  cmd="sudo mv log_${library}_${superkingdom}_others_${now} ${log_dir}"
  echo $cmd
  $cmd
fi


# Run register/merge/register:
if [ "$merge" = true ]; then
    
  if sudo [ -d /tmp/data/${library}_${superkingdom}/index_${library}_${superkingdom} ]; then
    echo "WARNING a previous registered index existed in /tmp/data/${library}_${superkingdom}/index_${library}_${superkingdom}" >&2
    echo "I remove it"
    sudo rm -rf /tmp/data/${library}_${superkingdom}/index_${library}_${superkingdom}
  fi

  echo "\t Prepare a list to register by size"
  cmd="sudo python3  $dir/path_maker.py  --parent-directory /tmp/data/${library}_${superkingdom} --root-dir /tmp/data/${library}_${superkingdom}/"
  echo $cmd  > list_${library}_${superkingdom}.txt
  $cmd > list_${library}_${superkingdom}.txt
  if [ $? -ne 0 ]; then
    echo "Creation of the list for registering failed"
    exit 1
  fi
  
  echo "\t Register by size"
  cmd="sh scripts/register_per_size.sh -l ${library} -s ${superkingdom} -f list_${library}_${superkingdom}.txt"
  echo $cmd
  $cmd
  if [ $? -ne 0 ]; then
    echo "Register by size failed"
  fi
  
  echo "\t Merge by sizes"
  cmd="nextflow -log log_${library}_${superkingdom}_merge_${now} run scripts/run_merge.nf -w az://indextheplanet/${library}_${superkingdom} --list_indexes list_${library}_${superkingdom}.txt --libking ${library}_${superkingdom}"
  echo $cmd
  $cmd
  if [ $? -ne 0 ]; then
    echo "Merge by sizes failed"
    exit 1
  fi

  cmd="sudo mv log_${library}_${superkingdom}_merge_${now} ${log_dir}"
  echo $cmd
  $cmd
  if [ $? -ne 0 ]; then
    echo "Moving logs failed"
    exit 1
  fi
  
  cmd="rm -f list_${library}_${superkingdom}.txt"
  echo $cmd
  $cmd

  echo "\t Register merged files in a unique index (few seconds)"
  cmd="sh scripts/register_merged.sh -l ${library} -s ${superkingdom}"
  echo $cmd
  $cmd
  if [ $? -ne 0 ]; then
    echo "Register merged files failed"
    exit 1
  fi

  echo "\t Validate merged files"
  cmd="sudo python3 scripts/validate_merge.py /tmp/data/${library}_${superkingdom}"
  echo $cmd 
  $cmd
  if [ $? -ne 0 ]; then
    echo "Merged files validation failed"
    exit 1
  fi
fi
exit 0
