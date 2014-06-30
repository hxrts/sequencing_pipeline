# Define the MuTect and other paths
MUTECT_PATH_VER10=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/MuTect/version-1.0/muTect-1.0.27783-bin-BETA/muTect-1.0.27783.jar
MUTECT_PATH_VER14=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/MuTect/version-1.4/muTect-1.1.4.jar
REF=/home/sam/HOPP-Informatics/projects/MutPipeline/Homo_sapiens_assembly19.fasta
COSMIC=/hopp-storage/HOPP-TOOLS/PIPELINES/MutTools/MuTect/version-1.0/hg19_cosmic_v54_120711.vcf
DBSNP=/hopp-storage/HOPP-TOOLS/PIPELINES/MutTools/MuTect/version-1.0/dbsnp_132_b37.leftAligned.vcf

/usr/lib/jvm/java-6-openjdk-amd64/jre/bin/java -Xmx2g -jar "$MUTECT_PATH_VER14" -T MuTect \
										-R "$REF" \
										-rf BadCigar \
										-filterMBQ \
										--input_file:tumor $1/out.recal.quality.bam \
										--input_file:normal $2/out.recal.quality.bam \
										--out $3/MU-$4.txt \
										-L $5
# java -Xmx2g -jar "$MUTECT_PATH_VER14" -T MuTect -R "$REF" --tumor_sample_name $1/out.recal.quality.bam --normal_sample_name $2/out.recal.quality.bam --dbsnp "$DBSNP" --cosmic "$COSMIC" --out $3
