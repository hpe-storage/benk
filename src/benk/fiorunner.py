#!/usr/bin/env python3
#
# Copyright 2024 Hewlett Packard Enterprise Development LP.
#

from time import sleep
from subprocess import run
from os import environ
from kubernetes import utils,client
import traceback
import json

class FioRunner:
    def __init__(self, benk):
        self.api = benk.api
        self.config = benk.config
        self.unlink = self.config.get('workloadDeleteFiles')

        klient = client.CoreV1Api(self.api)

        retries = int(benk.config.get('benkApiRetries'))
        ips = []
        
        while retries:
            pods = klient.list_namespaced_pod(benk.config.get('benkNamespace'), label_selector='app=benk')
        
            for pod in pods.items:
                if pod.status.pod_ip:
                    ips.append(pod.status.pod_ip)

            if all(ips) and len(ips) == (int(benk.config.get('workloadInstances')) * int(benk.config.get('workloadReplicas'))):
                # print(_fio_line(benk, _workload_filenames(benk), ips, 1))
                break
            else:
                sleep(float(benk.config.get('benkApiDelay', '1')))
                retries -= 1
                ips = []

        self.servers = ips
        self.files = self._workload_filenames()

    def _fio_line(self, fill):
        cmd = []
        
        # Fill or Run
        if fill:
            self.config['runtimeWorkloadPhase'] = '1'
            self.config['workloadDeleteFiles'] = '0' 
        else:
            self.config['runtimeWorkloadPhase'] = '0'
            self.config['workloadDeleteFiles'] = self.unlink

        # Files
        self.config['runtimeWorkloadFiles'] = self.files

        # Fio and args
        cmd.append('fio')
        cmd.append('{path}/fiospec.ini'.format(path=self.config.get('benkTemplates')))
        cmd.append('--output-format=json')

        if self.config.get('workloadExtraArgs'):
            cmd.append(self.config.get('workloadExtraArgs'))

        # Servers
        for server in self.servers:
            cmd.append('--client={ip}'.format(ip=server))

        # Clean up
        cmd.append('|')
        cmd.append('grep')
        cmd.append('-v')
        cmd.append("^'<'")

        return ' '.join(cmd)

    def _workload_filenames(self):
        files = []

        for file in range(int(self.config.get('workloadPVCs'))):
            if self.config.get('pvcPersistPVC') and self.config.get('workloadDeleteFiles') == "0":
                fio = '%s/f.io' % file
            else:
                fio = '%s/${HOSTNAME}-f.io' % file

            files.append(self.config.get('benkMountPath').format(prefix='benk', pvc=fio))

        return ':'.join(files)

    def _run(self, cmd):
        raw = {}
        results = {}
        environ.update(self.config)
        
        shell = run(cmd, shell=True, check=False, capture_output=True, env=environ) 
        raw = json.loads(shell.stdout)

        results['data'] = raw.get('client_stats')[-1]
        results['data'].pop('trim')
        results['data'].pop('sync')
        results['metadata'] = {
                    'version': raw.get('fio version'),
                    'timestamp': str(raw.get('timestamp')),
                    'time': raw.get('time'),
                    'global': raw.get('global options'),
                    'stderr': shell.stderr.decode('utf-8'),
                    'job': raw.get('client_stats')[0].get('job options'),
                }
        return results
    
    def fill(self):
        results = {}
        results = self._run(self._fio_line(True))

        return results

    def load(self):
        results = {}
        results = self._run(self._fio_line(False))

        return results
