#!/bin/bash

# Takes a list of R packages from the output of installed.packages() and 
# creates an output file with the extracted package names

OUT="packages.txt"	# output file

if [ ! $# -eq 1 ]; then
	printf "Usage: read-packages <file>\n\n"
	exit 1
fi

while read -r line; do
	line=$(echo $line | sed 's/[\s]*\".*"$//')
	echo $line >> $OUT
done < "$1"
