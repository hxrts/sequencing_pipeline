echo Sniping somatic mutations on sample $3 using normal and tumor recalibrated .bam files 

source /home/sam/HOPP-Informatics/projects/sequencing_pipeline/path_file.txt # includes path to the reference genome $REF

echo $REF
echo "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

bam-somaticsniper -q 1 -Q 15 -J -s 0.01 -F classic -f "$REF" $1/out.recal.quality.bam $2/out.recal.quality.bam $3/SS-$4.txt 

bam-somaticsniper -q 1 -Q 15 -J -s 0.01 -F vcf -f  "$REF" $1/out.recal.quality.bam $2/out.recal.quality.bam $3/SS-$4.vcf  
