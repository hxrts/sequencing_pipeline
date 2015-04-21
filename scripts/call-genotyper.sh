#!/bin/bash

echo "*** calling Unified Genotyper ***"
source path_file.sh	# includes path to the reference genome $REF and the $GATK path

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