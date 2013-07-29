<%def name="render()">\
                  # Aggregates #
                  declare -A AGGREGATES
                  % for rc in resource_classes:
                  AGGREGATES[${rc.name}]=-1
                  % endfor
                  # Nodes #
                  declare -A BM_HOSTS
                  % for rc in resource_classes:
                      %if rc.service_type=="compute":
                          %for r in rc.racks:
                              %for n in r.nodes:
                  BM_HOSTS[${n.node_id}]=${rc.name}
                  % endfor
                  % endfor
                  % endif
                  % endfor
                  # Flavors #
                  declare -A FLAVORS
                  % for rc in resource_classes:
                      % for f in rc.flavors:
<% ram, vcpu, disk, ephemeral, swap = nova_util.extract_from_capacities(f) %>\
                  FLAVORS[${rc.name}.${f.name}]='--ephemeral=${ephemeral} --swap=${swap} ${rc.name}.${f.name} auto ${ram} ${disk} ${vcpu}'
                  % endfor
                  % endfor
</%def>\