#!/bin/bash

# ------------------------------------------------------------------- #
# This script parses somatic sniper's vcf output and makes it
# into a tab-delimited file for annovar's filtering and annotation
# ------------------------------------------------------------------- #

# Input:
# $1 - somatic sniper path
# $2 - somatic sniper sample name

# --------------------------------------#
# Define the path to the required tools
# --------------------------------------#

echo "*** parsing somatic sniper's vcf output to tab delimited ***"
source path_file.sh # path to $GATK, $REF

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

# Convert the variants in the vcf format to tab delimited format
java -Xmx2g -jar "$GATK" -T VariantsToTable \
			 -R "$REF" \
			 -V $1/SS-$2.vcf \
			 -F CHROM -F POS -F POS -F REF -F ALT \
			 -GF DP -GF BCOUNT -GF SSC \
			 -AMD \
			 -o "$WORK_DIR"/$2.tmp1

# Remove the header by deleting the first line
more +2 "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/tmp0
cp "$WORK_DIR"/tmp0 "$WORK_DIR"/$2.tmp1

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
cut -f 1-3 "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/chr-pos-pos
cut -f 4 "$WORK_DIR"/$2.tmp1 | cut -f 1 -d "," > "$WORK_DIR"/ref
cut -f 5 "$WORK_DIR"/$2.tmp1 | cut -f 1 -d "," > "$WORK_DIR"/alt
cut -f 6 "$WORK_DIR"/$2.tmp1  > "$WORK_DIR"/normal-dp 
cut -f 7 "$WORK_DIR"/$2.tmp1 | cut -f 1 -d "," > "$WORK_DIR"/N-A
cut -f 7 "$WORK_DIR"/$2.tmp1 | cut -f 2 -d "," > "$WORK_DIR"/N-C
cut -f 7 "$WORK_DIR"/$2.tmp1 | cut -f 3 -d "," > "$WORK_DIR"/N-G
cut -f 7 "$WORK_DIR"/$2.tmp1 | cut -f 4 -d "," > "$WORK_DIR"/N-T
cut -f 9 "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/tumor-dp
cut -f 10 "$WORK_DIR"/$2.tmp1 | cut -f 1 -d "," > "$WORK_DIR"/T-A
cut -f 10 "$WORK_DIR"/$2.tmp1 | cut -f 2 -d "," > "$WORK_DIR"/T-C
cut -f 10 "$WORK_DIR"/$2.tmp1 | cut -f 3 -d "," > "$WORK_DIR"/T-G
cut -f 10 "$WORK_DIR"/$2.tmp1 | cut -f 4 -d "," > "$WORK_DIR"/T-T
cut -f 11 "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/tumor-ssc

# Paste the entries into a file
paste "$WORK_DIR"/chr-pos-pos \
      "$WORK_DIR"/ref \
      "$WORK_DIR"/alt \
      "$WORK_DIR"/normal-dp \
      "$WORK_DIR"/tumor-dp \
      "$WORK_DIR"/N-A \
      "$WORK_DIR"/N-C \
      "$WORK_DIR"/N-G \
      "$WORK_DIR"/N-T \
      "$WORK_DIR"/T-A \
      "$WORK_DIR"/T-C \
      "$WORK_DIR"/T-G \
      "$WORK_DIR"/T-T \
      "$WORK_DIR"/tumor-ssc > "$WORK_DIR"/$2.tmp2

# Delete the intermediary files
rm -rf "$WORK_DIR"/chr \
       "$WORK_DIR"/pos \
       "$WORK_DIR"/chr-pos \
       "$WORK_DIR"/$2.tmp1.chr.pos \
       "$WORK_DIR"/$2.tmp1.uniq \
       "$WORK_DIR"/chr-pos-pos \
       "$WORK_DIR"/ref \
       "$WORK_DIR"/alt \
       "$WORK_DIR"/normal-dp \
       "$WORK_DIR"/N-A \
       "$WORK_DIR"/N-C \
       "$WORK_DIR"/N-G \
       "$WORK_DIR"/N-T \
       "$WORK_DIR"/tumor-dp \
       "$WORK_DIR"/T-A \
       "$WORK_DIR"/T-C \
       "$WORK_DIR"/T-G \
       "$WORK_DIR"/T-T \
       "$WORK_DIR"/tumor-ssc \
       "$WORK_DIR"/tmp0 \
       "$WORK_DIR"/$2.tmp1
