#!/usr/bin/env python3
"""Disable only native gestures handled by the BTT bridge; preserve rollback."""
import argparse
import json
from pathlib import Path
import plistlib
import subprocess

TRACKPAD_KEYS = ['TrackpadThreeFingerHorizSwipeGesture', 'TrackpadThreeFingerVertSwipeGesture',
                 'TrackpadFourFingerHorizSwipeGesture', 'TrackpadFourFingerVertSwipeGesture',
                 'TrackpadFourFingerPinchGesture']
DOMAINS = {
    'com.apple.AppleMultitouchTrackpad': dict.fromkeys(TRACKPAD_KEYS, 0),
    'com.apple.driver.AppleBluetoothMultitouch.trackpad': dict.fromkeys(TRACKPAD_KEYS, 0),
    'com.apple.dock': dict.fromkeys(['showMissionControlGestureEnabled','showAppExposeGestureEnabled',
                                   'showLaunchpadGestureEnabled','showDesktopGestureEnabled'], False),
}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--restore',action='store_true')
    args=p.parse_args()
    backup=Path.home()/'.config/deskflow-gestures-system-backup.json'
    if not args.restore and not backup.exists():
        saved={}
        for domain,keys in DOMAINS.items():
            result=subprocess.run(['defaults','export',domain,'-'],capture_output=True)
            values=plistlib.loads(result.stdout) if result.returncode==0 else {}
            saved[domain]={key:values.get(key) for key in keys}
        backup.parent.mkdir(parents=True,exist_ok=True)
        backup.write_text(json.dumps(saved,indent=2)+'\n')
    values=json.loads(backup.read_text()) if args.restore else DOMAINS
    for domain,keys in values.items():
        for key,value in keys.items():
            if value is None:
                subprocess.run(['defaults','delete',domain,key],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            else:
                kind='-bool' if isinstance(value,bool) else '-int'
                encoded = ('true' if value else 'false') if isinstance(value,bool) else str(value)
                subprocess.run(['defaults','write',domain,key,kind,encoded],check=True)
    subprocess.run(['killall','Dock'],check=False)
    print('Native gesture settings restored' if args.restore else 'Conflicting native gestures disabled; keyboard shortcuts preserved')

if __name__=='__main__': main()
