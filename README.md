## High throughput genomic sequencing pipeline
### Installation
When cloning this repo for the first time you must install the necessary tools.
1. Create a 'tools' directory in the root folder
2. Place a copy of annovar, samtools, etc.

### Executing the script
production run: `python call-mutations-indels.py -s sample_info.txt -p path_file.txt -d outputdir [-b intervals.maf]`

debug run: `python -i call-mutations-indels.py -s sample_info.txt -p path_file.txt -d outputdir [-b intervals.maf]`

This pipeline is currently installed on the hopp-cli server and must be executed from /home/sam/HOPP-Informatics/projects/sequencingPipeline.

### Build reference index (if adding new assembly)
Generate the BWA index
`bwa index -a bwtsw reference.fa`

Generate the fasta file index
`samtools faidx reference.fa`

Generate the sequence dictionary
`java -jar picard.jar /home/sam/tools/picard-tools-1.130/CreateSequenceDictionary REFERENCE=reference.fa OUTPUT=reference.dict`

### Warning
This pipeline is still in development and produces known errors use at your own risk.
