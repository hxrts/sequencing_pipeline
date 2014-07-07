#!/bin/bash

if [ $# -eq 0 ]; then
  echo -e "\n"Usage: $0 '[directory containing the .bam file] [interval file]'
  echo -e Note : All files and directories should be specified with full path"\n"
  exit 1;
fi

# --------------------------------------
# Define the path to the required tools
# --------------------------------------
# hg19 reference (uncomment if you want to use hg19)
#REF=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/reference/human_hg19.fasta
REF=/home/sam/HOPP-Informatics/projects/MutPipeline/Homo_sapiens_assembly19.fasta
# GATK reference
GAT=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/GenomeAnalysisTK-2.4-9-g532efad/GenomeAnalysisTK.jar
# samtools reference
SAM=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/samtools/samtools
# Picard tools reference
PIC=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/picard-tools-1.46/
# VCF file reference
VCF_FILE=/HOPP-Informatics/projects/MutPipeline/REF/00-All.vcf
# Use old GATK for identifying target intervals
GAT0=/hopp-storage/HOPP-TOOLS/PIPELINES/GATKBundle/Sting/dist/GenomeAnalysisTK.jar

# ------------------------------------
# Move to the working directory
# ------------------------------------

file_dir=$(echo $1 | sed 's|\(.*\)/.*|\1|')
cd "$file_dir"

file_name=$(basename $1)

# ------------------------------------
# For each file apply the pipeline
# ------------------------------------

for file in `ls -d "$file_dir"/"$file_name"` ; do

  echo 
  echo '###########################################################################'
  echo  Processing "$file_name" using hg19 and VCF=1000 genomes VCF 
  echo '###########################################################################'
  echo 
  # --------------------------------------------------------------------------------
  # Use samtools to clean, sort and index files and use picard to mark duplicates
  # --------------------------------------------------------------------------------
    
  echo ================== Cleaning "$file" ==========================  
  $SAM view -F 0x04 -b "$file" > out.bam
  chmod 755 out.bam
  echo --------------------------------------------------------------
  echo Sorting "$file" 
  echo --------------------------------------------------------------
  $SAM sort out.bam out.sorted
  chmod 755 out.sorted.bam
  echo --------------------------------------------------------------
  echo Indexing "$file" 
  $SAM index out.sorted.bam out.sorted.bam.bai
  
  echo --------------------------------------------------------------
  echo Marking Duplicates 
  echo --------------------------------------------------------------
  java -Xmx15g -jar $PIC/MarkDuplicates.jar \
  	    	   I=out.sorted.bam \
  	     	   O=out.not.ordered.sorted.marked.bam \
                   M=my.duplication.metrics \
                   AS=true \
		   REMOVE_DUPLICATES=true \
  		   VALIDATION_STRINGENCY=LENIENT
  echo --------------------------------------------------------------
  echo Reordering marked file
  java -Xmx15g -jar $PIC/ReorderSam.jar ALLOW_INCOMPLETE_DICT_CONCORDANCE=TRUE I=out.not.ordered.sorted.marked.bam O=out.sorted.marked.bam REFERENCE=$REF
  echo
  echo --------------------------------------------------------------
  echo Adding read groups to the sorted and marked bam file
  java -Xmx15g -jar $PIC/AddOrReplaceReadGroups.jar \
	            I=out.sorted.marked.bam \
		    O=out.sorted.marked.readgroup.bam \
		    SORT_ORDER=coordinate \
		    RGID=1 \
		    RGLB=mskcc \
		    RGPL=illumina \
		    RGPU=1 \
		    RGSM=$1 \
		    CREATE_INDEX=True \
		    VALIDATION_STRINGENCY=SILENT 
  echo
  echo --------------------------------------------------------------
  echo Indexing the marked and readgroup added duplicates '.bam' file
  $SAM index out.sorted.marked.readgroup.bam out.sorted.marked.readgroup.bam.bai
  echo 
  # -----------------------------------------------------------------
  # Use GATK to identify target regions for realignment and realign 
  # -----------------------------------------------------------------
  echo ==================== Starting GATK  ========================== 
  echo --------------------------------------------------------------
  echo Identifying target regions for realignment 
  echo --------------------------------------------------------------
  java -Xmx15g -jar $GAT0 -T RealignerTargetCreator \
                          -R $REF \
                          -I out.sorted.marked.readgroup.bam \
			  -L $2 \
                          -B:dbsnp,VCF $VCF_FILE \
                          -o out.intervals  
  
  echo --------------------------------------------------------------
  echo Realigning the file "$file" 
  echo --------------------------------------------------------------
  java -Xmx15g -jar $GAT -T IndelRealigner \
                         -R $REF \
                         -I out.sorted.marked.readgroup.bam \
			 -L $2 \
                         -targetIntervals out.intervals \
			 -filterMBQ \
                         -o out.realigned.bam  
  # ---------------------------------------------
  # Count covariates and recalibrate using GATK
  # ---------------------------------------------
  echo --------------------------------------------------------------
  echo Counting covariates 
  echo --------------------------------------------------------------
  java -Xmx15g -jar $GAT0 -T CountCovariates \
                          --solid_nocall_strategy PURGE_READ \
                          -cov ReadGroupCovariate \
                          -cov QualityScoreCovariate \
                          -cov CycleCovariate \
                          -cov DinucCovariate \
                          -R $REF \
			  -L $2 \
                          -I out.realigned.bam \
                          -B:dbsnp,VCF $VCF_FILE \
                          -recalFile recal_data.csv \
			  -dP illumina \
			  -dRG xxxxx \
                          -nt 12
  echo --------------------------------------------------------------
  echo Table recalibration 
  echo --------------------------------------------------------------
  java -Xmx15g -jar $GAT0 -T TableRecalibration \
                          --solid_nocall_strategy PURGE_READ \
                          -R $REF \
			  -L $2 \
                          -I out.realigned.bam \
                          --out out.recal.bam \
                          -recalFile recal_data.csv \
			  -dP illumina \
			  -dRG xxxxx 
  echo --------------------------------------------------------------
  echo Removing reads with zero mapping quality
  echo -------------------------------------------------------------- 
  $SAM view -b -q 1 out.recal.bam > out.recal.quality.bam
  $SAM index out.recal.quality.bam
  # -------------------------------------------
  # Pipeline ends here
  # -------------------------------------------
  # echo ====================== Cleaning up ============================
  # echo ---------------------------------------------------------------
  # echo Creating relevant directories 
  # echo --------------------------------------------------------------- 
  # mkdir ../recalibrated-"$file"

  ###################################################################
  ### Depricated - No longer used
  ###################################################################
  ### mkdir analysis-"$file"-folder/original
  ### mkdir analysis-"$file"-folder/pre-processed
  ### mkdir analysis-"$file"-folder/indel-realignment
  ### mkdir analysis-"$file"-folder/recalibrated
  ###################################################################

  # echo ---------------------------------------------------------------
  # echo Moving folders to appropriate places 
  # echo ---------------------------------------------------------------

  ###################################################################
  ### Depricated - No longer used
  ###################################################################
  ### mv "$file" analysis-"$file"-folder/original
  ### mv "$file".bai analysis-"$file"-folder/original    
  ### mv out.bam out.sorted.bam out.sorted.bam.bai \
  ###    out.sorted.marked.bam out.sorted.marked.bam.bai \
  ###    my.duplication.metrics analysis-"$file"-folder/pre-processed
  ### mv out.intervals out.realigned.bam out.realigned.bai \
  ###    analysis-"$file"-folder/indel-realignment
  ###################################################################

  # mv recal_data.csv out.recal.quality.bam out.recal.quality.bam.bai ../recalibrated-"$file"

  echo ----------------------------------------------------------------
  echo Removing unwanted intermediary files
  echo ----------------------------------------------------------------

  if [ -f out.recal.quality.bam ]; then
    if [ -s out.recal.quality.bam ]; then  
      rm -rf out.bam out.sorted.bam out.sorted.bam.bai \
             out.sorted.marked.bam out.sorted.marked.bam.bai \
	     out.sorted.marked.readgroup.bam out.sorted.marked.readgroup.bai out.sorted.marked.readgroup.bam.bai \
             my.duplication.metrics out.not.ordered.sorted.marked.bam
      rm -rf out.intervals out.realigned.bam out.realigned.bai out.recal.bam out.recal.bai
    else
      echo out.recal.quality.bam size is zero - something wrong with the pipeline
    fi
  else
    echo out.recal.quality.bam does not exist - something wrong with the pipeline
  fi

done
