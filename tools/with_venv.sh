#!/bin/bash
tools_path=${tools_path:-$(dirname $0)}
venv_path=${venv_path:-${tools_path}}
tox_env=$(cd ${venv_path} && find ../.tox -maxdepth 1 -name "py*" | sort | tail -n1)
venv_dir=${venv_name:-${tox_env}}
TOOLS=${tools_path}
VENV=${venv:-${venv_path}/${venv_dir}}
source ${VENV}/bin/activate && "$@"
