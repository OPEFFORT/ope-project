# RHOAI Deployment Tools

This directory contains Kubernetes manifests and tooling for deploying and managing courses on OpenShift AI (RHOAI) infrastructure.

## Overview

The RHOAI deployment tools provide automated management of student notebooks, user groups, and resource allocation for course environments. These tools are designed to work with OpenShift AI and integrate with ColdFront for user provisioning.


## Components

### CronJobs

All cronjobs run on a schedule (default schedule is hourly: `0 * * * *`) and can be triggered manually using `oc create job --from=cronjob/<name>`.

#### 1. group-sync

**Purpose**: Synchronizes users with edit permissions in a namespace to an OpenShift group.

**Use Case**: Keep ColdFront-provisioned users in sync with OpenShift groups for RBAC and resource quotas.

**Configuration**:
- `GROUP_NAME`: OpenShift group to sync users to
- `NAMESPACE`: Course namespace to watch for edit rolebindings

**Deployment**:
```bash
cd deployment/cronjobs/group-sync/
# Edit cronjob.yaml to set GROUP_NAME and NAMESPACE
# Edit kustomization.yaml to set target namespace
oc apply -k . --as system:admin
```

**Manual Trigger**:
```bash
oc create -n <namespace> job --from=cronjob/group-sync group-sync
```

**Notes**:
- If deploying for multiple classes, update the clusterrolebinding name to avoid conflicts
- Users must have edit rolebinding in the specified namespace to be added to the group

---

#### 2. nb-culler

**Purpose**: Automatically shuts down notebooks that exceed a runtime threshold to conserve resources.

**Use Case**: Prevent students from leaving notebooks running indefinitely, reducing cluster resource consumption.

**Configuration**:
- `GROUP_NAME`: OpenShift group to apply culling to (only affects notebooks owned by group members)
- `CUTOFF_TIME`: Maximum runtime in seconds before shutdown (e.g., `43200` for 12 hours)

**Deployment**:
```bash
cd deployment/cronjobs/nb-culler/
# Edit cronjob.yaml to set GROUP_NAME and CUTOFF_TIME
oc project rhods-notebooks
oc apply -k . --as system:admin
```

**Manual Trigger**:
```bash
oc create -n rhods-notebooks job --from=cronjob/nb-culler nb-culler
```

**Notes**:
- Only affects notebooks in `rhods-notebooks` namespace
- Notebooks are shut down gracefully; PVCs persist
- Different cutoff times can be configured per group

---

#### 3. multiple-ns-group-sync

**Purpose**: Synchronizes users across multiple namespaces to a single OpenShift group.

**Use Case**: Courses with multiple associated namespaces (e.g., dev, test, prod environments).

**Configuration**:
- `GROUP_NAME`: OpenShift group to sync users to
- `CLASS_NAME`: Class identifier used to discover namespaces (e.g., `cs210`)

**Deployment**:
```bash
cd deployment/cronjobs/multiple-ns-group-sync/
# Edit cronjob.yaml to set GROUP_NAME and CLASS_NAME
oc project <target-namespace>
oc apply -k . --as system:admin
```

**Manual Trigger**:
```bash
oc create -n <namespace> job --from=cronjob/multiple-ns-group-sync multiple-ns-group-sync
```

---

### Webhooks

#### assign-class-label

**Purpose**: Mutating admission webhook that automatically adds `nerc.mghpcc.org/class=<classname>` labels to notebook pods based on user group membership.

**Use Case**: Enable class-specific resource quotas, gatekeeper policies, and monitoring by differentiating users of different classes in shared namespaces.

**Prerequisites**:
- Run `group-sync` cronjob first to populate OpenShift groups
- Cert-manager installed for TLS certificate generation

**Configuration**:
1. Edit `webhooks/assign-class-label/deployment.yaml`:
   - Set `GROUPS` environment variable to comma-separated list of OpenShift groups (e.g., `cs210,cs506,ds210`)
2. Update namespace in kustomization.yaml if deploying to new environment

**Deployment**:
```bash
cd deployment/webhooks/assign-class-label/
# Edit deployment.yaml to set GROUPS
oc apply -k . --as system:admin
```

**How It Works**:
1. User launches a notebook in RHOAI
2. Webhook intercepts pod creation request
3. Checks user's group membership against configured GROUPS list
4. Adds `nerc.mghpcc.org/class=<group>` label to pod metadata
5. Pod is created with class label for downstream policy enforcement

---

### GPU Class Setup

**Purpose**: Automate setup of GPU resource classes and queues across course namespaces.

**Use Case**: Configure GPU access (V100, A100, H100) for ML/AI courses.

**Deployment**:
```bash
cd deployment/gpu-class/
./gpu-class-setup.sh <namespace>
```

---

## Common Workflows

### Setting Up a New Course

1. **Create OpenShift Group**:
   ```bash
   cd deployment/cluster-scope/base/user.openshift.io/groups/
   mkdir <course-name>
   # Create group.yaml (copy from existing group)
   oc apply -f <course-name>/group.yaml
   ```

2. **Deploy Group Sync**:
   ```bash
   cd deployment/cronjobs/group-sync/
   # Edit GROUP_NAME=<course-name>, NAMESPACE=<course-namespace>
   oc apply -k . --as system:admin
   ```

3. **Deploy Notebook Culler**:
   ```bash
   cd deployment/cronjobs/nb-culler/
   # Edit GROUP_NAME=<course-name>, CUTOFF_TIME=<seconds>
   oc apply -k . --as system:admin
   ```

4. **Deploy Class Label Webhook**:
   ```bash
   cd deployment/webhooks/assign-class-label/
   # Add <course-name> to GROUPS env variable in deployment.yaml
   oc apply -k . --as system:admin
   ```

### Retrieving Student Notebook URLs

TAs can retrieve notebook URLs for debugging or access verification:

```bash
# List all notebooks
oc get notebooks -n rhods-notebooks

# Get URL for specific notebook
cd scripts/
python get_url.py
# Enter notebook name when prompted
```

**Requirements**: Install `pyyaml` first: `pip install pyyaml`

---

## Monitoring and Troubleshooting

### Check CronJob Status

```bash
# List cronjobs
oc get cronjobs -n <namespace>

# View recent jobs
oc get jobs -n <namespace>

# View job logs
oc logs job/<job-name> -n <namespace>
```

### Check Webhook Status

```bash
# View webhook pods
oc get pods -n <webhook-namespace> -l app=assign-class-label

# View webhook logs
oc logs -n <webhook-namespace> -l app=assign-class-label -f

# Check webhook configuration
oc get mutatingwebhookconfiguration assign-class-label
```

### Common Issues

1. **Group sync not adding users**: Verify users have `edit` rolebinding in target namespace
2. **Webhook not labeling pods**: Ensure user is in configured GROUPS and cert-manager is running
3. **Notebook culler not working**: Check GROUP_NAME matches OpenShift group, verify CUTOFF_TIME is in seconds

---

## Container Images

RHOAI automation containers are located in `../containers/`:
- `assign-class-label/`: Flask webhook service (Python 3.12)
- `group-sync/`: OpenShift client automation (opf-toolbox base)

To rebuild containers, see individual Dockerfiles and deployment manifests.

---

## Configuration Reference

### Common Environment Variables

| Variable | Used In | Description | Example |
|----------|---------|-------------|---------|
| `GROUP_NAME` | All cronjobs | OpenShift group name | `cs210` |
| `NAMESPACE` | group-sync | Namespace to watch | `cs210-class` |
| `CUTOFF_TIME` | nb-culler | Max runtime in seconds | `43200` (12 hours) |
| `CLASS_NAME` | multiple-ns-group-sync | Class identifier | `cs210` |
| `GROUPS` | assign-class-label | Comma-separated groups | `cs210,cs506,ds210` |

### Kustomize Structure

All deployments use Kustomize for configuration management:
```yaml
kustomization.yaml
├── namespace: <target-namespace>
├── resources: [YAML files to deploy]
└── patchStrategicMerge: [optional patches]
```

To customize for your environment, edit `kustomization.yaml` in each component directory.

---

## Security Considerations

- All cronjobs and webhooks require cluster-admin permissions (`--as system:admin`)
- RBAC manifests grant minimal required permissions (see `role.yaml`, `clusterrole.yaml` in each component)
- Webhook TLS certificates managed by cert-manager
- Sensitive values should be stored in Secrets (not committed to git)

---

## Additional Documentation

- **TA Access Guide**: See `../content/contributor_guide/rhoai_ta_access.md`
- **Container Build Guide**: See `../containers/README.md`
- **OPE Main Guide**: See `../README.md`

---

## Support

For issues, questions, or contributions:
- GitHub Issues: [ope-project issues](https://github.com/OPEFFORT/ope-project/issues)
- Original BU-RHOAI: [BU-RHOAI repository](https://github.com/OCP-on-NERC/BU-RHOAI)
