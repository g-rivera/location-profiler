import android
import os
import time
import sys
import wifi_stuff
import gps_stuff
import ast

droid = android.Android()
MAX_PROFILE_LENGTH = 8
STARTUP_SCRIPT = 'polling_loop.py'

extras = {"com.googlecode.android_scripting.extra.SCRIPT_PATH":
"/sdcard/sl4a/scripts/%s" % STARTUP_SCRIPT}
myintent = droid.makeIntent(
    "com.googlecode.android_scripting.action.LAUNCH_BACKGROUND_SCRIPT",
    None, None, extras, None,
    "com.googlecode.android_scripting",
    "com.googlecode.android_scripting.activity.ScriptingLayerServiceLauncher").result
script_dir = '/mnt/sdcard/sl4a/scripts/settings'#'./settings'
    
def main():
    ''' start up background thread. '''    
    LOG = "../logtest.py.log"
    if os.path.exists(LOG) is False:
        f = open(LOG, "w")
        f.close()
    LOG = open(LOG, "a")
    print "starting BG process"
    droid.startActivityIntent(myintent)
    LOG.write("Starting %s\n" % STARTUP_SCRIPT)   
    init()
    show_main_menu()

def init():
    """
      Initialize location profiles name to be none
    """
    global list
    list = []
    create_default()
    for dirname, dirnames, filenames in os.walk(script_dir):
        for filename in filenames:
            list.append(filename)


def show_main_menu():
    """
        Show main menu as: "EDIT PROFILE", "ADD PROFILE", "APPLY PROFILE", "DELETE PROFILE". 
    """
    droid.dialogCreateAlert("Profiles")
    l = ["EDIT PROFILE", "ADD PROFILE", "APPLY PROFILE", "DELETE PROFILE"]
    droid.dialogSetItems(l)
    droid.dialogSetPositiveButtonText('OK')
    droid.dialogSetNegativeButtonText('Cancel')
    droid.dialogShow()
    result = droid.dialogGetResponse().result
    if result.has_key(u'which'):
        sys.exit(0)
    elif result.has_key("item"):
        item = result["item"]
        if item == 0:
            edit_profile()
        elif item == 1:
            add_profile()
        elif item == 2:
            apply_profile()
        else:
            delete_profile()

def edit_profile():
    """
        Lookup all existing profiles names by looking up the profile names
        in the setting file and display them.
    """

    droid.dialogCreateAlert("Select the profile to edit", "Choose item and press OK")
    droid.dialogSetItems(list)
    droid.dialogSetPositiveButtonText('OK')
    droid.dialogSetNegativeButtonText('Cancel')
    droid.dialogShow()
    response = droid.dialogGetResponse().result
    if response.has_key(u'which'):
        show_main_menu()
    if response.has_key("item"):
        read_settings(response["item"])

def read_settings(file_index):
    """
        Read settings for the profile.
    """
    settings = []
    dispValues = []
    f = open(script_dir + '/' + list[file_index], 'r')
    i=0
    for line in f.readlines():
        if line != "\n" and "Profile_location_wifi" not in line and "Interval" not in line \
           and "Profile_location" not in line and "Current_profile" not in line:
            setting = line.split(':')[0]
            value = line.split(':')[1].strip('\n')
            if value == "True":
                dispValues.append(i)
            settings.append(setting)
            i = i + 1
    f.close()
    show_sub_menu(settings, dispValues, file_index)

def show_sub_menu(settings, dispValues, file_index):
    """
        Show settings for the profile.
    """
    droid.dialogCreateAlert('Editing ' + list[file_index], 'choose any number of items and then press OK')
    droid.dialogSetPositiveButtonText('Done')
    droid.dialogSetNegativeButtonText('Cancel')
    droid.dialogSetMultiChoiceItems(settings, dispValues)
    droid.dialogShow()
    response = droid.dialogGetResponse().result
    if 'negative' not in response[u'which']:
        selectedResult = droid.dialogGetSelectedItems().result
        write_settings(file_index, selectedResult)
    show_main_menu()

def write_settings(file_index,selectedResult,set_profile=False):
    """
        Write settings for the profile
    """
    i = 0
    fin = open(script_dir + '/' + list[file_index], 'r')
    fout = open(script_dir + '/' + list[file_index]+'NEW', 'w')
    for line in fin:
        if line != "\n":
            if "Profile_location" in line or "Interval" in line or "Profile_location_wifi" in line \
                or ("Current_profile" in line and not set_profile):
                fout.write(line)
            elif set_profile:
                if "Current_profile" in line:
                    setting = line.split(':')[0]
                    value = line.split(':')[1].strip('\n')
                    if file_index in selectedResult:
                        fout.write(line.replace(':False', ':True'))
                    else:
                        fout.write(line.replace(':True', ':False'))
                else:
                   fout.write(line)
            else:
                setting = line.split(':')[0]
                value = line.split(':')[1].strip('\n')
                if i in selectedResult:
                    fout.write(line.replace(':False', ':True'))
                else:
                    fout.write(line.replace(':True', ':False') )
                i = i + 1
    fin.close()
    fout.close()
    #Remove original file
    os.remove(script_dir + '/' + list[file_index])
    #Move new file
    fnew = open(script_dir + '/' + list[file_index], 'w')
    fout = open(script_dir + '/' + list[file_index]+'NEW', 'r')
    for line in fout:
        fnew.write(line)
    fnew.close()
    fout.close()
    os.remove(script_dir + '/' + list[file_index]+'NEW')

def add_profile():
    """
        Prompt the user to add a profile. Called when user hit "Add" button.
        Will call find_profile function. When new GPS location or wifi data is detected,
        then prompt the user to enter the name of the new profile.
        if profile found, then prompt the user that the profile already existed, prompt user to update the profile:
        Hitting OK to update, cancel to exit without updating the profile.
   """
    droid.dialogCreateSpinnerProgress("SCANNING LOCATION", "POLLING")
    droid.dialogShow()    
    gps_location=gps_stuff.poll_gps()
    wifi_network = wifi_stuff.wifi_scan();
    droid.dialogDismiss()
    selected_networks = wifi_stuff.get_selected_wifi(wifi_network)
    if len(wifi_network) > 0 or gps_location != {}:
        if len(selected_networks) <= 0 and len(wifi_network) > 0:
            while True:
                droid.dialogCreateAlert('You must choose at least 1 wifi network')
                droid.dialogSetNegativeButtonText('OK')
                droid.dialogShow()
                response = droid.dialogGetResponse().result
                if 'negative' in response[u'which']:
                    droid.dialogDismiss()
                    selected_networks = wifi_stuff.get_selected_wifi(wifi_network)
                    if len(selected_networks) > 0:
                        break
        
        p = find_profile(gps_location, wifi_networks=selected_networks)
        if p in list and p!='DEFAULT':
            droid.dialogCreateAlert('This location already exists in profile: ' + p + " Press OK to update the " + p + "profile with the newly detected wifi data." )
            droid.dialogSetPositiveButtonText('OK')
            droid.dialogSetNegativeButtonText('Cancel')
            droid.dialogShow()
            response = droid.dialogGetResponse().result
            if 'negative' not in response[u'which']:
                update_exist_profile(p,gps_location, selected_networks) 
            show_main_menu()
        else:            
            res = droid.dialogGetInput('Please enter profile name').result
            if res == None or len(res) == 0:
                show_main_menu()
            elif len(res) > MAX_PROFILE_LENGTH:
                while True:
                    droid.dialogDismiss()
                    res = droid.dialogGetInput('Name max is eight character! Please enter profile name again.').result
                    if res == None:
                        show_main_menu()
                    elif len(res) <= MAX_PROFILE_LENGTH:
                        break
            if len(res) <= MAX_PROFILE_LENGTH:
                if res not in list:
                    list.append(res)
                    put_new_profile(res,gps_location,selected_networks)
                else:
                    droid.dialogCreateAlert('Are you sure to override the existing ' + res + ' profile?', 'Choose OK to confirm')
                    droid.dialogSetPositiveButtonText('OK')
                    droid.dialogSetNegativeButtonText('Cancel')
                    droid.dialogShow()
                    response = droid.dialogGetResponse().result
                    if 'negative' not in response[u'which']:
                        put_new_profile(res,gps_location,selected_networks)
                read_settings(list.index(res))
    
    else:
        droid.dialogCreateAlert("Can't detect any valid location: No GPS data or WIFI data detected!" )
        droid.dialogShow()
        time.sleep(3)
        droid.dialogDismiss()
        show_main_menu()


def put_new_profile(fileName,gps_loc,networks):
    """
        Add new profile to the setting directory.  Use default profile as the new settings profile.
   """
    f = open(script_dir + '/' + fileName, 'w')
    f_d = open(script_dir + '/' + "DEFAULT", 'r')
    for line in f_d:
        if "Profile_location_wifi:" in line:
            line = "Profile_location_wifi:" + repr(networks) + '\n'
        if "Profile_location:" in line:
            line = "Profile_location:" + repr(gps_loc) + '\n'
        f.write(line)
    f.close()
    f_d.close()

def update_exist_profile(filename,gps_loc, networks):
    """
        Update the existing profile with the newly detected wifi data.
   """
    f = open(script_dir + '/' + filename, 'r')
    f_d = open(script_dir + '/' + filename + "new", 'w')
    for line in f:
        if "Profile_location_wifi:" in line and len(networks) > 0:
            line = "Profile_location_wifi:" + repr(networks) + '\n'
        if "Profile_location:" in line and gps_loc != {}:
            line = "Profile_location: " + repr(gps_loc) + '\n'
        f_d.write(line)
    f.close()
    f_d.close()    
    os.remove(script_dir + '/' + filename)
    fnew = open(script_dir + '/' + filename, 'w')    
    fout = open(script_dir + '/' + filename +'new', 'r')
    for line in fout:
        fnew.write(line)
    fnew.close()
    fout.close()
    os.remove(script_dir + '/' + filename +'new')        

def delete_profile():
    """
        When DELETE PROFILE item is hit, then show all profiles for user to select which profile to delete.
        "Are you sure to delete this profile?" will be shown. Hit OK to delete. Hit cancel to go back to
        main menu.
   """
    droid.dialogCreateAlert('Delete profile', 'choose profile and then press OK')
    droid.dialogSetSingleChoiceItems(list)
    droid.dialogSetPositiveButtonText('OK')
    droid.dialogSetNegativeButtonText('Cancel')
    droid.dialogShow()
    response = droid.dialogGetResponse().result
    if 'negative' in response[u'which']:
        show_main_menu()
    else:
        selected = droid.dialogGetSelectedItems().result
        file_index = selected[0]
        droid.dialogCreateAlert('Are you sure to delete the ' + list[file_index] + ' profile?', 'choose OK to confirm')
        droid.dialogSetPositiveButtonText('OK')
        droid.dialogSetNegativeButtonText('Cancel')
        droid.dialogShow()
        response = droid.dialogGetResponse().result
        if 'negative' not in response[u'which']:
            os.remove(script_dir + '/' + list[file_index])
            list.remove(list[file_index])
        show_main_menu()

def apply_profile():
    """
        Apply profile to the phone settings
    """
    i = 0
    val = 0
    for dirname, dirnames, filenames in os.walk(script_dir):
        for filename in filenames:
            #Find out the current profile and highlight it
            fin = open(script_dir + '/' + filename, 'r')
            for line in fin:
                if "Current_profile" in line:
                    curr = line.split(':')[1]
                    if curr.strip("\n") == "True":
                        val = i
            i = i+1
            fin.close()
    droid.dialogCreateAlert("Applying the following profile to the phone", 'choose the profile name and then press OK')
    droid.dialogSetSingleChoiceItems(list, val)
    droid.dialogSetPositiveButtonText('OK')
    droid.dialogSetNegativeButtonText('Cancel')
    droid.dialogShow()
    response = droid.dialogGetResponse().result
    if 'negative' not in response[u'which']:
        selected = droid.dialogGetSelectedItems().result
        write_settings(val, selected, True)
        write_settings(selected[0], selected, True)
        apply_settings(list[selected[0]])    
    show_main_menu()

def apply_settings(name):
    """
        Toggle phone settings.  Got warning when toggling airplan mode, comment it for now.
    """
    fin = open(script_dir + '/'+ name, 'r')
    
    for line in fin:
        '''	
        if "Airplane Mode" in line:
            curr = line.split(':')[1]
            if curr.strip("\n") == "True":
                droid.toggleAirplaneMode(True)
            else:
                droid.toogleAirplaneMode(False)
        '''
        print line
        if "Bluetooth On" in line:
            curr = line.split(':')[1]
            if curr.strip("\n") == "True":
                droid.toggleBluetoothState(True)
            else:
                droid.toggleBluetoothState(False)
        if "Ringer Silent" in line:
            curr = line.split(':')[1]
            if curr.strip("\n") == "True":
                print "turned ringer off"
                droid.toggleRingerSilentMode(True)
            else:
                droid.toggleRingerSilentMode(False)
        if "Screen Off" in line:
            curr = line.split(':')[1]
            if curr.strip("\n") == "True":
                droid.setScreenBrightness(0)
            else:
                droid.setScreenBrightness(255)
        if "Wifi On" in line:
            curr = line.split(':')[1]
            if curr.strip("\n") == "True":
                droid.toggleWifiState(True)
            else:
                droid.toggleWifiState(False)
    fin.close()

def create_default():
    """
        Create default profile.
    """
    if os.path.exists(script_dir + "/" + "DEFAULT") is False:    
        f = open(script_dir + "/" + "DEFAULT", "w")
        f.write("Profile_location_wifi:[]" + "\n")
        f.write("Profile_location: {}" "\n")
        f.write("Interval:30" + "\n")
        f.write("Current_profile:False" + "\n")
        f.write("Bluetooth On:True" + "\n")
        f.write("Ringer Silent:True" + "\n")
        f.write("Screen Off:True" + "\n")
        f.write("Wifi On:True" + "\n")
        f.close()

def set_current_profile(name):
    """
        Set "Current_profile:True/False" in the setting files to indicate the phone's current profile.
    """
    l = []    
    for dirname, dirnames, filenames in os.walk(script_dir):
        for filename in filenames:
            l.append(filename)
    for filename in l:            
        f = open(script_dir + "/" + filename, "r")
        f_new = open(script_dir + "/" + filename + "new", "w")
        for line in f:
            if "Current_profile" in line:
                if name != filename:
                    f_new.write("Current_profile:False\n")
                else:
                    f_new.write("Current_profile:True\n")
            else:
                f_new.write(line)                        
        f.close()
        f_new.close()
            
    for n in l:
        os.remove(script_dir + '/' + n)
        fnew = open(script_dir + '/' + n, 'w')
        fout = open(script_dir + '/' + n +'new', 'r')
        for line in fout:
            fnew.write(line)
        fnew.close()
        fout.close()
        os.remove(script_dir + '/' + n +'new')        
    apply_settings(name)
    
def find_profile(gps_location={},wifi_networks=[]):
    profile_dir=script_dir
    if gps_location!={}: 
        gps_profile=find_gps_in_profiles(profile_dir,gps_location)
        if gps_profile:
            print "Found GPS Profile %s" % gps_profile
            return gps_profile
    
    if wifi_networks<>():
        for network in wifi_networks:
            
            profile_name=find_wifi_in_profiles(profile_dir,network['bssid'])
            if profile_name:
                return profile_name
            else:
                return "DEFAULT"

def find_wifi_in_profiles(profile_dir,mac_address):
    file_names=os.listdir(profile_dir)
    
    
    for file_name in file_names:
        
        setting_file=open(profile_dir + '/' + file_name)
        if setting_file.read().find(mac_address)!=-1:
            setting_file.close()
            profile_found=True
            return file_name
        setting_file.close()
        
def find_gps_in_profiles(profile_dir,gps_position):
    file_names=os.listdir(profile_dir)
    for file_name in file_names:
        
        setting_file=open(profile_dir + '/' + file_name)
        for line in setting_file:
            if line.find("Profile_location: ")>-1:
                gps=line[line.find(": ")+2:].replace('\n','').replace('\r','')
                print str(gps) + '...'
                gps=eval(gps)
                if gps!={}:
                    distance=gps_stuff.calc_distance((gps['lat'],gps['lng']),(gps_position['lat'],gps_position['lng']))
                    if distance <= (gps['accuracy']+gps_position['accuracy'])/2:
                        return file_name
                    
        setting_file.close()
        
if __name__ == "__main__":
    sys.exit(main())


