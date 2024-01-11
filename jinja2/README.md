Jinja2 templates are used to translate the JSON output from benk to a desired data structure. TSV and CSV are simple to paste into a spreadsheet. For more comprehensive, structured and automated benchmarks, SQL or any other database may be more practical.

This log entry may be used as a boilerplate to write templates. The outputter from benk provide different set of variables to Jinja depending on if it's a single log file being processed or two. Check out the example templates for details.

```json
{
  "benk": {
    "controllers": {
      "data": [
        {
          "name": "benk-0",
          "provisioned": 13.121052503585815,
          "deleted": 0.036958932876586914
        }
      ],
      "metadata": {
        "provisioned": {
          "runtime": 13.87154221534729,
          "min": 13.121052503585815,
          "max": 13.121052503585815,
          "mean": 13.121052503585815,
          "median": 13.121052503585815,
          "stdev": 0
        },
        "destruction": {
          "runtime": 0.7882373332977295,
          "min": 0.036958932876586914,
          "max": 0.036958932876586914,
          "mean": 0.036958932876586914,
          "median": 0.036958932876586914,
          "stdev": 0
        }
      }
    },
    "pvcs": {
      "data": [
        {
          "name": "benk-0-0",
          "provisioned": 0.04697132110595703,
          "pv": "pvc-b0e554c1-f418-49bf-8060-eb3fe236813b",
          "deleted": 39.75776433944702
        }
      ],
      "metadata": {
        "provisioned": {
          "runtime": 0.7978861331939697,
          "min": 0.04697132110595703,
          "max": 0.04697132110595703,
          "mean": 0.04697132110595703,
          "median": 0.04697132110595703,
          "stdev": 0
        },
        "destruction": {
          "runtime": 40.508225202560425,
          "min": 39.75776433944702,
          "max": 39.75776433944702,
          "mean": 39.75776433944702,
          "median": 39.75776433944702,
          "stdev": 0
        }
      }
    },
    "metadata": {
      "provisioning": {
        "runtime": 14.681398630142212,
        "seconds/pvc": 14.681398630142212,
        "seconds/workload": 14.681398630142212
      },
      "destruction": {
        "runtime": 41.30830693244934,
        "seconds/pvc": 41.30830693244934,
        "seconds/workload": 41.30830693244934
      },
      "io": {
        "fill": 10.022749662399292,
        "load": 31.245493173599243
      },
      "runtime": 97.25799250602722,
      "parameters": {
        "config": {
          "pvcAnnotations": "",
          "workloadWorkingSetSize": "4G",
          "workloadBlockSize": "8k",
          "workloadPVCs": "1",
          "workloadController": "deployment",
          "workloadReplicas": "1",
          "workloadInstances": "1",
          "workloadPattern": "randrw",
          "workloadReadPercentage": "80",
          "workloadRuntime": "30",
          "workloadThreads": "1",
          "workloadIODepth": "1",
          "workloadDirectIO": "1",
          "workloadNoOp": "",
          "workloadExtraArgs": "",
          "workloadDeleteFiles": "0",
          "pvcVolumeMode": "Filesystem",
          "pvcAccessMode": "ReadWriteOnce",
          "pvcVolumeSize": "9Gi",
          "pvcDataSourceName": "",
          "pvcDataSourceKind": "",
          "pvcStorageClassName": "benk",
          "pvcPersistPVC": "",
          "benkApiRetries": "4800",
          "benkApiDelay": "0.75",
          "benkNamespace": "benk",
          "benkTemplates": "/templates",
          "benkControllerFile": "templates/deployment.yaml",
          "benkImage": "quay.io/datamattsson/benk:v0.0.1",
          "benkImagePullPolicy": "IfNotPresent",
          "benkMountPath": "/data/{prefix}-{pvc}",
          "benkPVCName": "{prefix}-{controller}-{pvc}",
          "benkControllerName": "{prefix}-{controller}",
          "benkWaitForPVCs": "",
          "sutServiceName": "alletra6000-csp-svc",
          "sutBackendIP": "192.168.1.1",
          "runtimeWorkloadPhase": "0",
          "runtimeWorkloadFiles": "/data/benk-0/${HOSTNAME}-f.io"
        }
      }
    },
    "fio": {
      "data": {
        "jobname": "benk",
        "groupid": 0,
        "error": 0,
        "job options": {
          "rw": "randrw",
          "rwmixread": "80",
          "bs": "8k",
          "direct": "1",
          "time_based": "1",
          "runtime": "30",
          "create_only": "0",
          "numjobs": "1",
          "iodepth": "1",
          "group_reporting": "1",
          "unlink": "0"
        },
        "read": {
          "io_bytes": 315400192,
          "io_kbytes": 308008,
          "bw_bytes": 10512989,
          "bw": 10266,
          "iops": 1283.323889,
          "runtime": 30001,
          "total_ios": 38501,
          "short_ios": 0,
          "drop_ios": 0,
          "slat_ns": {
            "min": 0,
            "max": 0,
            "mean": 0,
            "stddev": 0,
            "N": 0
          },
          "clat_ns": {
            "min": 249871,
            "max": 22076546,
            "mean": 648782.315654,
            "stddev": 447936.209889,
            "N": 38501,
            "percentile": {
              "1.000000": 342016,
              "5.000000": 382976,
              "10.000000": 403456,
              "20.000000": 440320,
              "30.000000": 468992,
              "40.000000": 501760,
              "50.000000": 544768,
              "60.000000": 716800,
              "70.000000": 782336,
              "80.000000": 823296,
              "90.000000": 872448,
              "95.000000": 929792,
              "99.000000": 1499136,
              "99.500000": 2277376,
              "99.900000": 5668864,
              "99.950000": 7962624,
              "99.990000": 21364736
            }
          },
          "lat_ns": {
            "min": 250161,
            "max": 22077134,
            "mean": 649402.026805,
            "stddev": 447957.862995,
            "N": 38501
          },
          "bw_min": 8576,
          "bw_max": 12960,
          "bw_agg": 100,
          "bw_mean": 10281.440678,
          "bw_dev": 1107.554829,
          "bw_samples": 59,
          "iops_min": 1072,
          "iops_max": 1620,
          "iops_mean": 1285.101695,
          "iops_stddev": 138.471172,
          "iops_samples": 59
        },
        "write": {
          "io_bytes": 79601664,
          "io_kbytes": 77736,
          "bw_bytes": 2653300,
          "bw": 2591,
          "iops": 323.889204,
          "runtime": 30001,
          "total_ios": 9717,
          "short_ios": 0,
          "drop_ios": 0,
          "slat_ns": {
            "min": 0,
            "max": 0,
            "mean": 0,
            "stddev": 0,
            "N": 0
          },
          "clat_ns": {
            "min": 289121,
            "max": 19080027,
            "mean": 489290.420397,
            "stddev": 411849.307849,
            "N": 9717,
            "percentile": {
              "1.000000": 350208,
              "5.000000": 382976,
              "10.000000": 399360,
              "20.000000": 419840,
              "30.000000": 432128,
              "40.000000": 444416,
              "50.000000": 460800,
              "60.000000": 473088,
              "70.000000": 485376,
              "80.000000": 505856,
              "90.000000": 536576,
              "95.000000": 585728,
              "99.000000": 970752,
              "99.500000": 1384448,
              "99.900000": 5603328,
              "99.950000": 12648448,
              "99.990000": 19005440
            }
          },
          "lat_ns": {
            "min": 289428,
            "max": 19080858,
            "mean": 490238.530205,
            "stddev": 411882.327226,
            "N": 9717
          },
          "bw_min": 2032,
          "bw_max": 3585,
          "bw_agg": 100,
          "bw_mean": 2599.20339,
          "bw_dev": 352.283819,
          "bw_samples": 59,
          "iops_min": 254,
          "iops_max": 448,
          "iops_mean": 324.847458,
          "iops_stddev": 44.052404,
          "iops_samples": 59
        },
        "job_runtime": 30000,
        "usr_cpu": 0.986667,
        "sys_cpu": 4.87,
        "ctx": 48666,
        "majf": 0,
        "minf": 12,
        "iodepth_level": {
          "1": 100,
          "2": 0,
          "4": 0,
          "8": 0,
          "16": 0,
          "32": 0,
          ">=64": 0
        },
        "iodepth_submit": {
          "0": 0,
          "4": 100,
          "8": 0,
          "16": 0,
          "32": 0,
          "64": 0,
          ">=64": 0
        },
        "iodepth_complete": {
          "0": 0,
          "4": 100,
          "8": 0,
          "16": 0,
          "32": 0,
          "64": 0,
          ">=64": 0
        },
        "latency_ns": {
          "2": 0,
          "4": 0,
          "10": 0,
          "20": 0,
          "50": 0,
          "100": 0,
          "250": 0,
          "500": 0,
          "750": 0,
          "1000": 0
        },
        "latency_us": {
          "2": 0,
          "4": 0,
          "10": 0,
          "20": 0,
          "50": 0,
          "100": 0,
          "250": 0.01,
          "500": 47.33502,
          "750": 23.18014,
          "1000": 26.892447
        },
        "latency_ms": {
          "2": 2.059397,
          "4": 0.373305,
          "10": 0.118213,
          "20": 0.026961,
          "50": 0.012443,
          "100": 0,
          "250": 0,
          "500": 0,
          "750": 0,
          "1000": 0,
          "2000": 0,
          ">=2000": 0
        },
        "latency_depth": 1,
        "latency_target": 0,
        "latency_percentile": 100,
        "latency_window": 0,
        "hostname": "192.168.252.46",
        "port": 8765
      },
      "metadata": {
        "version": "fio-3.34",
        "timestamp": "1704916010",
        "time": "Wed Jan 10 19:46:50 2024",
        "global": {
          "size": "4G",
          "filename": "/data/benk-0/benk-0-7685568796-kvqhh-f.io"
        },
        "stderr": "",
        "job": {
          "rw": "randrw",
          "rwmixread": "80",
          "bs": "8k",
          "direct": "1",
          "time_based": "1",
          "runtime": "30",
          "create_only": "0",
          "numjobs": "1",
          "iodepth": "1",
          "group_reporting": "1",
          "unlink": "0"
        }
      }
    }
  },
  "log": [
    "Using in-cluster config"
  ]
}
```
