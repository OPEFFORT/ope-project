#!/bin/bash

CLASS_NAME="bu-cs599-pmpp-cuda"

create_resource_command=(oc create -f -)
openshift_url=https://rhods-dashboard-redhat-ods-applications.apps.edu.nerc.mghpcc.org/projects
# split openshift url to provide as parameters
host="${openshift_url%/projects*}"        # get everything before projects
hub_host=$host
run_name="gpu_class_test"
image_name="csw-dev-f25"

create_wb() {
    #set namespace
    namespace=$1

    username="jappavoo@bu.edu"

    user="jappavoo-40bu-2edu"

    # give notebook within namespace a name
    notebook_name="csw-dev"

    params=(
        -p NOTEBOOK_NAME="$notebook_name"
        -p RUN_NAME="$run_name"
        -p USERNAME="$username"
        -p NAMESPACE="$namespace"
        -p USER="$user"
        -p IMAGE_NAME="$image_name"
        -p OPENSHIFT_URL="$openshift_url"
        -p HUB_HOST="$hub_host"
    )

    oc process -f notebook_resource.yaml --local "${params[@]}" | "${create_resource_command[@]}"  --as system:admin 1>&2

    echo "$notebook_name"
}

apply_localqueue() {
    namespace=$1

    local_params=(
        -p NAMESPACE="$namespace"
    )

    oc process -f localqueue.yaml --local "${local_params[@]}" | "${create_resource_command[@]}" --as system:admin  1>&2
}

apply_rolebinding() {
    #set namespace and nb name
    namespace=$1
    notebook_name=$2

    rb_params=(
        -p NAMESPACE="$namespace"
        -p SERVICE_ACCOUNT_NB="$notebook_name"
    )

    oc process -f rbac_template.yaml --local "${rb_params[@]}" | "${create_resource_command[@]}" --as system:admin
}

create_clusterrole_bindings() {

    oc apply -f clusterrole.yaml --as system:admin
    # oc create will fail if resource exists (safer)
    oc create -f clusterrolebinding.yaml --as system:admin
}

add_sa_to_clusterrolebinding() {
    namespace=$1
    notebook_name=$2

    oc adm policy add-cluster-role-to-user pod-reader --rolebinding-name="csw-pod-reader" system:serviceaccount:$namespace:$notebook_name --as system:admin
    oc adm policy add-cluster-role-to-user nerc-node-reader --rolebinding-name="csw-node-reader" system:serviceaccount:$namespace:$notebook_name --as system:admin
    oc adm policy add-cluster-role-to-user kueue-clusterqueue-reader --rolebinding-name="csw-kueue-clusterqueue-reader" system:serviceaccount:$namespace:$notebook_name --as system:admin
}

# create_clusterrole_bindings

oc get ns | grep "^${CLASS_NAME}-" | awk '{print $1}' | while read ns; do
    #ns="ja-ope-test"
    oc project "$ns"

    #create a workbench and save the name of the notebook to apply rolebindings
    nb_name="$(create_wb "$ns")"
    apply_rolebinding "$ns" "$nb_name"
    apply_localqueue "$ns"
    add_sa_to_clusterrolebinding "$ns" "$nb_name"

done
