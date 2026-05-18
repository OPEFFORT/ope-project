import os
import sys
import openshift_client as oc
import logging

LOG = logging.getLogger(__name__)


def add_users_to_group(group):
    # Run the `oc get` command, capture the JSON output, and load the data
    rolebinding = oc.selector('rolebinding/edit').object()

    users_in_rolebinding = set(
        subject['name'] for subject in rolebinding.model.subjects
    )
    # Handle case where group.model.users might be None
    users_in_group = set(group.model.users) if group.model.users else set()

    users_to_add = users_in_rolebinding.difference(users_in_group)
    users_to_remove = users_in_group.difference(users_in_rolebinding)

    group_name = group.model.metadata.name
    LOG.info('adding to group %s: %s', group_name, users_to_add)
    LOG.info('removing from group %s: %s', group_name, users_to_remove)
    # Update the group's users list
    group.patch({'users': list(users_in_rolebinding)})
    # Remove users from the group
    for user in users_to_remove:
        group.model.users.remove(user)
    group.patch({'users': list(group.model.users)})


if __name__ == '__main__':
    # Use environment variables for group name and namespace
    group_name = os.environ.get('GROUP_NAME')
    namespace_name = os.environ.get('NAMESPACE')

    logging.basicConfig(level='INFO')

    # Check if the required environment variables are present
    if not group_name or not namespace_name:
        LOG.error('GROUP_NAME and NAMESPACE environment variables are required.')
        sys.exit(1)

    # Check that group exists
    try:
        group = oc.selector(f'group/{group_name}').object()
    except oc.model.OpenShiftPythonException:
        LOG.error('Unable to find group %s', group_name)
        sys.exit(1)

    # Run add_users_to_group in the given namespace
    with oc.project(namespace_name):
        add_users_to_group(group)
