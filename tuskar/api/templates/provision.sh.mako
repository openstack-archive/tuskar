<%def name="render()">\
                  #!/bin/bash -v
                  CONF=/root/tuskar/provision.conf
                  source /root/stackrc
                  wait_for(){
                    LOOPS=$1
                    SLEEPTIME=$2
                    shift ; shift
                    i=0
                    while [ $i -lt $LOOPS ] ; do
                      i=$((i + 1))
                      eval "$@" && return 0 || true
                      sleep $SLEEPTIME
                      done
                      return 1
                  }
                  wait_for 60 10 test -f /opt/stack/boot-stack/init-openstack.ok
                  # We must enable host aggregate matching when scheduling
                  echo "[DEFAULT]" >> /etc/nova/nova.conf
                  echo "scheduler_default_filters=AggregateInstanceExtraSpecsFilter,AvailabilityZoneFilter,RamFilter,ComputeFilter" >> /etc/nova/nova.conf
                  service openstack-nova-scheduler restart
                  # wait until nova and keystone are ready and confgured
                  while ! nova list; do source /root/stackrc; echo "Waiting for correct creds"; sleep 30; done
                  # Remove default flavors
                  for i in {1..5}
                  do
                    nova flavor-delete $i
                  done
                  # Set to not empty
                  HASH="md5sum"
                  declare -A EXISTING_AGGREGATES
                  while true
                  do
                    if [ "$HASH" != "`md5sum $CONF`" ]
                    then
                      HASH="`md5sum $CONF`"
                      echo "New Resources Found, Registering"
                      source $CONF
                      # Register Host Aggregates
                      aggs=`nova aggregate-list`
                      for a in ${'${!AGGREGATES[@]}'}
                      do
                       # Check to see 
                       if [ `expr "$aggs" : ".*\s$a\s"` == 0 ]
                       then
                         ${"EXISTING_AGGREGATES[$a]=$(nova aggregate-create $a | tail -n +4 | head -n 1 | tr -s ' ' | cut -d '|' -f2)"}
                         ${"nova aggregate-set-metadata ${EXISTING_AGGREGATES[$a]} class=$a-hosts"}
                       else
                         EXISTING_AGGREGATES[$a]=$a
                       fi
                      done
                      # Register Flavors
                      for f in ${'${!FLAVORS[@]}'}
                      do
                        ${'nova flavor-show $f &> /dev/null'}
                        if [ $? == 1 ]; then
                          ${'nova flavor-create ${FLAVORS[$f]}'}
                          ${'nova flavor-key $f set class=`expr $f : "\(.*\)\."`-hosts'}
                        fi
                      done
                      # Register Hosts
                      ${'while [ ${#BM_HOSTS[@]} -gt 0 ]'}
                      do
                        LIST=`nova host-list`
                        for i in ${'${!BM_HOSTS[@]}'}
                        do
                          HOST_ID=`expr "$LIST" : ".*\(overcloud-nova$i-\(\w\)\{12\}\)"`
                          if [ $HOST_ID ]
                          then
                            # Check to see if this host is already added to this aggregate
                            ${'AGG_DETAILS=`nova aggregate-details ${EXISTING_AGGREGATES[${BM_HOSTS[$i]}]}`'}
                            ${'if [ `expr "$AGG_DETAILS" : ".*$HOST_ID"` ]'}
                            then
                              ${'nova aggregate-add-host ${EXISTING_AGGREGATES[${BM_HOSTS[$i]}]} $HOST_ID'}
                            fi
                            unset BM_HOSTS[$i]
                          fi
                        done
                        sleep 1m
                      done
                      echo "Resource Registration Complete"
                    else
                      cat /var/cache/heat-cfntools/last_metadata | python -c 'import sys;import json;print json.load(sys.stdin)["AWS::CloudFormation::Init"]["config"]["files"]["/root/tuskar/provision.conf"]["content"]' > /root/tuskar/provision.conf
                    fi
                    sleep 1m
                  done
</%def>\
