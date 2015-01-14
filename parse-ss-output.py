# This python program parses somatic sniper output and makes an annovar ready output

# Import relevant modules
import sys
import csv
import os
import argparse
#------------------------------------------------------------------#
# Parser Info
#------------------------------------------------------------------#
parser = argparse.ArgumentParser(description='This program parses somatic sniper calls and makes annovar ready file for further processing.')
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

	# Define paths to the directories and tools
	somatic_sniper_directory = path[1]+"/"+"somatic_sniper"
	SS_PARSER_PATH = "/hopp-storage/HOPP-TOOLS/PIPELINES/MutPipelines/scripts/ss-variants-to-table.sh"	
	ANNOVAR = "/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar-may-2013/annovar/annotate_variation.pl -buildver hg19"
	ANNOVAR_DB = "/hopp-storage/HOPP-TOOLS/ANNOTATIONS/annovar-may-2013/annovar/humandb"	
	COSMIC_ANNO = "/hopp-storage/HOPP-TOOLS/PIPELINES/MutPipelines/scripts/annotate-cosmic-calls.sh"
	NOVEL_ANNO = "/hopp-storage/HOPP-TOOLS/PIPELINES/MutPipelines/scripts/annotate-cosmic-filtered-calls.sh"	

	# Make a cosmic directory if it does not exist
	cosmic_directory = somatic_sniper_directory+"/"+"cosmic"
	if not os.path.exists(cosmic_directory):
		os.makedirs(cosmic_directory)

	# Make a directory for non-cosmic mutations if it does not exist
	novel_directory = somatic_sniper_directory+"/"+"novel"
	if not os.path.exists(novel_directory):
                os.makedirs(novel_directory) 

	# For each sample specified in the sample info file do the processing
	for i in range(len(sample_name)):
		print "----------------------------------------------------------------------------"		
		print "Pulling somatic mutations for "+sample_name[i]+" and making tab-delimed format"
		print "----------------------------------------------------------------------------"
		# Call the script to extract somatic sniper vcf calls and make it into table
		os_call = SS_PARSER_PATH+" "+somatic_sniper_directory+" "+sample_name[i]
		os.system(os_call)
		# The above script creates a temproary folder in the path[1]/somatic_sniper folder
		# which has a temproary tab-delimited file that needs to be parsed to make it into annovar format
		# Read the tab-delimited temprory file in path[1]/somatic_sniper/tmp directory
		tmp_file = somatic_sniper_directory+"/"+"tmp"+"/"+sample_name[i]+".tmp2"
		myTmpTabFile = csv.reader(open(tmp_file, "rU"), delimiter='\t', quotechar='|')
		# Make a file in the somatic sniper directory and write the output to the file
		wrt_file = somatic_sniper_directory+"/"+"SS-"+sample_name[i]+"-SOMATIC.tab"
		open_wrt_file = open(wrt_file, "wb")
		myWrtFile = csv.writer(open_wrt_file,delimiter='\t')
		for row in myTmpTabFile:
			# Column 3 is the ref base and columns 7 through 10 are the number of reads 
			# supporting A,C,G,T in that order
			if (row[3] == 'A'):
				ref_reads = row[7]
			if (row[3] == 'C'):
				ref_reads = row[8]
			if (row[3] == 'G'):
                                ref_reads = row[9]
                        if (row[3] == 'T'):
                                ref_reads = row[10]
			# Column 4 is the alt base and columns 11 through 14 are the number of reads
			# supporting A,C,G,T in that order
			if (row[4] == 'A'):
                                alt_reads = row[11]
                        if (row[4] == 'C'):
                                alt_reads = row[12]
			if (row[4] == 'G'):
                                alt_reads = row[13]
			if (row[4] == 'T'):
                                alt_reads = row[14]

			# Compute normal and tumor allelic frequencies
			normal_allelic_frequency = round((float(ref_reads)/float(row[5]))*100,2)
			tumor_allelic_frequency = round((float(alt_reads)/float(row[6]))*100,2)
			# Filter only somatic mutations, where the germline almost matches reference genome (upto 95%)
			if ((float(row[5]) != 0.0) and normal_allelic_frequency > 95):
				mutation_row = [row[0],row[1],row[2],row[3],row[4],row[5],row[6], \
						normal_allelic_frequency,tumor_allelic_frequency,row[15],sample_name[i], "somatic-sniper", \
						sample_name[i]+":"+row[0]+":"+row[1],"point-mutation","1"]
				myWrtFile.writerow(mutation_row)
		
		open_wrt_file.close()	

		# Filter the above somatic mutations through cosmic
		print "----------------------------------------------------------------------------"
		print "Filtering somatic mutations through cosmic"
		print "----------------------------------------------------------------------------"
		os_call = ANNOVAR+" "+"-filter -dbtype cosmic64"+" "+wrt_file+" "+"-outfile"+" "+cosmic_directory+"/"+sample_name[i]+" "+ANNOVAR_DB+"/"
		os.system(os_call) 

		# Annotate the cosmic filtered mutations
		print "----------------------------------------------------------------------------"
		print "Annotating cosmic filtered mutations"
		print "----------------------------------------------------------------------------"
		os_call = COSMIC_ANNO+" "+cosmic_directory+" "+sample_name[i]
		os.system(os_call)
		
		# Filter non-cosmic mutations through 1000g, dbsnp and ESP5400
		print "----------------------------------------------------------------------------"
		print "Filtering non-cosmic mutations through 1000g"
		print "----------------------------------------------------------------------------"
		os_call = ANNOVAR+" "+"-filter -dbtype 1000g2010nov_all"+" "+cosmic_directory+"/"+sample_name[i]+".hg19_cosmic64_filtered"+ \
			  " "+"-outfile"+" "+novel_directory+"/"+sample_name[i]+" "+ANNOVAR_DB+"/"
		os.system(os_call)
		
		# Filter 1000g filtered mutations through ESP5400
		print "----------------------------------------------------------------------------"
		print "Filtering 1000g filtered mutations through ESP5400"
		print "----------------------------------------------------------------------------"
		os_call = ANNOVAR+" "+"-filter -dbtype vcf -vcfdbfile ESP5400.vcf"+ \
				  " "+novel_directory+"/"+sample_name[i]+".hg19_ALL.sites.2010_11_filtered"+ \
				  " "+"-outfile"+" "+novel_directory+"/"+sample_name[i]+" "+ANNOVAR_DB+"/ESP5400"
		os.system(os_call)
		
		# Filter ESP5400 filtered mutations through dbSNP132
		print "----------------------------------------------------------------------------"
                print "Filtering ESP5400 filtered mutations through dbSNP132"
                print "----------------------------------------------------------------------------"
		os_call = ANNOVAR+" "+"-filter -dbtype snp132"+" "+novel_directory+"/"+sample_name[i]+".hg19_vcf_filtered"+ \
				  " "+"-outfile"+" "+novel_directory+"/"+sample_name[i]+" "+ANNOVAR_DB+"/"
		os.system(os_call)
		
		# Annotate dbSNP132 filtered mutations
		print "----------------------------------------------------------------------------"
                print "Annotating dbSNP132 filtered mutations"
                print "----------------------------------------------------------------------------"
                os_call = NOVEL_ANNO+" "+novel_directory+" "+sample_name[i]
                os.system(os_call)

else:
	print 'Sample information file is non-existent. Please make sure you give valid sample info file with path.'
	sys.exit(1)	 
