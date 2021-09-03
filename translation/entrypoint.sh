#!/usr/bin/env bash

set -e

: ${TORCH_DEVICE:="cuda:0"}
: ${TRANSLATION_CODE:="en-ru"}

if [ $(python -c "import torch; print(not torch.cuda.is_available())") = "True" ] && [[ $TORCH_DEVICE == cuda* ]]; then
  echo "No cuda for PyTorch is available. Falling back to CPU."
  export TORCH_DEVICE=cpu
fi

if [[ $1 == 'server' ]]; then
  exec python /usr/src/app/translation/cli.py "${TRANSLATION_CODE}" "${TORCH_DEVICE}"
fi

exec "$@"
