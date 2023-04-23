#!/bin/bash -e
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
python3 ${SCRIPT_DIR}/audio_delayer.py


