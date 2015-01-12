#!/bin/bash

echo "*** calling indels ***"
source path_file.sh	# path to the GATK (somatic indel detector) and reference genome

java -Xmx8g -jar "$GAT1" -R "$REF" -T SomaticIndelDetector -mnr 50000  \
							   -minConsensusFraction 0.7 \
							   -minCoverage 6 \
							   -minNormalCoverage 4 \
							   -o $3/SI-$4.vcf \
							   -verbose $3/SI-$4.txt \
							   -I:normal $1/out.recal.quality.bam \
							   -I:tumor $2/out.recal.quality.bam \
							   --validation_strictness SILENT -U
