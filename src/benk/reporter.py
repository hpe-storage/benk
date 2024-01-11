#!/usr/bin/env python3
#
# Copyright 2024 Hewlett Packard Enterprise Development LP.
#

from statistics import stdev, median, mean

class Reporter:
    def __init__(self):
        self.myvar = 'myvalue'
    def _dataset2list(self, dataset, key):

        results = []

        for r in dataset:
            if r.get(key) == None:
                r[key] = 0
            results.append(r.get(key))

        return results

    def aggregate(self, benk, pvcs, controllers, loader, metadata):

        controllers_provisioned_list = self._dataset2list(controllers.get('data'), 'provisioned')
        controllers_destruction_list = self._dataset2list(controllers.get('data'), 'deleted')

        controllers['metadata']['provisioned']['min'] = min(controllers_provisioned_list)
        controllers['metadata']['provisioned']['max'] = max(controllers_provisioned_list)
        controllers['metadata']['provisioned']['mean'] = mean(controllers_provisioned_list)
        controllers['metadata']['provisioned']['median'] = median(controllers_provisioned_list)
        controllers['metadata']['provisioned']['stdev'] = 0

        controllers['metadata']['destruction']['min'] = min(controllers_destruction_list)
        controllers['metadata']['destruction']['max'] = max(controllers_destruction_list)
        controllers['metadata']['destruction']['mean'] = mean(controllers_destruction_list)
        controllers['metadata']['destruction']['median'] = median(controllers_destruction_list)
        controllers['metadata']['destruction']['stdev'] = 0

        if len(controllers.get('data')) > 1:
            controllers['metadata']['provisioned']['stdev'] = stdev(controllers_provisioned_list)
            controllers['metadata']['destruction']['stdev'] = stdev(controllers_destruction_list)

        pvcs_provisioned_list = self._dataset2list(pvcs.get('data'), 'provisioned')
        pvcs_destruction_list = self._dataset2list(pvcs.get('data'), 'deleted')

        pvcs['metadata']['provisioned']['min'] = min(pvcs_provisioned_list)
        pvcs['metadata']['provisioned']['max'] = max(pvcs_provisioned_list)
        pvcs['metadata']['provisioned']['mean'] = mean(pvcs_provisioned_list)
        pvcs['metadata']['provisioned']['median'] = median(pvcs_provisioned_list)
        pvcs['metadata']['provisioned']['stdev'] = 0
        
        pvcs['metadata']['destruction']['min'] = min(pvcs_destruction_list)
        pvcs['metadata']['destruction']['max'] = max(pvcs_destruction_list)
        pvcs['metadata']['destruction']['mean'] = mean(pvcs_destruction_list)
        pvcs['metadata']['destruction']['median'] = median(pvcs_destruction_list)
        pvcs['metadata']['destruction']['stdev'] = 0
        
        if len(pvcs.get('data')) > 1:
            pvcs['metadata']['destruction']['stdev'] = stdev(pvcs_destruction_list)
            pvcs['metadata']['provisioned']['stdev'] = stdev(pvcs_provisioned_list)

        metadata['provisioning']['seconds/pvc'] = metadata.get('provisioning').get('runtime') / (int(benk.config.get('workloadPVCs')) * int(benk.config.get('workloadInstances')))
        metadata['provisioning']['seconds/workload'] = metadata.get('provisioning').get('runtime') / (int(benk.config.get('workloadInstances')))
        metadata['destruction']['seconds/pvc'] = metadata.get('destruction').get('runtime') / (int(benk.config.get('workloadPVCs')) * int(benk.config.get('workloadInstances')))
        metadata['destruction']['seconds/workload'] = metadata.get('destruction').get('runtime') / (int(benk.config.get('workloadInstances')))
        metadata['parameters'] = {}
        metadata['parameters']['config'] = benk.config

        report = {
                    'controllers': controllers, 
                    'pvcs': pvcs,
                    'metadata': metadata,
                    'fio': loader,
                 }

        return report
