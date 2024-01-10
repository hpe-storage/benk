#!/usr/bin/env python3
#
# Copyright 2024 Hewlett Packard Enterprise Development LP.
#

import os
import re
import time
import copy
import threading
import yaml
import json
import traceback # FIXME get a debug parm that dumps all exceptions or learn how to use exceptions properly
from pathlib import Path
from dotenv import load_dotenv
from kubernetes import utils,client
from kubernetes.client.rest import ApiException

class ManageResources:
    def __init__(self, apiref):
        self.api = apiref
        self.res_prefix = 'benk'
        self.workload_type = ''

        # Load configs
        load_dotenv()

        # Special treatment for PVC annotations
        re_pvc_annotations = r'(\w+)=(\w+)'
        pvc_annotations = dict(re.findall(re_pvc_annotations, os.getenv('pvcAnnotations', default='')))
        set_pvc_annotations = pvc_annotations if pvc_annotations else ''

        self.config = {
            'pvcAnnotations': set_pvc_annotations,
            'workloadWorkingSetSize': os.getenv('workloadWorkingSetSize', default='4G'),
            'workloadBlockSize': os.getenv('workloadBlockSize', default='8k'),
            'workloadPVCs': os.getenv('workloadPVCs', default='1'),
            'workloadController': os.getenv('workloadController', default='deployment'),
            'workloadReplicas': os.getenv('workloadReplicas', default='1'),
            'workloadInstances': os.getenv('workloadInstances', default='1'),
            'workloadPattern': os.getenv('workloadPattern', default='randrw'),
            'workloadReadPercentage': os.getenv('workloadReadPercentage', default='80'),
            'workloadRuntime': os.getenv('workloadRuntime', default='30'),
            'workloadThreads': os.getenv('workloadThreads', default='1'),
            'workloadIODepth': os.getenv('workloadIODepth', default='1'),
            'workloadDirectIO': os.getenv('workloadDirectIO', default='1'),
            'workloadNoOp': os.getenv('workloadNoOp', default=''),
            'workloadExtraArgs': os.getenv('workloadExtraArgs', default=''),
            'workloadDeleteFiles': os.getenv('workloadDeleteFiles', default='0'),
            'pvcVolumeMode': os.getenv('pvcVolumeMode', default='Filesystem'),
            'pvcAccessMode': os.getenv('pvcAccessMode', default='ReadWriteOnce'),
            'pvcVolumeSize': os.getenv('pvcVolumeSize', default='9Gi'),
            'pvcDataSourceName': os.getenv('pvcDataSourceName', default=''),
            'pvcDataSourceKind': os.getenv('pvcDataSourceKind', default=''),
            'pvcStorageClassName': os.getenv('pvcStorageClassName', default='benk'),
            'pvcPersistPVC': os.getenv('pvcPersistPVC', default=''),
            'benkApiRetries': os.getenv('benkApiRetries', default='4800'),
            'benkApiDelay': os.getenv('benkApiDelay', default='0.75'),
            'benkNamespace': os.getenv('benkNamespace', default='benk'),
            'benkTemplates': os.getenv('benkTemplates', default='/templates'),
            'benkControllerFile': '{directory}/{ctrlr}.yaml'.format(directory=os.getenv('benkTemplates', default='templates'), ctrlr=os.getenv('workloadController', default='deployment')),
            'benkImage': os.getenv('benkImage', default='quay.io/datamattsson/benk:v0.0.0'),
            'benkImagePullPolicy': os.getenv('benkImagePullPolicy', default='Always'),
            'benkMountPath': os.getenv('benkMountPath', default='/data/{prefix}-{pvc}'),
            'benkPVCName': os.getenv('benkPVCName', default='{prefix}-{controller}-{pvc}'),
            'benkControllerName': os.getenv('benkPVCName', default='{prefix}-{controller}'),
            'benkWaitForPVCs': os.getenv('benkWaitForPVCs', default=''),
            'sutServiceName': os.getenv('sutServiceName', default=''),
            'sutBackendIP': os.getenv('sutBackendIP', default=''),
        }

    def _create(self, resource):
        try:
            utils.create_from_dict(self.api, resource)
        except Exception as e: 
            pass

    def _delete(self, resource, api, kind):

        if api == 'core':
            klient = client.CoreV1Api(self.api)
        if api == 'apps':
            klient = client.AppsV1Api(self.api)

        try:
            if kind == 'Deployment':
                klient.delete_namespaced_deployment(resource.get('name'), self.config.get('benkNamespace'))
            if kind == 'PersistentVolumeClaim':
                klient.delete_namespaced_persistent_volume_claim(resource.get('name'), self.config.get('benkNamespace'))
        except ApiException as e:
            pass

    def _submit_for_deletion(self, resources, api, kind):

        if api == 'core':
            klient = client.CoreV1Api(self.api)
        if api == 'apps':
            klient = client.AppsV1Api(self.api)
                
        namespace = self.config.get('benkNamespace')

        # populate pvs on claim data
        if kind == 'PersistentVolumeClaim':
            for r in range(len(resources['data'])):
                handle = klient.read_namespaced_persistent_volume_claim(resources['data'][r].get('name'), namespace)
                resources['data'][r]['pv'] = handle.spec.volume_name

        submissions = {}
        epoch = time.time()
        threads = [] # was in for loop below FIXME

        for r in range(len(resources['data'])):
            
            execute = threading.Thread(target=self._delete, args=(resources['data'][r], api, kind))
            threads.append(execute)
            submissions[resources['data'][r].get('name')] = time.time() 
            execute.start()

        for r, thread in enumerate(threads):
            thread.join()

        wait_for = int(self.config.get('benkApiRetries'))
        deleted = copy.deepcopy(resources)

        while wait_for and len(deleted['data']) > 0:
            for r in range(len(resources['data'])):
                res_name = resources['data'][r].get('name')

                try: 
                    if kind == 'PersistentVolumeClaim':
                        klient.read_persistent_volume(resources['data'][r].get('pv'))
                    
                    if kind == 'Deployment':
                        # FIXME wait for the pods to be removed
                        klient.read_namespaced_deployment(res_name, namespace)
                except ApiException as e:
                    if str(e.status) == '404':
                        if not resources['data'][r].get('deleted'):
                            resources['data'][r]['deleted'] = time.time() - submissions[res_name]

                            for d in range(len(deleted['data'])):
                                if deleted['data'][d]['name'] == res_name:
                                    del deleted['data'][d] 
                                    break
                    pass

            time.sleep(float(self.config.get('benkApiDelay')))
            wait_for -= 1

        resources['metadata']['destruction']['runtime'] = time.time() - epoch

        return resources

    def _submit_for_creation(self, resources, api):

        if api == 'core':
            klient = client.CoreV1Api(self.api)
        if api == 'apps':
            klient = client.AppsV1Api(self.api)

        submissions = {}
        epoch = time.time()
        threads = [] # was in for below FIXME

        for r in range(len(resources)):
            execute = threading.Thread(target=self._create, args=(resources[r],))
            threads.append(execute)
            submissions[resources[r].get('metadata').get('name')] = time.time() 
            execute.start()

        for r, thread in enumerate(threads):
            thread.join()

        wait_for = int(self.config.get('benkApiRetries'))

        results = { 'data': [], 'metadata': { 'provisioned': {}, 'destruction': {} } }

        namespace = self.config.get('benkNamespace')

        while wait_for and resources:
            for r in resources:
                res_name = r.get('metadata').get('name')

                try:
                    if r.get('kind') == 'PersistentVolumeClaim':
                    
                        handle = klient.read_namespaced_persistent_volume_claim(res_name, namespace)
                    
                        if handle.status.phase == 'Bound' or not self.config.get('benkWaitForPVCs'):
                            result = { 'name': res_name, 
                                       'provisioned': time.time() - submissions[res_name] }
                            results['data'].append(result)
                            resources.remove(r)
                    
                    if r.get('kind') == 'Deployment':
                        handle = klient.read_namespaced_deployment(res_name, namespace)
                        
                        if handle.status.available_replicas == int(self.config.get('workloadReplicas')):
                            result = { 'name': res_name, 
                                       'provisioned': time.time() - submissions[res_name] }
                            results['data'].append(result)
                            resources.remove(r)
                except:
                    pass

            time.sleep(float(self.config.get('benkApiDelay')))
            wait_for -= 1

        results['metadata']['provisioned']['runtime'] = time.time() - epoch
        return results

    def create_pvcs(self):

        results = {}

        pvc = { 
               'apiVersion': 'v1',
               'kind': 'PersistentVolumeClaim',
               'metadata': {}, # FIXME annotations, Namespace below!
               'spec': {
                   'accessModes': [ self.config.get('pvcAccessMode') ],
                   'resources': {
                       'requests': {
                           'storage': self.config.get('pvcVolumeSize'),
                           },
                       },
                   'storageClassName': self.config.get('pvcStorageClassName'),
                   },
               }

        pvcs = []
 
        for c in range(int(self.config['workloadInstances'])):
            for r in range(int(self.config['workloadPVCs'])):
                new_pvc = copy.deepcopy(pvc)
                # FIXME don't concatenate the string, use .format on the correct config template
                new_pvc['metadata']['name'] = self.res_prefix + '-' + str(c) + '-' + str(r)
                new_pvc['metadata']['namespace'] = self.config.get('benkNamespace')
                pvcs.append(new_pvc)

        results = self._submit_for_creation(pvcs, 'core')

        return results

    def destroy_pvcs(self, pvcs):
        if self.config.get('pvcPersistPVC'):
            return pvcs
        
        results = self._submit_for_deletion(pvcs, 'core', 'PersistentVolumeClaim')
        return results

    def create_controllers(self):

        results = {}

        controller = yaml.safe_load(Path(self.config.get('benkControllerFile')).read_text())

        if self.config.get('workloadController') == 'deployment':
            self.workload_type = 'Deployment'
            controller['metadata']['namespace'] = self.config.get('benkNamespace')
            controller['spec']['replicas'] = int(self.config.get('workloadReplicas'))
            controller['spec']['template']['spec']['containers'][0]['imagePullPolicy'] = self.config.get('benkImagePullPolicy')
            controller['spec']['template']['spec']['containers'][0]['image'] = self.config.get('benkImage')
            if self.config.get('pvcVolumeMode') == 'Filesystem':
                controller['spec']['template']['spec']['containers'][0]['volumeMounts'] = []
            if self.config.get('pvcVolumeMode') == 'Block':
                controller['spec']['template']['spec']['containers'][0]['volumeDevices'] = []

        controllers = []
        
        for c in range(int(self.config['workloadInstances'])):
            new_controller = copy.deepcopy(controller)
            new_controller['metadata']['name'] = self.config.get('benkControllerName').format(prefix=self.res_prefix, controller=str(c))
            new_controller['metadata']['namespace'] = self.config.get('benkNamespace')
            new_controller['spec']['template']['spec']['volumes'] = []

            for p in range(int(self.config['workloadPVCs'])):
                if self.config.get('pvcVolumeMode') == 'Filesystem':

                    present = {}

                    present['mountPath'] = self.config.get('benkMountPath').format(prefix=self.res_prefix,
                                                                                   pvc=str(p))

                    present['name'] = self.config.get('benkPVCName').format(prefix=self.res_prefix,
                                                                            controller=str(c),
                                                                            pvc=str(p))

                    new_controller['spec']['template']['spec']['containers'][0]['volumeMounts'].append(present) 

                if self.config.get('pvcVolumeMode') == 'Block':
                    # FIXME
                    present = {}
                    controller['spec']['template']['spec']['volumeDevices'].append(present)

                pvc = {}
                pvc['name'] = present['name']
                pvc['persistentVolumeClaim'] = { 'claimName': present['name'] }

                new_controller['spec']['template']['spec']['volumes'].append(pvc)
            controllers.append(new_controller)

        results = self._submit_for_creation(controllers, 'apps')
        return results

    def destroy_controllers(self, controllers):
        results = self._submit_for_deletion(controllers, 'apps', self.workload_type)
        return results
