#!/bin/bash

echo "*** calling muTect with intervals ***"
source path_file.sh	# path to muTect

if [ $6 -eg RECALIBRATE ]
	then

	"$JAVA" -Xmx2g -jar "$MUTECT" -T MuTect \
								-R "$REF" \
								-rf BadCigar \
								-filterMBQ \
								--dbsnp "$DBSNPVCF" \
								--cosmic "$COSMICVCF" \
								--input_file:tumor $1/out.recal.quality.bam \
								--input_file:normal $2/out.recal.quality.bam \
								--out $3/MU-$4.txt \
								-L $5

else

	"$JAVA" -Xmx2g -jar "$MUTECT" -T MuTect \
								-R "$REF" \
								-rf BadCigar \
								-filterMBQ \
								--dbsnp "$DBSNPVCF" \
								--cosmic "$COSMICVCF" \
								--input_file:tumor $1/out.nonrecal.quality.bam \
								--input_file:normal $2/out.nonrecal.quality.bam \
								--out $3/MU-$4.txt \
								-L $5

fi