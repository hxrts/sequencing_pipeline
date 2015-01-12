#--------#
# GLOBAL
#--------#

REF=/home/sam/HOPP-Informatics/projects/sequencing_pipeline/refs/Homo_sapiens_assembly19.fasta

#---------#
# ANNOVAR
#---------#

ANNOVAR_PATH=/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar/annotate_variation.pl
ANNOVAR_DB=/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar/humandb/
ANNOVAR0=/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar/convert2annovar.pl
ANNOVAR="/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar-may-2013/annovar/annotate_variation.pl -buildver hg19"
ANNOVAR_DB=/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar-may-2013/annovar/humandb

#------#
# GATK
#------#

GATK=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/GenomeAnalysisTK-2.4-9-g532efad/GenomeAnalysisTK.jar
GAT1=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/Somatic-Indel-Detector/GATK/dist/GenomeAnalysisTK.jar
GAT0=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/Sting/dist/GenomeAnalysisTK.jar	# Use old GATK for identifying target intervals

#--------#
# MUTECT
#--------#

MUTECT_PATH_VER14=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/MuTect/version-1.4/muTect-1.1.4.jar

#---------------#
# SNP DATABASES
#---------------#

COSMIC=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/MuTect/version-1.0/hg19_cosmic_v54_120711.vcf
DBSNP=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/MuTect/version-1.0/dbsnp_132_b37.leftAligned.vcf

#----------#
# SAMTOOLS
#----------#

SAM=/home/sam/HOPP-Informatics/projects/sequencing_pipeline/tools/samtools-0.1.19/samtools

#--------#
# PICARD
#--------#

PIC=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/picard-tools-1.46/
VCF_FILE=/home/sam/HOPP-Informatics/projects/sequencing_pipeline/refs/00-All.vcf

#--------#
# SNPEFF
#--------#

SNPEFF=/hopp-storage/HOPP-TOOLS/ANNOTATIONS/snpEff/SnpSift.jar

#------------------------------#
# annotation execution scripts
#------------------------------#

# 1000g_ANNO=/hopp-storage/HOPP-TOOLS/PIPELINES/MutPipelines/scripts/annotate-100g-calls.sh <------ missing
# ESP_ANNO=/hopp-storage/HOPP-TOOLS/PIPELINES/MutPipelines/scripts/annotate-ESP-calls.sh <------ missing
# dbSNP_ANNO=/hopp-storage/HOPP-TOOLS/PIPELINES/MutPipelines/scripts/annotate-dbSNP-calls.sh <------ missing
# COSMIC_ANNO=/HOPP-Informatics/projects/sequencing_pipeline/scripts/annotate-cosmic-calls.sh




