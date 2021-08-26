#!/usr/bin/env bash

set -e

: ${TORCH_DEVICE:="cuda:0"}

if [ $(python -c "import torch; print(not torch.cuda.is_available())") = "True" ] && [[ $TORCH_DEVICE == cuda* ]]; then
  echo "No cuda for PyTorch is available. Falling back to CPU."
  export TORCH_DEVICE=cpu
fi

if [[ $1 == 'server' ]] && [[ $TORCH_DEVICE == "cpu" ]]; then
  exec gunicorn translation-api.app:app -c /usr/src/app/translation-api/gunicorn_cpu_conf.py
elif [[ $1 == 'server' ]] && [[ $TORCH_DEVICE == cuda:* ]]; then
  exec gunicorn translation-api.app:app -c /usr/src/app/translation-api/gunicorn_cuda_conf.py
fi

exec "$@"
