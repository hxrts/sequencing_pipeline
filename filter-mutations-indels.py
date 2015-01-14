# --------------------------------------------------------------------------------------------------------
# This program filters the mutations and indels through snp databases and annotates them.
# --------------------------------------------------------------------------------------------------------
# Import relevant modules
import sys
import csv
import os
import argparse
#------------------------------------------------------------------#
# Parser Info
#------------------------------------------------------------------#
parser = argparse.ArgumentParser(description='This program filters mutations and indels that were called')
parser.add_argument('-s','--sample-info', help='Sample information file [Required]', required=True)
#------------------------------------------------------------------#
# Get parser arguments and check validity
#------------------------------------------------------------------#
args = vars(parser.parse_args())
sample_file = args['sample_info']
#-------------------------------------------------------------------------#
# If sample info path exists then read the file & execute filter pipeline
#-------------------------------------------------------------------------# 
if (os.path.exists(sample_file)==True):

	# Open the input tab-delimited file
	myInputTabFile=csv.reader(open(sample_file, "rU"), delimiter='\t', quotechar='|')

	# Define the list for storing the information from the sample info file
	sample_name = []
	normal_bam_file = []
	tumor_bam_file = []
	path = []

	count = 0
	# Read the file by the row
	for row in myInputTabFile:
        	# first line contains the bam path
        	if(count == 0):
                	path.append(row[1])
        	# second line contains the local path
        	if(count == 1):
                	path.append(row[1])
        	# from third line we have the sample information
        	if(count > 1):
                	# row[0] is sample name
                	sample_name.append(row[0])
                	# row[1] is the normal bam file
                	normal_bam_file.append(row[1])
                	# row[2] is the tumor bam file
                	tumor_bam_file.append(row[2])

        	count=count+1

	# Make a directory in the path to store the results
	directory = path[1]+"/filtered"
	if not os.path.exists(directory):
    		os.makedirs(directory)

	# Make directories for results
	somatic_sniper_directory = directory + "/somatic_sniper"
	somatic_indel_directory = directory + "/somatic_indel_detector"
	mutect_directory = directory + "/mutect"
	unified_genotyper_directory = directory + "/unified_genotyper"

	if not os.path.exists(somatic_sniper_directory):
		os.makedirs(somatic_sniper_directory)
        if not os.path.exists(somatic_indel_directory): 
		os.makedirs(somatic_indel_directory)
	if not os.path.exists(mutect_directory):
		os.makedirs(mutect_directory)
	if not os.path.exists(unified_genotyper_directory):
		os.makedirs(unified_genotyper_directory)

	# Existing called variants directories
	ss_mut_call_dir = path[1]+"/somatic_sniper"
	si_mut_call_dir = path[1]+"/somatic_indel_detector"
	mu_mut_call_dir = path[1]+"/mutect"
	ug_mut_call_dir = path[1]+"/unified_genotyper"

	#-------------------------------------------------------------#
	# Define paths for the required programs and files
	#-------------------------------------------------------------#
	# ANNOVAR Path
	ANNOVAR_CONVERSION_PATH="/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar/convert2annovar.pl"
	#-------------------------------------------------------------#

	# For each sample specified in the sample info file do the processing
	for i in range(len(sample_name)):
		
        	# Status information
		print "-------------------------------------------------------------"
        	print "Converting sample "+sample_name[i]+"into annovar format"
		print "-------------------------------------------------------------"
		print "Converting Somatic Sniper results to annovar format for "+sample_name[i]
		sys.stdout.flush()
		os_call = ANNOVAR_CONVERSION_PATH + " " + ss_mut_call_dir + "/SS-" + sample_name[i] + ".vcf -format vcf4 --includeinfo" + " > " +somatic_sniper_directory+ "/" + sample_name[i] + ".annovar"
else:
	print 'Sample information file is non-existent. Please make sure you give valid sample info file with path.'
	sys.exit(1)
