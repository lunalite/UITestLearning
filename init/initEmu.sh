#!/bin/sh

max=4

if [ -z "$ANDROID_HOME" ]; then
    echo "Need to set ANDROID_HOME"
    exit 1
fi


for (( i=0; i < max; i++ ))
do
    echo no |$ANDROID_HOME/tools/bin/avdmanager create avd -f -n avd-$i -b x86 -c 512M -k "system-images;android-26;google_apis;x86" -g "google_apis"
    z=$((5554 + i*2))
    $ANDROID_HOME/emulator/emulator -avd avd-$i -skin 480x800 -port $z -noaudio -no-window &
    $ANDROID_HOME/platform-tools/adb -s emulator-$z shell input keyevent 82
    $ANDROID_HOME/platform  -tools/adb -s emulator-$z shell svc data disable
done



