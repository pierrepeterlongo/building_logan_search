
dir=$(echo $(cd $(dirname $0); pwd);) # script location

mkdir "fof_dir"
fof_dir="fof_dir"
if [ ! -d ${fof_dir} ]; then
  echo "WARNING: Directory ${fof_dir} does not exist. I create it." >&2
  mkdir -p ${fof_dir}
fi

mkdir log_dir
# Create the log directory
log_dir="log_dir"
if [ ! -d ${log_dir} ]; then
  echo "WARNING: Directory ${log_dir} does not exist. I create it." >&2
  mkdir -p ${log_dir}
fi

kmer_size=25
for fof in `ls -Sr sra_09042024_acc_librarysource_mbases_tax_id_total_count_*` ; do 
  library=`echo $fof | cut -d "_" -f 10 | cut -d "." -f 1`;
  superkingdom=`echo $fof | cut -d "_" -f 11 | cut -d "." -f 1`;
  fof_directory="${fof_dir}${library}_${superkingdom}"
  echo fofing $library $superkingdom
  python3 $dir/create_fof.py sra_09042024_acc_librarysource_mbases_tax_id_total_count_${library}_${superkingdom}.tsv ${fof_directory} ${kmer_size} > log_fof_${library}_${superkingdom}.txt
	
done

sudo mv log_fof_* $log_dir 