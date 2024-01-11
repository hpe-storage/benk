#!/bin/bash
#
# Copyright 2024 Hewlett Packard Enterprise Development LP.
#

if [[ -z ${1} ]]; then
	echo "Usage: $(basename ${0}) <overlay> <staggered starts in seconds>"
	exit 1
fi

if ! mkdir -p ${BENK_OUTPUT_LOCATION:=$(pwd)/logs}; then
	echo "Unable to log to ${BENK_OUTPUT_LOCATION}"
	exit 1
fi

overlay=kustomize/overlays/${1}

if ! [[ -d ${overlay} ]]; then
	echo "Error: overlay (${overlay}) doesn't exist"
	exit 1
fi

clusters=$(ls cluster-* | wc -l | awk '{print $1}')
now=$(date +%Y%m%d%H%M%S)

# Non-staggered starts
if [[ -z ${2} ]]; then
	for c in cluster-[1-${clusters}]-kubeconfig; do
		if ! [[ -e ${c} ]]; then
			echo "Error: kubeconfig (${c}) doesn't exist"
			exit 1
		fi
		export KUBECONFIG=${c}

		# Replace
		kubectl replace --force -k ${overlay} &
	done

	wait

	for c in cluster-[1-${clusters}]-kubeconfig; do
		export KUBECONFIG=${c}
		# Wait
		kubectl wait --for=condition=complete --timeout=7200s -n benk job/benk

		# Extract
		kubectl -n benk logs job/benk | tee -a ${BENK_OUTPUT_LOCATION}/run-${1}-${c}-${now}.log
	done
# Staggered starts
else
	for c in cluster-[1-${clusters}]-kubeconfig; do
		if ! [[ -e ${c} ]]; then
			echo "Error: kubeconfig (${c}) doesn't exist"
			exit 1
		fi
		export KUBECONFIG=${c}

		# Replace
		kubectl replace --force -k ${overlay}
		sleep ${2}
	done

	for c in cluster-[1-${clusters}]-kubeconfig; do
		export KUBECONFIG=${c}
		# Wait
		kubectl wait --for=condition=complete --timeout=7200s -n benk job/benk

		# Extract
		kubectl -n benk logs job/benk | tee -a ${BENK_OUTPUT_LOCATION}/run-${1}-${now}.log
	done
fi
