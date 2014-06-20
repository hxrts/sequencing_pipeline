# ------------------------------------------------------------------- #
# This script parses mutect txt output and makes it 
# into a tab-delimited file for annovar's filtering and annotation 
# ------------------------------------------------------------------- #
# Input: 
# $1 - mutect path
# $2 - mutect sample name

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

# Extract only somatic mutations using REJECT/KEEP status given in mutect
grep -v REJECT $1/MU-$2.txt > "$WORK_DIR"/$2-SOMATIC


# Remove the header by deleting the first line
more +3 "$WORK_DIR"/$2-SOMATIC > "$WORK_DIR"/tmp0
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
cut -f 4-5 "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/ref-alt
awk '{print $31 + $32}' "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/normal-dp
awk '{print $21 + $22}' "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/tumor-dp
cut -f 31 "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/normal-ad
cut -f 22 "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/tumor-ad
cut -f 17 "$WORK_DIR"/$2.tmp1 > "$WORK_DIR"/tumor-lod-fstar 

# Paste the entries into a file
paste "$WORK_DIR"/chr \
      "$WORK_DIR"/pos \
      "$WORK_DIR"/pos \
      "$WORK_DIR"/ref-alt \
      "$WORK_DIR"/normal-dp \
      "$WORK_DIR"/tumor-dp \
      "$WORK_DIR"/normal-ad \
      "$WORK_DIR"/tumor-ad \
      "$WORK_DIR"/tumor-lod-fstar > "$WORK_DIR"/$2.tmp2

# Delete the intermediary files
rm -rf "$WORK_DIR"/chr \
       "$WORK_DIR"/pos \
       "$WORK_DIR"/chr-pos \
       "$WORK_DIR"/ref-alt \
       "$WORK_DIR"/$2.tmp1.chr.pos \
       "$WORK_DIR"/$2.tmp1.uniq \
       "$WORK_DIR"/normal-dp \
       "$WORK_DIR"/tumor-dp \
       "$WORK_DIR"/normal-ad \
       "$WORK_DIR"/tumor-ad \
       "$WORK_DIR"/tumor-lod-fstar \
       "$WORK_DIR"/tmp0 \
       "$WORK_DIR"/$2.tmp1 \
       "$WORK_DIR"/$2-SOMATIC
