#!/bin/bash

echo "*** calling Unified Genotyper with intervals ***"
source path_file.sh	# includes path to the reference genome $REF and the $GATK path

if [ $6 -eg RECALIBRATE ]
	then

	"$JAVA" -Xmx8g -jar "$GATK" \
				-R "$REF" \
				-rf BadCigar \
				-T UnifiedGenotyper \
				-I:normal $1/out.recal.quality.bam \
				-I:tumor $2/out.recal.quality.bam \
				-o $3/SI-$4.vcf \
				-stand_call_conf 50.0 \
				-stand_emit_conf 10.0 \
				-dcov 200 \
				-mbq 17 \
				-nda \
				-glm BOTH \
				-pairHMM VECTOR_LOGLESS_CACHING
				-L $5

else

	"$JAVA" -Xmx8g -jar "$GATK" \
				-R "$REF" \
				-rf BadCigar \
				-T UnifiedGenotyper \
				-I:normal $1/out.nonrecal.quality.bam \
				-I:tumor $2/out.nonrecal.quality.bam \
				-o $3/SI-$4.vcf \
				-stand_call_conf 50.0 \
				-stand_emit_conf 10.0 \
				-dcov 200 \
				-mbq 17 \
				-nda \
				-glm BOTH \
				-pairHMM VECTOR_LOGLESS_CACHING
				-L $5

fi