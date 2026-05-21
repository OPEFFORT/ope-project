# CONTAINERS

This directory contains the source for containers that are part of your project.

## Container Categories

### Student Environment Containers

These containers provide JupyterLab environments for students to work with course content:

- **default/**: Complete course environment with JupyterLab and course materials
- **testing/**: Testing variant of the student environment

These containers are built using the OPE framework Makefiles and can be customized by editing requirements files.

### RHOAI Automation Containers

These containers provide services for OpenShift AI infrastructure automation:

- **assign-class-label/**: Flask webhook service for automatic pod class label assignment
- **group-sync/**: OpenShift group synchronization service

These containers are deployed as Kubernetes services and cronjobs. See `deployment/` directory for deployment manifests.
