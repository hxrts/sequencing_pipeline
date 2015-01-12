#!/bin/bash

echo "*** calling Unified Genotyper ***"
source path_file.sh	# includes path to the reference genome $REF and the $GATK path

/usr/lib/jvm/java-6-openjdk-amd64/jre/bin/java -Xmx2g -jar "$GATK" -T UnifiedGenotyper \
								   -R "$REF" \
								   -rf BadCigar \
								   -filterMBQ \
								   -glm BOTH \
								   -I $1/out.recal.quality.bam \
								   -I $2/out.recal.quality.bam \
								   --out $3/UG-$4.vcf \
								   -stand_call_conf 50.0 \
								   -stand_emit_conf 10.0 \
								   -dcov 50
