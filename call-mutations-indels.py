# --------------------------------------------------------------------------------------------------------#
# This primary script that parses the sample information provided by the user and calls mutations + indels
# If there is a need to realign and recalibrate, it runs GATK realignment/recalibration scripts
# --------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------#
# Import relevant modules
#------------------------------------------------------------------#

import sys
import csv
import os
import argparse

#------------------------------------------------------------------#
# Parser Info
#------------------------------------------------------------------#

parser = argparse.ArgumentParser(description='This program calls mutations and indels after indel realignment and recalibration. \
					    					  It optionally does GATK realignment and recalibration.')
parser.add_argument('-s','--sample-info', help='Sample information file [Required]', required=True)
parser.add_argument('-d','--directory', help='Temproary directory name to create [Required]',required=True)
parser.add_argument('-r','--recalibrate', help='Option to realign and recalibrate', required=False)
parser.add_argument('-b','--bedfile', help='Option to realign/recalibrate only on the specified intervals given by the bed file', required=False)
parser.add_argument('-ov','--only-variants', help='Option to call only variants when the recalibrated files are locally present', required=False)
parser.add_argument('-mu','--mutect', help='Option to use only mutect', required=False)
parser.add_argument('-ss','--somatic-sniper', help='Option to use only somatic sniper',required=False)
parser.add_argument('-si','--somatic-indels', help='Option to use only somatic indel detector',required=False)
parser.add_argument('-ug','--unified-genotyper', help='Option to use only unified genotyper',required=False)
parser.add_argument('-p','--path-file', help='Specifies path file',required=True)

#------------------------------------------------------------------#
# Get parser arguments and check validity
#------------------------------------------------------------------#

args = vars(parser.parse_args())
sample_file = args['sample_info']
directory_name = args['directory']
bedfile_name = args['bedfile']
exdir = os.path.dirname(os.path.abspath(__file__))

# Check the arguments of -r/--recalibrate, -mu/--mutect, -ss/--somatic-sniper, -si/--somatic-indels -ug/--unified-genotyper
if ((args['recalibrate'] != None) and (args['recalibrate'] != 'RECALIBRATE')):
	print "Please check the argument of -r/--recalibrate: It should be RECALIBRATE"
	sys.exit(1)
if ((args['only_variants'] != None) and (args['only_variants'] != 'ONLY-VARIANTS')):
	print "Please check the argument of -ov/--only-variants: It should be ONLY-VARIANTS"
	sys.exit(1)
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
#-------------------------------------------------------------#
# If none of the options for -mu, -ss, -si are given, then
# execute all the callers by setting the flag to 1
#-------------------------------------------------------------#

if ((args['mutect'] == None) and (args['somatic_sniper'] == None) and (args['somatic_indels'] == None) and (args['unified_genotyper'] == None)):
	mutect_flag = 1
	somatic_sniper_flag = 1
	somatic_indel_flag = 1
	unified_genotyper_flag = 1
if (args['only_variants'] == None):
	only_variants_flag = 0

#-------------------------------------------------------------#
# Otherwise execute only the required caller by setting the 
# callers flag as 1 and other callers flag as 0
#-------------------------------------------------------------#

if (args['mutect'] != None):
	mutect_flag = 1
	somatic_sniper_flag = 0
	somatic_indel_flag = 0
	unified_genotyper_flag = 0
if (args['somatic_sniper'] != None):
	mutect_flag = 0
	somatic_sniper_flag = 1
	somatic_indel_flag = 0
	unified_genotyper_flag = 0
if (args['somatic_indels'] != None):
	mutect_flag = 0
	somatic_sniper_flag = 0
	somatic_indel_flag = 1
	unified_genotyper_flag = 0
if (args['unified_genotyper'] != None):
	mutect_flag = 0
	somatic_sniper_flag = 0
	somatic_indel_flag = 0
	unified_genotyper_flag = 1
if ((args['bedfile'] != None)):
	bedfile_flag = 1
else:
	bedfile_flag = 0
if (args['only_variants'] != None):
	only_variants_flag = 1

#-------------------------------------------------------------#
# Define paths for the required programs
#-------------------------------------------------------------#

SAM_INDEX_PATH = exdir + '/home/sam/tools/samtools-1.1/samtools index'		# samtools path	
GATK_PATH = exdir + '/scripts/pipelineGATK.sh'																				# GATK pipeline path
GATK_INTERVAL_PATH = exdir + '/scripts/pipelineIntervalGATK.sh'																# GATK interval script path
SOMATIC_SNIPER_PATH = exdir + '/scripts/call-somatic-sniper.sh'																# somatic sniper path
SOMATIC_INDEL_PATH = exdir + '/scripts/call-indels.sh'																		# somatic indel_detector path
SOMATIC_INDEL_INTERVAL_PATH = exdir + '/scripts/call-indels-with-intervals.sh'												# somatic indel path with intervals
MUTECT_PATH = exdir + '/scripts/call-mutect.sh'																				# mutect path
MUTECT_INTERVAL_PATH = exdir + '/scripts/call-mutect-with-intervals.sh'														# mutect path with intervals
UNIFIED_GENOTYPER_PATH = exdir + '/scripts/call-genotyper.sh'																# unified genotyper path
UNIFIED_GENOTYPER_INTERVAL_PATH = exdir + '/scripts/call-genotyper-with-intervals.sh'										# unified genotyper with intervals

#------------------------------------------------------------------#
# If sample info path exists then read the file & execute pipeline
#------------------------------------------------------------------# 

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

	# Make a temproary directory in the path only if only variants flag is zero
	directory = path[1]+"/TMP"+"-"+directory_name
	if (only_variants_flag == 0):
		if not os.path.exists(directory):
				os.makedirs(directory)
		else:
			os_call = "rm -rf "+ directory
			os.system(os_call)
			os.makedirs(directory)

	# Check if the recalibration flag is on and in that case make a folder for storing raw bams
	if (only_variants_flag == 0):
		if (args['recalibrate'] == 'RECALIBRATE'):
			os.makedirs(directory + "/raw_bams")
			os.makedirs(directory + "/recalibrated_bams")
		else:
			os.makedirs(directory + "/recalibrated_bams")
	
	# Make directories for results
	somatic_sniper_directory = path[1] + "/somatic_sniper"
	somatic_indel_directory = path[1] + "/somatic_indel_detector"
	mutect_directory = path[1]+"/mutect"
	unified_genotyper_directory = path[1]+"/unified_genotyper"

	if not os.path.exists(somatic_sniper_directory):
		if (somatic_sniper_flag == 1):
			os.makedirs(somatic_sniper_directory)
		if not os.path.exists(somatic_indel_directory):
			if (somatic_indel_flag == 1):
				os.makedirs(somatic_indel_directory)
	if not os.path.exists(mutect_directory):
		if (mutect_flag == 1):
			os.makedirs(mutect_directory)
	if not os.path.exists(unified_genotyper_directory):
		if (unified_genotyper_flag == 1):
			os.makedirs(unified_genotyper_directory)

	#---------------------------------------------------------------------#
	# For each sample specified in the sample info file do the processing
	#---------------------------------------------------------------------#
	
	for i in range(len(sample_name)):
		
			# Status information
		print "-------------------------------------------------------------"
		print "Processing sample "+sample_name[i]
		print "-------------------------------------------------------------"
		sys.stdout.flush()	
		# We call copying and realignment/recalibration scripts only if "only_variants_flag" is zero
		if (only_variants_flag == 0):
			# If we need to do realignment and recalibration copy the raw bams in the local directory and execute GATK
			if (args['recalibrate'] == 'RECALIBRATE'):
				
				# First copy the normal and tumor files to the local directory
				normal_directory = directory + "/raw_bams" + "/" + sample_name[i] + "_NL"
				tumor_directory = directory + "/raw_bams" + "/" + sample_name[i] + "_TU"
				os.makedirs(normal_directory)
				os.makedirs(tumor_directory)
				sys.stdout.flush()
				os_call = "cp "+path[0]+"/"+normal_bam_file[i]+" "+normal_directory
				os.system(os_call)
				print "Copying normal bam file to the local folder"
				sys.stdout.flush()
				os_call = "cp "+path[0]+"/"+tumor_bam_file[i]+" "+tumor_directory
				os.system(os_call)
				print "Copying tumor bam file to the local folder"
		
				# Call GATK pipeline to the tumor and normal files locally stored
				if (bedfile_flag == 1):
					print "Calling GATK interval pipeline on the normal and tumor bams"
					print "-------------------------------------------------------------"
					sys.stdout.flush()
					os_call = GATK_INTERVAL_PATH+" "+normal_directory+"/"+normal_bam_file[i]+" "+bedfile_name
					os.system(os_call)
					os_call = GATK_INTERVAL_PATH+" "+tumor_directory+"/"+tumor_bam_file[i]+" "+bedfile_name
					os.system(os_call)
				else:
					print "Calling GATK pipeline on the normal and tumor bams"
					print "-------------------------------------------------------------"
					sys.stdout.flush()
					os_call = GATK_PATH+" "+normal_directory+"/"+normal_bam_file[i]
					os.system(os_call)
					os_call = GATK_PATH+" "+tumor_directory+"/"+tumor_bam_file[i]
					os.system(os_call)

				# Make directory for storing the recalibrated bams
				normal_recalibrated_directory = directory + "/recalibrated_bams" + "/" + sample_name[i] + "_NL"
				tumor_recalibrated_directory = directory + "/recalibrated_bams" + "/" + sample_name[i] + "_TU"
				os.makedirs(normal_recalibrated_directory)
				os.makedirs(tumor_recalibrated_directory)
				# Copy the recalibrated bams to the required directory
				sys.stdout.flush()
				os_call = "cp "+normal_directory+"/"+"out.recal.quality.bam"+" "+normal_recalibrated_directory+"/"
				print "Copying recalibrated normal file to the recalibrated folder"
				os.system(os_call)
				os_call = "cp "+normal_directory+"/"+"out.recal.quality.bam.bai"+" "+normal_recalibrated_directory+"/"
				print "Copying recalibrated tumor file to the recalibrated folder"
				os.system(os_call)
				sys.stdout.flush()
				os_call = "cp "+tumor_directory+"/"+"out.recal.quality.bam"+" "+tumor_recalibrated_directory+"/"
				os.system(os_call)
				os_call = "cp "+tumor_directory+"/"+"out.recal.quality.bam.bai"+" "+tumor_recalibrated_directory+"/"
				os.system(os_call)

				#-------------------------------------------------------------#
				# Copy the recalibrated files to the original path
				#-------------------------------------------------------------#

				sys.stdout.flush()
				print "Copying recalibrated normal bam files to HOPP storage server"
				os_call = "cp"+" "+normal_recalibrated_directory+"/out.recal.quality.bam"+" "+path[0]+"/"+"recalibrated-"+normal_bam_file[i]
				os.system(os_call)
				os_call = "cp"+" "+normal_recalibrated_directory+"/out.recal.quality.bam.bai"+" "+path[0]+"/"+"recalibrated-"+normal_bam_file[i]+".bai"
				os.system(os_call)
				print "Copying recalibrated tumor bam files to HOPP storage server"
				sys.stdout.flush()
				os_call = "cp"+" "+tumor_recalibrated_directory+"/out.recal.quality.bam"+" "+path[0]+"/"+"recalibrated-"+tumor_bam_file[i]
				os.system(os_call)
				os_call = "cp"+" "+tumor_recalibrated_directory+"/out.recal.quality.bam.bai"+" "+path[0]+"/"+"recalibrated-"+tumor_bam_file[i]+".bai"
				os.system(os_call)
			else:
				# If there is no recalibration necessary, make directories for storing the recalibrated bams
				normal_recalibrated_directory = directory + "/recalibrated_bams" + "/" + sample_name[i] + "_NL"
				tumor_recalibrated_directory = directory + "/recalibrated_bams" + "/" + sample_name[i] + "_TU"
				os.makedirs(normal_recalibrated_directory)
				os.makedirs(tumor_recalibrated_directory)
				# Copy the recalibrated bams to the required directory
				print "Copying recalibrated normal file to the folder"
				sys.stdout.flush()
				os_call = "cp "+path[0]+"/"+normal_bam_file[i]+" "+normal_recalibrated_directory+"/"+"out.recal.quality.bam"
				os.system(os_call)
				print "Indexing the recalibrated normal bam file"
				sys.stdout.flush()
				os_call = SAM_INDEX_PATH+" "+normal_recalibrated_directory+"/"+"out.recal.quality.bam"
				os.system(os_call)
				print "Copying recalibrated tumor file to the folder"
				sys.stdout.flush()
				os_call = "cp "+path[0]+"/"+tumor_bam_file[i]+" "+tumor_recalibrated_directory+"/"+"out.recal.quality.bam"
				os.system(os_call)
				print "Indexing the recalibrated tumor bam file"
				sys.stdout.flush()
				os_call = SAM_INDEX_PATH+" "+tumor_recalibrated_directory+"/"+"out.recal.quality.bam"
				os.system(os_call)

		#-------------------------------------------------------------#
		# Call somatic sniper and somatic indel detector and mutect
		# depending on the flag. If none specified all the flags are
		# set to 1 and hence all callers will be executed
		#-------------------------------------------------------------#
		
		# Define normal and tumor directories
		normal_recalibrated_directory = directory + "/recalibrated_bams" + "/" + sample_name[i] + "_NL"
		tumor_recalibrated_directory = directory + "/recalibrated_bams" + "/" + sample_name[i] + "_TU"
		recalibrated_normal_file = normal_recalibrated_directory+"/"+"out.recal.quality.bam"
		recalibrated_tumor_file = tumor_recalibrated_directory+"/"+"out.recal.quality.bam"

		# Check if the recalibrated files exists
		if not os.path.exists(recalibrated_normal_file):
			print 'Recalibrated normal file  not existant'
			sys.exit(1)
		if not os.path.exists(recalibrated_tumor_file):
			print 'Recalibrated tumor file  not existant'
			sys.exit(1)
		# Check of the appropriate callers are present and if so make calls	
		if (somatic_sniper_flag == 1):
			print "-------------------------------------------------------------"
			print "Calling somatic mutations using Somatic Sniper"
			sys.stdout.flush()
			os_call = SOMATIC_SNIPER_PATH+" "+tumor_recalibrated_directory+" "+normal_recalibrated_directory+" "+somatic_sniper_directory+" "+sample_name[i]
			os.system(os_call)
		if (somatic_indel_flag == 1):
			if (bedfile_flag == 1):
				print "-------------------------------------------------------------"
				print "Calling somatic indels with intervals list"
				print "-------------------------------------------------------------"
				sys.stdout.flush()
				os_call = SOMATIC_INDEL_INTERVAL_PATH+" "+normal_recalibrated_directory+" "+tumor_recalibrated_directory+" "+somatic_indel_directory+" "+sample_name[i]+" "+bedfile_name
				os.system(os_call)
			else:
				print "-------------------------------------------------------------"
				print "Calling somatic indels"
				print "-------------------------------------------------------------"
				sys.stdout.flush()
				os_call = SOMATIC_INDEL_PATH+" "+normal_recalibrated_directory+" "+tumor_recalibrated_directory+" "+somatic_indel_directory+" "+sample_name[i]
				os.system(os_call)
		if (mutect_flag == 1):
			if (bedfile_flag == 1):
				print "-------------------------------------------------------------"
				print "Calling muTect with intervals list"
				print "-------------------------------------------------------------"
				sys.stdout.flush()
				os_call = MUTECT_INTERVAL_PATH+" "+tumor_recalibrated_directory+" "+normal_recalibrated_directory+" "+mutect_directory+" "+sample_name[i]+" "+bedfile_name
				os.system(os_call)
			else:
				print "-------------------------------------------------------------"
				print "Calling muTect"
				print "-------------------------------------------------------------"
				sys.stdout.flush()
				os_call = MUTECT_PATH+" "+tumor_recalibrated_directory+" "+normal_recalibrated_directory+" "+mutect_directory+" "+sample_name[i]
				os.system(os_call)
		if (unified_genotyper_flag == 1):
			if (bedfile_flag == 1):
				print "-------------------------------------------------------------"
				print "Calling Unified Genotyper with intervals list"
				print "-------------------------------------------------------------"
				sys.stdout.flush()
				os_call = UNIFIED_GENOTYPER_INTERVAL_PATH+" "+tumor_recalibrated_directory+" "+normal_recalibrated_directory+" "+unified_genotyper_directory+" "+sample_name[i]+" "+bedfile_name
				os.system(os_call)
			else:
				print "-------------------------------------------------------------"
				print "Calling Unified Genotyper on all intervals"
				print "-------------------------------------------------------------"
				sys.stdout.flush()
				os_call = UNIFIED_GENOTYPER_PATH+" "+tumor_recalibrated_directory+" "+normal_recalibrated_directory+" "+unified_genotyper_directory+" "+sample_name[i]
				os.system(os_call)
else:
	print 'Sample information file is non-existent. Please make sure you give valid sample info file with path.'
	sys.exit(1)
