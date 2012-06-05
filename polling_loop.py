import wifi_stuff
import gps_stuff

import os
import android
import time
import locator_menu

interval = '60'
profile_dir='/mnt/sdcard/sl4a/scripts/settings'
droid = android.Android()
if __name__=='__main__':
    working=True
    while working:
        droid.dialogCreateSpinnerProgress("SCANNING LOCATION", "POLLING")
        droid.dialogShow()    
        time.sleep(3)
        print "getting wifi networks..."
        current_networks=wifi_stuff.wifi_scan()
        print "getting gps position..."
        gps_location=gps_stuff.poll_gps()
        print gps_location
        print "looking up profile..."
        droid.dialogDismiss()
        profile=locator_menu.find_profile(gps_location=gps_location,wifi_networks=current_networks)
        if profile:
            print "profile: %s!!!!!" % profile
            locator_menu.apply_settings(profile)
            locator_menu.set_current_profile(profile)
            setting_file=open(profile_dir + '/' + profile)
            for line in setting_file.readlines():
                if "Interval" in line:
                    interval = line.split(":")[1]
            setting_file.close()        
        else:
            print "no matching profile"
        #working=False
        
        time.sleep(int(interval))

