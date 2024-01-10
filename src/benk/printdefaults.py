#!/usr/bin/env python3
#
# Copyright 2024 Hewlett Packard Enterprise Development LP.
#

from manageresources import ManageResources

benk = ManageResources(None)

sorted_params = list(benk.config.keys())

sorted_params.sort()

print('# Benk defaults\n\
#\n\
# Note: Some parameters may not have been implemented yet\n\
#')

for k in sorted_params:
    if not benk.config.get(k):
        benk.config[k] = ''
    print('# {key}={value}'.format(value=benk.config.get(k), key=k))
