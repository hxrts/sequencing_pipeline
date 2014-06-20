# Define the MuTect and other paths
GATK=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/GenomeAnalysisTK-2.4-9-g532efad/GenomeAnalysisTK.jar
REF=/home/sam/HOPP-Informatics/projects/MutPipeline/Homo_sapiens_assembly19.fasta
#REF=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/reference/human_hg19.fasta

/usr/lib/jvm/java-6-openjdk-amd64/jre/bin/java -Xmx2g -jar "$GATK" -T UnifiedGenotyper \
								   -R "$REF" \
								   -rf BadCigar \
								   -filterMBQ \
								   -glm BOTH \
								   -I $1/out.recal.quality.bam \
								   -I $2/out.recal.quality.bam \
								   --out $3/UG-$4.vcf \
								   -L $5 \
								   -stand_call_conf 50.0 \
								   -stand_emit_conf 10.0 \
								   -dcov 50
