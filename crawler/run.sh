#!/usr/bin/env bash

if [ $# -eq 0 ]
  then
    echo "No arguments supplied."
    echo "Usage: ./run.sh (AVD Number)"
    exit 1
fi

emulatorNo=$((5554 + $1 * 2))

if [ "$LOGNAME" = "hkoh006" ]
  then
    export PYTHONPATH=../; python3.6 Main.py emulator-5554 ../../APK2/apk-$1 avd1
   else
    export PYTHONPATH=../; python3.6 Main.py emulator-$emulatorNo ../../apk/apk-$1 avd$1
fi

