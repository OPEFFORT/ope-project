import logging
import json
import base64
from flask import Flask, request, jsonify, Response
from kubernetes import config, client
from openshift.dynamic import DynamicClient

from pydantic import ValidationError
from typing import Any, List

from models import AdmissionReviewResponse, AdmissionReview, AdmissionResponse, Status

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def decode_pod_user(pod_user: str) -> str:
    return pod_user.replace('-40', '@').replace('-2e', '.')


def get_client() -> DynamicClient:
    try:
        config.load_config()
        k8s_client = client.ApiClient()
        dyn_client = DynamicClient(k8s_client)
        return dyn_client
    except config.ConfigException as e:
        LOG.error('Could not configure Kubernetes client: %s', str(e))
        exit(1)


def get_group_resource(dyn_client):
    return dyn_client.resources.get(api_version='user.openshift.io/v1', kind='Group')


# Get users of a given group
def get_group_members(group_resource: Any, group_name: str) -> List[str]:
    group_obj = group_resource.get(name=group_name)
    return group_obj.users


def assign_class_label(
    pod: dict[str, Any], groups: list[str], dyn_client: DynamicClient
) -> str | None:
    # Extract pod metadata
    try:
        pod_metadata = pod.get('metadata', {})
        pod_labels = pod_metadata.get('labels', {})
        pod_user = pod_labels.get('opendatahub.io/user', None)
    except AttributeError as e:
        LOG.error(f'Error extracting pod information: {e}')
        return None

    if pod_user is None:
        return None

    pod_user = decode_pod_user(pod_user)

    group_resource = get_group_resource(dyn_client)

    # Iterate through classes
    for group in groups:
        users = get_group_members(group_resource, group)

        # Check if group has no users
        if not users:
            LOG.warning(f'Group {group} has no users or users attribute is not a list.')
            continue

        # Compare users in the groups (classes) with the pod user
        if pod_user in users:
            LOG.info(f'Assigning class label: {group} to user {pod_user}')
            return group

    return None


def create_app(**config: Any) -> Flask:
    app = Flask(__name__)
    app.config.from_prefixed_env('RHOAI_CLASS')
    app.config.update(config)

    if not app.config['GROUPS']:
        LOG.error('RHOAI_CLASS_GROUPS environment variables are required.')
        exit(1)

    groups = app.config['GROUPS'].split(',')

    dyn_client = get_client()

    @app.route('/mutate', methods=['POST'])
    def mutate_pod() -> Response:
        # Grab pod for mutation and validate request
        try:
            admission_review = AdmissionReview(**request.get_json())
        except ValidationError as e:
            LOG.error('Validation error: %s', e)
            return (
                jsonify(
                    AdmissionReviewResponse(
                        response=AdmissionResponse(
                            uid=request.json.get('request', {}).get('uid', ''),
                            allowed=False,
                            status=Status(message=f'Invalid request: {e}'),
                        )
                    ).model_dump()
                ),
                400,
                {'content-type': 'application/json'},
            )

        uid = admission_review.request.uid
        pod = admission_review.request.object.model_dump()

        # Grab class that the pod user belongs to
        try:
            class_label = assign_class_label(pod, groups, dyn_client)
        except Exception as err:
            LOG.error('failed to assign class label: %s', err)
            return 'unexpected error encountered', 500, {'content-type': 'text/plain'}

        # If user not in any class, return without modifications
        if not class_label:
            return (
                jsonify(
                    AdmissionReviewResponse(
                        response=AdmissionResponse(
                            uid=uid,
                            allowed=True,
                            status=Status(message='No class label assigned.'),
                        )
                    ).model_dump()
                ),
                200,
                {'content-type': 'application/json'},
            )

        # Generate JSON Patch to add class label
        patch = [
            {
                'op': 'add',
                'path': '/metadata/labels/nerc.mghpcc.org~1class',
                'value': class_label,
            }
        ]

        # Encode patch as base64 for response
        patch_base64 = base64.b64encode(json.dumps(patch).encode('utf-8')).decode(
            'utf-8'
        )

        # Return webhook response that includes the patch to add class label
        return (
            jsonify(
                AdmissionReviewResponse(
                    response=AdmissionResponse(
                        uid=uid, allowed=True, patchType='JSONPatch', patch=patch_base64
                    )
                ).model_dump()
            ),
            200,
            {'content-type': 'application/json'},
        )

    return app
