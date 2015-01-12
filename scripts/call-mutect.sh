#!/bin/bash

echo "*** calling MuTect with intervals ***"
source path_file.sh	# path to MuTect v14, REF, COSMIC, DBSNP

/usr/lib/jvm/java-6-openjdk-amd64/jre/bin/java -Xmx2g -jar "$MUTECT_PATH_VER14" -T MuTect \
										-R "$REF" \
										-rf BadCigar \
										-filterMBQ \
										--input_file:tumor $1/out.recal.quality.bam \
										--input_file:normal $2/out.recal.quality.bam \
										--out $3/MU-$4.txt