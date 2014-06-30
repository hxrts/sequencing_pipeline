# This is the master script for parsing mutation calls from various programs, filtering and annotating them.

# example file input: python master.py

# Import relevant modules
import sys
import csv
import os
import argparse
#------------------------------------------------------------------#
# Parser Info
#------------------------------------------------------------------#
parser = argparse.ArgumentParser(description='This program parses mutation calls, filters and annotates them')
parser.add_argument('-s','--sample-info', help='Sample information file [Required]', required=True)
parser.add_argument('-fss','--somatic-sniper', help='Filter and annotate somatic sniper calls', required=False)
parser.add_argument('-fsi','--somatic-indels', help='Filter and annotate somatic indel detector calls', required=False)
parser.add_argument('-fmu','--mutect', help='Filter and annotate mutect calls', required=False)
parser.add_argument('-fug','--unified-genotyper', help='Filter and annotate unified genotyper calls', required=False)
parser.add_argument('-p','--path-file', help='Path file [Required]', required=True)

# Get parser arguments
args = vars(parser.parse_args())
sample_file = args['sample_info']
exdir = os.path.dirname(__file__)

# Check the arguments of -r/--recalibrate, -mu/--mutect, -ss/--somatic-sniper, -si/--somatic-indels, -ug/--unified-genotyper, -p/--path-file
if ((args['mutect'] != None) and (args['mutect'] != 'MUTECT')):
        print "Please check the argument of -mu/--mutect: It should be MUTECT"
        sys.exit(1)
if ((args['somatic_sniper'] != None) and (args['somatic_sniper'] != 'SOMATIC-SNIPER')):
        print "Please check the argument of -ss/--somatic-sniper: It should be SOMATIC-SNIPER"
        sys.exit(1)
if ((args['somatic_indels'] != None) and (args['somatic_indels'] != 'SOMATIC-INDELS')):
        print "Please check the argument of -si/--somatic-indels: It should be SOMATIC-INDELS"
        sys.exit(1)
if ((args['unified_genotyper'] != None) and (args['unified_genotyper'] != 'UNIFIED-GENOTYPER')):
        print "Please check the argument of -ug/--unified-genotyper: It should be UNIFIED-GENOTYPER"
        sys.exit(1)
if ((args['path_file'] != None) and (args['path_file'] != 'PATH-FILE')):
        print "Please check the argument of -p/path-file: It should be PATH-FILE"
        sys.exit(1)

# Set a flag if a particular call filtering is set 
if (args['mutect'] != None):
	mutect_flag = 1
else:
	mutect_flag = 0
if (args['somatic_sniper'] != None):
	somatic_sniper_flag = 1
else:
	somatic_sniper_flag = 0
if (args['somatic_indels'] != None):
	somatic_indels_flag = 1
else:
	somatic_indels_flag = 0
if (args['unified_genotyper'] != None):
	unified_genotyper_flag = 1
else:
	unified_genotyper_flag = 0
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
	if (somatic_sniper_flag == 1):
		mutation_directory = path[1]+"/"+"somatic_sniper"
		SS_PARSER_PATH = "/hopp-storage/HOPP-TOOLS/PIPELINES/MutPipelines/scripts/ss-variants-to-table.sh"
	if (somatic_indels_flag == 1):
		mutation_directory = path[1]+"/"+"somatic_indel_detector"
        	SI_PARSER_PATH = "/hopp-storage/HOPP-TOOLS/PIPELINES/MutPipelines/scripts/si-variants-to-table.sh"
	if (mutect_flag == 1):
		mutation_directory = path[1]+"/"+"mutect"
		MUTECT_PARSER_PATH = "/hopp-storage/HOPP-TOOLS/PIPELINES/MutPipelines/scripts/mu-variants-to-table.sh"

	# Define the paths to the tools
	ANNOVAR = os.path.join(exdir, '/tools/annovar/annotate_variation.pl -buildver hg19')
	ANNOVAR_DB = os.path.join(exdir, '/tools/annovar/humandb')
	otg_ANNO = os.path.join(exdir, '/scripts/annotate-1000g-calls.sh')
	ESP_ANNO = os.path.join(exdir, '/scripts/annotate-ESP-calls.sh')
	dbSNP_ANNO = os.path.join(exdir, '/scripts/annotate-dbSNP-calls.sh')
	COSMIC_ANNO = os.path.join(exdir, '/scripts/annotate-cosmic-calls.sh')

	# Make a filter directory if it does not exist
        filter_directory = mutation_directory+"/"+"filter"
        if not os.path.exists(filter_directory):
                os.makedirs(filter_directory)

	# For each sample specified in the sample info file do the processing
	for i in range(len(sample_name)):

		# Make a tab delimed file in the mutation directory for writing
		wrt_file = mutation_directory+"/"+sample_name[i]+"-SOMATIC.tab"
		print "----------------------------------------------------------------------------"		
		print "Pulling somatic mutations for "+sample_name[i]+" and making tab-delimed format"
		print "----------------------------------------------------------------------------"
		if (somatic_sniper_flag == 1):
			print "Converting somatic sniper vcf for "+sample_name[i]+" to tab-delimed format"
			somatic_sniper_directory = mutation_directory
			# Call the script to extract somatic sniper vcf calls and make it into table
			os_call = SS_PARSER_PATH+" "+somatic_sniper_directory+" "+sample_name[i]
			os.system(os_call)
			# The above script creates a temproary folder in the path[1]/somatic_sniper folder
			# which has a temproary tab-delimited file that needs to be parsed to make it into annovar format
			# Read the tab-delimited temprory file in path[1]/somatic_sniper/tmp directory
			tmp_file = somatic_sniper_directory+"/"+"tmp"+"/"+sample_name[i]+".tmp2"
			myTmpTabFile = csv.reader(open(tmp_file, "rU"), delimiter='\t', quotechar='|')
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

		if (somatic_indels_flag == 1):
			somatic_indel_directory = mutation_directory
                	print "Converting somatic indel detector vcf for "+sample_name[i]+" to tab-delimed format"
                	# Call the script to extract somatic indel vcf calls and make it into table
                	os_call = SI_PARSER_PATH+" "+somatic_indel_directory+" "+sample_name[i]
                	os.system(os_call)
                	# The above script creates a temproary folder in the path[1]/somatic_indel_detector folder
                	# which has a temproary tab-delimited file that needs to be parsed to make it into annovar format
                	# Read the tab-delimited temprory file in path[1]/somatic_indel_detector/tmp directory
                	tmp_file = somatic_indel_directory+"/"+"tmp"+"/"+sample_name[i]+".tmp2"
                	myTmpTabFile = csv.reader(open(tmp_file, "rU"), delimiter='\t', quotechar='|')
                	# Make a file in the somatic indel directory and write the output to the file
			open_wrt_file = open(wrt_file, "wb")
                        myWrtFile = csv.writer(open_wrt_file,delimiter='\t')
                	for row in myTmpTabFile:
				# Check if it is a insertion or a deletion by finding the number of bases
                        	if (row[3] == "-"):
                                	mutation_row = [row[0],row[1],row[2],row[3],row[4],row[5],row[6], \
                                        	        row[7],row[8],row[9],sample_name[i], "somatic-indel-dectector", \
                                                	sample_name[i]+":"+row[0]+":"+row[1],"insertion","1"]
                        	elif (row[4] == "-"):
                                	mutation_row = [row[0],row[1],row[2],row[3],row[4],row[5],row[6], \
                                        	        row[7],row[8],row[9],sample_name[i], "somatic-indel-dectector", \
                                                	sample_name[i]+":"+row[0]+":"+row[1],"deletion","1"]
                        	else:
                                	mutation_row = [row[0],row[1],row[2],row[3],row[4],row[5],row[6], \
                                        	        row[7],row[8],row[9],sample_name[i], "somatic-indel-dectector", \
                                                	sample_name[i]+":"+row[0]+":"+row[1],"del-or-ins","1"]
                        	myWrtFile.writerow(mutation_row)
	
		if (mutect_flag == 1):
			mutect_directory = mutation_directory
			print "Converting mutect file for "+sample_name[i]+" to tab-delimited format"
			# Call the script to extract "KEEP" mutect calls and make it into table
			os_call = MUTECT_PARSER_PATH+" "+mutect_directory+" "+sample_name[i]
			os.system(os_call)
			# The above script creates a temproary folder in the path[1]/mutect folder
                        # which has a temproary tab-delimited file that needs to be parsed to make it into annovar format
                        # Read the tab-delimited temprory file in path[1]/mutect_detector/tmp directory
			tmp_file = mutect_directory+"/"+"tmp"+"/"+sample_name[i]+".tmp2"
			myTmpTabFile = csv.reader(open(tmp_file, "rU"), delimiter='\t', quotechar='|')
                        # Make a file in the somatic indel directory and write the output to the file
                        open_wrt_file = open(wrt_file, "wb")
                        myWrtFile = csv.writer(open_wrt_file,delimiter='\t')
			for row in myTmpTabFile:
				mutation_row = [row[0],row[1],row[2],row[3],row[4],row[5],row[6], \
                                		row[7],row[8],row[9],sample_name[i], "mutect", \
                               			sample_name[i]+":"+row[0]+":"+row[1],"point-mutation","1"]
				myWrtFile.writerow(mutation_row)

		open_wrt_file.close()

		# Filter the above somatic mutations through cosmic
		print "----------------------------------------------------------------------------"
		print "Filtering somatic mutations through cosmic"
		print "----------------------------------------------------------------------------"
		os_call = ANNOVAR+" "+"-filter -dbtype cosmic64"+" "+wrt_file+" "+"-outfile"+" "+filter_directory+"/"+sample_name[i]+" "+ANNOVAR_DB+"/COSMIC"
		os.system(os_call)

		# Annotate cosmic filtered mutations
		print "----------------------------------------------------------------------------"
		print "Annotating cosmic filtered mutations"
		print "----------------------------------------------------------------------------"
		os_call = COSMIC_ANNO+" "+filter_directory+" "+sample_name[i]
		os.system(os_call)
		
		# Filter somatic  mutations through 1000g
		print "----------------------------------------------------------------------------"
		print "Filtering somatic mutations through 1000g"
		print "----------------------------------------------------------------------------"
		os_call = ANNOVAR+" "+"-filter -dbtype 1000g2010nov_all"+" "+wrt_file+" "+"-outfile"+" "+filter_directory+"/"+sample_name[i]+" "+ANNOVAR_DB+"/1000g"
		os.system(os_call)
	
                # Annotate 1000g filtered mutations
                print "----------------------------------------------------------------------------"
                print "Annotating 1000g filtered mutations"
                print "----------------------------------------------------------------------------"
                os_call = otg_ANNO+" "+filter_directory+" "+sample_name[i]
                os.system(os_call)
	
		# Filter somatic mutations through ESP5400
		print "----------------------------------------------------------------------------"
		print "Filtering somatic filtered mutations through ESP5400"
		print "----------------------------------------------------------------------------"
		os_call = ANNOVAR+" "+"-filter -dbtype vcf -vcfdbfile ESP5400.vcf"+" "+wrt_file+" "+"-outfile"+" "+filter_directory+"/"+sample_name[i]+" "+ANNOVAR_DB+"/ESP"
		os.system(os_call)
		
                # Annotate ESP5400 filtered mutations
                print "----------------------------------------------------------------------------"
                print "Annotating ESP5400 filtered mutations"
                print "----------------------------------------------------------------------------"
                os_call = ESP_ANNO+" "+filter_directory+" "+sample_name[i]
                os.system(os_call)

		# Filter somatic filtered mutations through dbSNP132
		print "----------------------------------------------------------------------------"
                print "Filtering somatic filtered mutations through dbSNP132"
                print "----------------------------------------------------------------------------"
		os_call = ANNOVAR+" "+"-filter -dbtype snp132"+" "+wrt_file+" "+"-outfile"+" "+filter_directory+"/"+sample_name[i]+" "+ANNOVAR_DB+"/dbSNP"
		os.system(os_call)
		
		# Annotate dbSNP132 filtered mutations
		print "----------------------------------------------------------------------------"
                print "Annotating dbSNP132 filtered mutations"
                print "----------------------------------------------------------------------------"
                os_call = dbSNP_ANNO+" "+filter_directory+" "+sample_name[i]
                os.system(os_call)

else:
	print 'Sample information file is non-existent. Please make sure you give valid sample info file with path.'
	sys.exit(1)	 
