
#!/bin/bash


# Help message function
display_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -i <indexdirectory>  Index location containing the kmindex files"
    echo "  -h                   Display this help message"
    echo "Example: $0 -i index"
    exit 1
}


# Parse command-line arguments
while getopts ":ri:h" opt; do
  case ${opt} in
    l )
      base_dir="$OPTARG"
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

# Check if library and superkingdom are provided
if [ -z "$index" ]; then
  echo "Error: 'index' option mandatory." >&2
  display_help
fi




### First checks if a merged_index exists.
### In this case, register directly the merged index in the main index
for logsize in $(seq 1 45); do
    dir_path="$base_dir/merged_index_${logsize}"

    if ls -l "${dir_path}" >/dev/null 2>&1 ; then # a subsplit exists
          cmd="kmindex register -i ${base_dir} -n ${logsize} -p ${dir_path}"
          echo $cmd
          $cmd
      fi 

    subsplitid=0
    while true; do  # walk all subsplits
      if ls -l "${dir_path}_${subsplitid}" >/dev/null 2>&1 ; then # a subsplit exists
          cmd="kmindex register -i ${base_dir} -n ${logsize}_${subsplitid} -p ${dir_path}_${subsplitid}"
          echo $cmd
          $cmd
      else
          break # no more sub splits
      fi 
      subsplitid=$((subsplitid+1))
    done # end each subsplit
done


# Then the rest (non merged directories)
# for each log value, the dir path ($base_dir/index_${logsize}) contains either
# - nothing : this log value was not among indexed data
# - a 0_logsize symb link (a link to a non merged index)
# - a pow_logsize symb link (a link to a merged index)
# - a pow_logsize_subsplit_id link ((a link to a submerged index)
for logsize in $(seq 1 45); do
    # if size already registered previously, continue
    if ls $base_dir/index_${logsize}_* >/dev/null 2>&1; then
      continue
    fi

    # Construct the directory path
    dir_path="$base_dir/index_${logsize}"
    if ls "$dir_path" >/dev/null 2>&1; then
        # get the symbolic link eg 
        # 0_3 -> 84/12a975835aae435078c2e620d88a79/0_3/ if unmerged (only 0s)
        # or
        # pow_31 -> merged_index_31 (if merged 0s and others)
        # or
        # pow_31_0 -> merged_index_31.0 (if merged 0s and others and if the merge was splitted into several sub matrices)

      if ls -l "${dir_path}/0_${logsize}" >/dev/null 2>&1 ; then # not merged 
              full_link=$( sudo ls -l "${dir_path}/0_${logsize}" ) 
              symb_link=`echo ${full_link} | cut -d ">" -f 2`
              # echo "registering " ${logsize} " from " ${symb_link}
              cmd="kmindex register -i ${base_dir}/index -n ${logsize} -p ${symb_link}"
              echo $cmd
              $cmd
      else # merged
          if ls -l "${dir_path}/pow_${logsize}" >/dev/null 2>&1 ; then # no sub split
              full_link=$( ls -l "${dir_path}/pow_${logsize}" )
              symb_link=`echo ${full_link} | cut -d ">" -f 2`
              # echo "registering " ${logsize} " from " ${symb_link}
              cmd="kmindex register -i ${base_dir}/index -n ${logsize} -p ${symb_link}"
              echo $cmd
              $cmd
          else  # with sub split
            subsplitid=0
            while true; do  # walk all subsplits
                if ls -l "${dir_path}/pow_${logsize}_${subsplitid}" >/dev/null 2>&1 ; then # a subsplit exists
                    full_link=$( ls -l "${dir_path}/pow_${logsize}_${subsplitid}" )
                    symb_link=`echo ${full_link} | cut -d ">" -f 2`
                    # echo "registering " ${logsize} " from " ${symb_link}
                    cmd="kmindex register -i ${base_dir}/index -n ${logsize}_${subsplitid} -p ${symb_link}"
                    echo $cmd
                    $cmd

                else
                    break # no more sub splits
                fi 
              subsplitid=$((subsplitid+1))
            done # end each subsplit
            # also check the "null" suffix: 
            if ls -l "${dir_path}/pow_${logsize}_null" >/dev/null 2>&1 ; then # a subsplit exists
              full_link=$( sudo ls -l "${dir_path}/pow_${logsize}_null" )
              symb_link=`echo ${full_link} | cut -d ">" -f 2`
              # echo "registering " ${logsize} " from " ${symb_link}
              cmd="kmindex register -i ${base_dir}/index -n ${logsize}_null -p ${symb_link}"
              echo $cmd
              $cmd
            fi
        fi # end with sub split
      fi # end merged
    fi # end all sub paths tested
done

# remove now useless old registered indexes
#rm -r /tmp/data/${library}_${superkingdom}/index_${library}_${superkingdom}_* 

echo "Registering of final indexes (merged or not) is over. It is located in directory index_${library}_${superkingdom}"