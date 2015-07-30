#!/bin/bash
buildname=simple-test
force_on=$1 # define a node name here if we need to

function run() {
    oc delete builds --all >/dev/null
    B=$(oc start-build ${buildname})
    BP=$(oc get pod|grep build|awk '{print $1}')
    Host=$(oc describe pod $BP|grep Node:|gsed -r 's/Node:[ \t]*//;s,/.*,,')

    if [[ -n ${force_on} && ${force_on} != ${Host} ]];then
        oc cancel-build ${B} >/dev/null
        return 1
    fi
}

while true;do
    run
    if [[ $? != 0 ]];then
        run
    else
        break
    fi
done

echo "Started around: $(date)"
echo "Running on ${Host}"

echo -n "Waiting that the build ${BP} started: "

while :;do
    running=$(oc get pod ${BP}|grep Running)
   [[ -n ${running} ]] && break
    sleep 2
    echo -n "."
done
echo ". success"

echo "Wait that the build ${BP} has succeded":
while true;do
    OUTPUT=$(oc build-logs ${B} |tail -n1)
    if echo ${OUTPUT} | grep -q "Successfully pushed";then
        echo "Success: ${OUTPUT}"
        break
    fi
    echo "Waiting: ${OUTPUT}"
    sleep 5
done

echo "End at: $(date)"
