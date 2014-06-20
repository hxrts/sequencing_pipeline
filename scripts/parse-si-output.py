# This python program parses somatic indel detector output and makes an annovar ready output

# Import relevant modules
import sys
import csv
import os
import argparse
#------------------------------------------------------------------#
# Parser Info
#------------------------------------------------------------------#
parser = argparse.ArgumentParser(description='This program parses somatic indel detector calls and makes annovar ready file for further processing.')
parser.add_argument('-s','--sample-info', help='Sample information file [Required]', required=True)
# Get parser arguments
args = vars(parser.parse_args())
sample_file = args['sample_info']
#---------------------------------------------------------------------#
# If sample info path exists then read the file 
#---------------------------------------------------------------------# 
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

	somatic_indel_directory = path[1]+"/"+"somatic_indel_detector"
	SI_PARSER_PATH = "/hopp-storage/HOPP-TOOLS/PIPELINES/MutPipelines/scripts/si-variants-to-table.sh"	

	# For each sample specified in the sample info file do the processing
	for i in range(len(sample_name)):
		
		print "Converting somatic indel detector vcf for "+sample_name[i]+" to tab-delimed format"
		# Call the script to extract somatic indel vcf calls and make it into table
		os_call = SI_PARSER_PATH+" "+somatic_indel_directory+" "+sample_name[i]
		os.system(os_call)
		# The above script creates a temproary folder in the path[1]/somatic_indel_directory folder
		# which has a temproary tab-delimited file that needs to be parsed to make it into annovar format
		# Read the tab-delimited temprory file in path[1]/somatic_indel_detector/tmp directory
		tmp_file = somatic_indel_directory+"/"+"tmp"+"/"+sample_name[i]+".tmp2"
		myTmpTabFile = csv.reader(open(tmp_file, "rU"), delimiter='\t', quotechar='|')
		# Make a file in the somatic indel directory and write the output to the file
		wrt_file = somatic_indel_directory+"/"+"SI-"+sample_name[i]+"-SOMATIC.tab"
		myWrtFile = csv.writer(open(wrt_file, "wb"),delimiter='\t')
		for row in myTmpTabFile:
			if (len(row[3]) > 1):
				mutation_row = [row[0],row[1],row[2],row[3],row[4],row[5],row[6], \
						row[7],row[8],row[9],sample_name[i], "somatic-indel-dectector", \
						sample_name[i]+":"+row[0]+":"+row[1],"deletion","1"]
			elif (len(row[4]) > 1):
				mutation_row = [row[0],row[1],row[2],row[3],row[4],row[5],row[6], \
                                                row[7],row[8],row[9],sample_name[i], "somatic-indel-dectector", \
                                                sample_name[i]+":"+row[0]+":"+row[1],"insertion","1"]
			else:
				mutation_row = [row[0],row[1],row[2],row[3],row[4],row[5],row[6], \
                                                row[7],row[8],row[9],sample_name[i], "somatic-indel-dectector", \
                                                sample_name[i]+":"+row[0]+":"+row[1],"del-or-ins","1"] 
		
			myWrtFile.writerow(mutation_row)
else:
	print 'Sample information file is non-existent. Please make sure you give valid sample info file with path.'
	sys.exit(1)	 
