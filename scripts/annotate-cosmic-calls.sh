#!/bin/bash
# This script will annotate the cosmic calls using annovar
# $1 cosmic directory name
# $2 sample name

# Annovar annotation and database path
ANNOVAR_PATH=/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar/annotate_variation.pl 
ANNOVAR_DB=/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar/humandb/

# Extract only the columns that annovar accepts for annotating
cut -f 3- $1/$2.hg19_cosmic64_dropped > $1/tmp
"$ANNOVAR_PATH" -buildver hg19 -dbtype gene $1/tmp "$ANNOVAR_DB"

# Clean the genenames in the exonic list
cut -f 3 $1/tmp.exonic_variant_function | cut -f 1 -d ":" | cut -f 1 -d "(" | cut -f 1 -d ";" | cut -f 1 -d "," > $1/tmp.genenames
paste $1/tmp.genenames $1/tmp.exonic_variant_function > $1/$2-cosmic.exonic
mv $1/tmp.variant_function $1/$2-cosmic.variants

rm -rf 	$1/tmp \
	$1/tmp.exonic_variant_function \
	$1/tmp.variant_function \
	$1/tmp.log \
	$1/tmp.genenames \
	$1/$2.log
