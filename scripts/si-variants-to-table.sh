#!/bin/bash

# ------------------------------------------------------------------- #
# This script parses somatic indel detector vcf output and makes it 
# into a tab-delimited file for annovar's filtering and annotation 
# ------------------------------------------------------------------- #

# Input: 
# $1 - somatic indel dectector path
# $2 - somatic indel detector sample name

# --------------------------------------#
# Define the path to the required tools
# --------------------------------------#

echo "*** parsing somatic indel detector vcf output to tab delimited ***"
source path_file.sh # path to the $SNPEFF, $ANNOVAR0

# Make a temproary directory in $1 if it does not exists
TMP_DIR=$1/tmp

if [ -d "$TMP_DIR" ]; then
	rm -rf "$TMP_DIR"
	mkdir $1/tmp
else 
	mkdir $1/tmp
fi

# Define the working directory
WORK_DIR=$1/tmp

# Extract only somatic indels using SNPSIFT
cat $1/SI-$2.vcf | java -jar "$SNPEFF" filter "(exists SOMATIC)" > "$WORK_DIR"/$2-SOMATIC.vcf

# Convert the variants in the vcf format to tab delimited format using annovar
"$ANNOVAR0" --format vcf4 "$WORK_DIR"/$2-SOMATIC.vcf --includeinfo --outfile "$WORK_DIR"/$2.tmp1

# Retain only unique mutations. First cut chromosome and the position
cut -f 1 "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/chr
cut -f 2 "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/pos
# The mutation is identified by chr and pos and hence paste them together
paste -d ":" "$WORK_DIR"/chr "$WORK_DIR"/pos > "$WORK_DIR"/chr-pos
# Paste chr:pos into the variants table
paste "$WORK_DIR"/chr-pos "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/$2.tmp1.chr.pos
# Sort by the first position and retain only unique entries (specified by -u)
sort -u -k1,1 "$WORK_DIR"/$2.tmp1.chr.pos > "$WORK_DIR"/$2.tmp1.uniq
# Remove the first column as it is not required
cut -f 2- "$WORK_DIR"/$2.tmp1.uniq > "$WORK_DIR"/$2.tmp1

# Cut the entries that are required for annotation
cut -f 1-5 "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/chr-pos-pos-ref-alt
cut -f 17 "$WORK_DIR"/$2.tmp1 | cut -f 3 -d ":" > "$WORK_DIR"/normal-dp 
cut -f 17 "$WORK_DIR"/$2.tmp1 | cut -f 2 -d ":" | cut -f 2 -d "," > "$WORK_DIR"/normal-ad
cut -f 17 "$WORK_DIR"/$2.tmp1 | cut -f 5 -d ":" | cut -f 2 -d "," > "$WORK_DIR"/normal-mqs 
cut -f 18 "$WORK_DIR"/$2.tmp1 | cut -f 3 -d ":" > "$WORK_DIR"/tumor-dp
cut -f 18 "$WORK_DIR"/$2.tmp1 | cut -f 2 -d ":" | cut -f 1 -d "," > "$WORK_DIR"/tumor-ad
cut -f 18 "$WORK_DIR"/$2.tmp1 | cut -f 5 -d ":" | cut -f 1 -d "," > "$WORK_DIR"/tumor-mqs

# Paste the entries into a file
paste "$WORK_DIR"/chr-pos-pos-ref-alt \
      "$WORK_DIR"/normal-dp \
      "$WORK_DIR"/tumor-dp \
      "$WORK_DIR"/normal-ad \
      "$WORK_DIR"/tumor-ad \
      "$WORK_DIR"/tumor-mqs > "$WORK_DIR"/$2.tmp2

# Delete the intermediary files
rm -rf "$WORK_DIR"/chr \
       "$WORK_DIR"/pos \
       "$WORK_DIR"/chr-pos \
       "$WORK_DIR"/$2.tmp1.chr.pos \
       "$WORK_DIR"/$2.tmp1.uniq \
       "$WORK_DIR"/chr-pos-pos-ref-alt \
       "$WORK_DIR"/normal-dp \
       "$WORK_DIR"/tumor-dp \
       "$WORK_DIR"/normal-ad \
       "$WORK_DIR"/tumor-ad \
       "$WORK_DIR"/normal-mqs \
       "$WORK_DIR"/tumor-mqs \
       "$WORK_DIR"/tmp0 \
       "$WORK_DIR"/$2.tmp1 \
       "$WORK_DIR"/$2-SOMATIC.vcf \
       "$WORK_DIR"/$2-SOMATIC.vcf.idx	

