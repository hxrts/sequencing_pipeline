#!/bin/bash
# echo Running Somatic Indel Detector on sample $3 using normal and tumor recalibrated .bam files >> /Applications/MAMP/htdocs/logs/somatic_indel_detector.log
# java -Xmx8g -jar ~/Documents/tools/picard-tools-1.46/AddOrReplaceReadGroups.jar I=$1/out.recal.quality.bam O=$1-readgroup.bam SORT_ORDER=coordinate RGID=1 RGLB=mskcc RGPL=illumina RGPU=1 RGSM=$1 CREATE_INDEX=True VALIDATION_STRINGENCY=SILENT
# java -Xmx8g -jar ~/Documents/tools/picard-tools-1.46/AddOrReplaceReadGroups.jar I=$2/out.recal.quality.bam O=$2-readgroup.bam SORT_ORDER=coordinate RGID=1 RGLB=mskcc RGPL=illumina RGPU=1 RGSM=$1 CREATE_INDEX=True VALIDATION_STRINGENCY=SILENT

# Path to the GATK and reference genome
GAT0=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/Somatic-Indel-Detector/GATK/dist/GenomeAnalysisTK.jar
REF=/home/sam/HOPP-Informatics/projects/MutPipeline/Homo_sapiens_assembly19.fasta

java -Xmx8g -jar "$GAT0" -R "$REF" -T SomaticIndelDetector -mnr 50000  \
							   -minConsensusFraction 0.7 \
							   -minCoverage 6 \
							   -minNormalCoverage 4 \
							   -o $3/SI-$4.vcf \
							   -verbose $3/SI-$4.txt \
							   -I:normal $1/out.recal.quality.bam \
							   -I:tumor $2/out.recal.quality.bam \
							   --validation_strictness SILENT -U
