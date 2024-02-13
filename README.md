![](assets/benk-light-bg.png)

Benk, like benchmark, but with a K(8s). You may use it to run Benchmark Experiments Nurtured on Kubernetes.

# Overview

Benk is a kitchen sink for running storage provisioning and I/O benchmark experiments on Kubernetes. This project is work in progress. Features are missing and the user experience is rough around the edges. You can help by [contributing](CONTRIBUTING.md), filing an [issue](https://github.com/hpe-storage/benk/issues) or contribute your insights on current issues. Look at the [examples](examples) for insights on what benk can do.

Usage boils down to three phases:

1. **Configuration:** Workload counts and I/O behavior (I/O testing is optional)
1. **Running:** Single experiment or sequence multiple experiments (limited by bash glob expansion)
1. **Reporting:** Use Jinja2 [templates](jinja2) to process logs and customize the output for reporting

Benk uses [FIO](https://github.com/axboe/fio) in client and server mode.

# Synopsis

Starter examples below. Build your own library of configuration files and reporting templates. A walkthrough of some of these examples are available in a blog post on HPE Developer Community.

- [Working with Benk: A storage provisioning and IO performance benchmark suite for Kubernetes](https://developer.hpe.com/blog/working-with-benk-a-storage-provisioning-and-io-performance-benchmark-suite-for-kubernetes/)

## Hello World

Assumes connectivity to a Kubernetes cluster with a storage driver capable of dynamic provisioning is installed and capable of attaching `PersistentVolumes` to worker nodes.

```text
git clone https://github.com/hpe-storage/benk && cd benk
pip3 install -r requirements.txt
cp kustomize/base/config-dist.env kustomize/base/config.env
cp kustomize/base/storageclass-dist.yaml kustomize/base/storageclass.yaml
# Edit kustomize/base/config.env and kustomize/base/storageclass.yaml 
# to fit the environment under test
kubectl create ns benk
kubectl apply -k kustomize/overlays/default
kubectl wait -n benk --timeout=300s --for=condition=complete job/benk
kubectl logs -n benk job/benk | jq
```

Benk's runtime configuration file is [config.env](kustomize/overlays/default/config.env) which is configured per Job.

Two helper shell scripts allows simple sequencing of multiple jobs and the reporter can either report on a single Job or two jobs for easy A/B testing comparison.

### Job scaling (single sequence)

Assumes `kustomize/base/config.env` and `kustomize/base/storagclass.yaml` exists along with a `Namespace` named "benk" on the cluster.

```text
for i in {1..8}; do cp -a kustomize/overlays/default kustomize/overlays/mytest-${i}; done
# Edit kustomize/overlays/mytest-*/config.env for each iteration
./sequencer.sh mytest-
./src/benk/outputter.py -l logs/run-mytest-*.log -t jinja2/example-single.tsv.j2
```

### Job scaling (A/B sequence)

Assumes `kustomize/base/config.env` and `kustomize/base/storagclass.yaml` exists along with a `Namespace` named "benk" on the cluster.

```text
for i in {1..8}; do cp -a kustomize/overlays/default kustomize/overlays/mytest-a-${i}; done
for i in {1..8}; do cp -a kustomize/overlays/default kustomize/overlays/mytest-b-${i}; done
# Edit kustomize/overlays/mytest-*/config.env for each iteration
./sequencer.sh mytest-a-
./sequencer.sh mytest-b-
./src/benk/outputter.py -a logs/run-mytest-a-*.log -b logs/run-mytest-b-*.log -t jinja2/example-ab.tsv.j2
```

### Multi-cluster testing

Assumes `kustomize/base/config.env` and `kustomize/base/storagclass.yaml` exists along with a `Namespace` named "benk" on each cluster.

Running multiple workloads across multiple clusters simultaneously but independently, it's possible to do so by naming kubeconfig files like this: `cluster-N-kubeconfig` where N starts with a "1" sequenced in order up to the last cluster.

It's also possible to stagger the start of each job.

Puts all cluster's logs content in one log file with 15 seconds staggered starts:

```text
./sequencer-cluster.sh default 15
./src/benk/outputter.py -l logs/run-default-mydate.log -t jinja2/example-single.tsv.j2
```

Each cluster has its on log file (omitting staggered starts):

```text
./sequencer-cluster.sh default
./src/benk/outputter.py -a logs/run-default-N-mydate.log -b logs/run-default-N-mydate.log -t jinja2/example-ab.tsv.j2
```

**Note:** It's not possible to run sequences on multiple clusters, single overlays only for now.

# Example Configurations

Benk was born out of a need to collect vast amounts of performance scaling metrics for very particular configurations over a short amount of time. These two first example use cases and configurations illustrate the outcomes.

## Provisioning Performance

The wall times for starting and stopping the workloads are clocked to understand how a storage driver and potential backend behaves under pressure. Pressure in this context means a lot of requests for provisioning and attaching storage to workloads. Benk was used to provision hundreds of PVCs to gauge wall time from submission to running and tearing down.

- [Provisioning Performance](examples/provisioning-performance)

## NFS Server Provisioner IO Performance

The HPE CSI Driver features an NFS Server Provisioner and there were concerns how well it performed under certain circumstances. Benk was used to model standard mixed and four corner benchmarks with various client and server counts to isolate potential bottlenecks.

- [NFS Server Provisioner IO Performance](examples/nfs-io-performance)

See [examples](examples) if you want to contribute examples.

# Building

A Dockerfile and Makefile is readily available to rebuild the image with `docker buildx` targeting amd64 and arm64.

```text
export CONTAINER_REGISTRY=quay.io/yourorg/benk
export IMAGE_TAG=v0.0.1-myimage
make PUSH=--push image
```

A custom image can be set in `kustomize/base/config.env`.

# Contributing

We value all feedback and contributions. If you find any issues or want to contribute, please feel free to open an issue or file a PR. More details in [CONTRIBUTING.md](CONTRIBUTING.md)


# Community

Please file any issues, questions or feature requests you may have [here](https://github.com/hpe-storage/benk/issues) You may also join our Slack community to chat with HPE folks close to this project. We hang out in `#Kubernetes`. Sign up at [slack.hpedev.io](https://slack.hpedev.io/) and login at [hpedev.slack.com](https://hpedev.slack.com/)

# License

This is open source software licensed using the MIT License. Please see [LICENSE](LICENSE.md) for details.
