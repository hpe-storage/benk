#!/bin/bash
#
# Copyright 2024 Hewlett Packard Enterprise Development LP.
#

if [[ -z ${1} ]]; then
	echo "Usage: $(basename ${0}) <overlay prefix>"
	exit 1
fi

if ! mkdir -p ${BENK_OUTPUT_LOCATION:=$(pwd)/logs}; then
	echo "Unable to log to ${BENK_OUTPUT_LOCATION}"
	exit 1
fi

overlays=kustomize/overlays
now=$(date +%Y%m%d%H%M%S)

for i in ${overlays}/${1}*; do 
	if ! [[ -d ${i} ]]; then
		echo "Error: overlay (${i}) doesn't exist"
		exit 1
	fi

	# Replace
	kubectl replace --force -k ${i}

	# Wait
	kubectl wait --for=condition=complete --timeout=7200s -n benk job/benk
	
	# Extract
	kubectl -n benk logs job/benk | tee -a ${BENK_OUTPUT_LOCATION}/run-${1}${now}.log
done
