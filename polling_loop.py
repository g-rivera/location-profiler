import wifi_stuff
import gps_stuff

import os
import android
import time
import locator_menu



droid = android.Android()

def get_polling_interval(profile_name):
    """
    Return the polling interval saved indicated in the profile profile_name.
    """
    #This is the profile directory
    profile_dir='./settings'#'/mnt/sdcard/sl4a/scripts/settings'

    #Open the profile
    setting_file=open(profile_dir + '/' + profile_name)

    #Scan through the settings in that profile
    for line in setting_file.readlines():

        #If the setting is Interval, return the integer representation
        #of the setting value
        if "Interval" in line:
            setting_file.close()
            interval = int(line.split(":")[1])
            
    #Close the setting file
    setting_file.close()
    return interval
    
def apply_profile(profile_name):
    """
    Apply the settings contained in the profile named profile name
    to the phone.
    """

    #Apply the settings in that profile to the phone
    locator_menu.apply_settings(profile_name)

    #Mark the current profile as current.
    locator_menu.set_current_profile(profile_name)


#If this module is running directly in the interpreter
if __name__=='__main__':
    #We are always working
    working=True

    #The default polling interval
    interval=60
    
    #loop forever
    while working:

        #Show the class that polling is happening
        droid.dialogCreateSpinnerProgress("SCANNING LOCATION", "POLLING")
        droid.dialogShow()

        #Give the dialog time to start
        time.sleep(3)

        #Get a list of current wifi networks first since it is
        #faster than getting gps
        current_networks=wifi_stuff.wifi_scan()
 

        #Try to find a profile that includes at least one of the wifi
        #networks present
        profile=locator_menu.find_profile(wifi_networks=current_networks)

        #If we were able to find a network other than the default
        if profile !="DEFAULT":

            #Apply the profile
            apply_profile(profile)
            
            #Get rid of the progress form.  We are done scanning.
            droid.dialogDismiss()

            #Let the class know that a profile has been activated
            #based on the presence of wifi networks
            droid.makeToast("% profile applied from wifi networks" % profile)

            #Set the polling interval to that indicated by the profile
            interval=get_polling_interval(profile)
                  
        else:

            #Get the current gps coordinates
            gps_location=gps_stuff.poll_gps()

            #See if we can find a profile that matches the gps coordinates
            profile=locator_menu.find_profile(gps_location=gps_location)

            #If a profile was returned
            if profile:

                
                apply_profile(profile)
                #Get rid of the progress form.  We are done scanning.
                droid.dialogDismiss()

                #Let the class know that a profile has been activated
                #based on gps location
                droid.makeToast("%s profile applied from GPS location" % profile)
                
                #Set the polling interval to that indicated by the profile
                interval=get_polling_interval(profile)        
        print "---" + profile
        time.sleep(interval)
