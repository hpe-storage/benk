#!/usr/bin/env python3
#
# Copyright 2024 Hewlett Packard Enterprise Development LP.
#

import traceback
import json
import sys
import time
from kubernetes import client, config

# Local 
from fiorunner import FioRunner
from manageresources import ManageResources
from reporter import Reporter

def main():

    report = {
                'benk': {}, 
                'log': [],
                }

    metadata = {
                'provisioning': {},
                'destruction': {},
                'io': {},
                }

    try:
        config.load_kube_config()
        report['log'].append('Using kubectl client config')
    except:
        config.load_incluster_config()
        report['log'].append('Using in-cluster config')

    try:
        benk = ManageResources(client.ApiClient())

        epoch = time.time()
        itime = epoch

        # Creation
        pvcs = benk.create_pvcs()
        controllers = benk.create_controllers()
        metadata['provisioning']['runtime'] = time.time() - epoch 
        itime = time.time()

        # Load
        fio = FioRunner(benk)

        if benk.config.get('workloadNoOp'):
            filler = {}
        else:
            filler = fio.fill()
        
        metadata['io']['fill'] = time.time() - itime
        itime = time.time()

        if benk.config.get('workloadNoOp'):
            loader = {}
        else:
            loader = fio.load()

        metadata['io']['load'] = time.time() - itime
        itime = time.time()

        # Destruction
        controllers = benk.destroy_controllers(controllers)
        pvcs = benk.destroy_pvcs(pvcs)
        metadata['destruction']['runtime'] = time.time() - itime
        itime = time.time()

        # Reporting
        metadata['runtime'] = time.time() - epoch
        report['benk'] = Reporter().aggregate(benk, pvcs, controllers, loader, metadata)

    except:
        traceback.print_exc()
        sys.exit(1)

    print(json.dumps(report))

if __name__ == '__main__':
    main()
