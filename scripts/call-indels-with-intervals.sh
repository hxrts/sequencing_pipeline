#!/bin/bash

echo "*** calling indels with intervals ***"
source path_file.sh	# path to the GATK (somatic indel detector) and reference genome

if [ $5 -eg RECALIBRATE ]
	then

	"$JAVA" -Xmx8g -jar "$SomaticIndelDetector" -R "$REF" -T SomaticIndelDetector -mnr 50000  \
								   -minConsensusFraction 0.7 \
								   -minCoverage 6 \
								   -minNormalCoverage 4 \
								   -o $3/SI-$4.vcf \
								   -verbose $3/SI-$4.txt \
								   -I:normal $1/out.recal.quality.bam \
								   -I:tumor $2/out.recal.quality.bam \
								   -L $5 \
								   --validation_strictness SILENT -U

else

	"$JAVA" -Xmx8g -jar "$SomaticIndelDetector" -R "$REF" -T SomaticIndelDetector -mnr 50000  \
								   -minConsensusFraction 0.7 \
								   -minCoverage 6 \
								   -minNormalCoverage 4 \
								   -o $3/SI-$4.vcf \
								   -verbose $3/SI-$4.txt \
								   -I:normal $1/out.nonrecal.quality.bam \
								   -I:tumor $2/out.nonrecal.quality.bam \
								   -L $5 \
								   --validation_strictness SILENT -U

fi