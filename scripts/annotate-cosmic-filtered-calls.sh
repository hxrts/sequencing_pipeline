# This script will annotate the cosmic, dbsnp, 1000g and ESP5400 filtered calls using annovar
# $1 directory name
# $2 sample name

# Annovar annotation and database path
ANNOVAR_PATH=/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar/annotate_variation.pl 
ANNOVAR_DB=/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar/humandb/

# Annotate dbsnp filtered calls using refseq
"$ANNOVAR_PATH" -buildver hg19 -dbtype gene $1/$2.hg19_snp132_filtered "$ANNOVAR_DB"

# Clean the genenames in the exonic list
cut -f 3 $1/$2.hg19_snp132_filtered.exonic_variant_function | \
cut -f 1 -d ":" | cut -f 1 -d "(" | cut -f 1 -d ";" | cut -f 1 -d "," > $1/$2.hg19_snp132_filtered.genenames

paste $1/$2.hg19_snp132_filtered.genenames $1/$2.hg19_snp132_filtered.exonic_variant_function > $1/$2-novel.exonic
mv $1/$2.hg19_snp132_filtered.variant_function $1/$2-novel.variants

rm -rf	$1/$2.hg19_snp132_filtered.exonic_variant_function \
	$1/$2.hg19_snp132_filtered.variant_function \
	$1/$2.hg19_snp132_filtered.log \
	$1/$2.hg19_snp132_filtered.genenames \
	$1/$2.log
