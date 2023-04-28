#!/bin/bash -e
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
amixer -c 1 cset numid=6 100%
python3 ${SCRIPT_DIR}/audio_delayer.py


