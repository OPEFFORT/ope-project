pattern="^bu-cs599-pmpp-cuda-"

    for proj in $(oc get projects -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | grep "$pattern"); do
        echo "deleting notebook + pvc"
        oc -n "$proj" delete notebook --as system:admin --all --ignore-not-found --wait=true || true
        oc -n "$proj" delete pvc --as system:admin --all --ignore-not-found --wait=true || true
    done
