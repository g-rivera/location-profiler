
import android, os, time, sys
from wifi_stuff import *

droid=android.Android()
MAX_PROFILE_LENGTH = 8

def main():
    init()
    show_main_menu()

def init():
    """
      Initialize location profiles name to be none
    """
    global script_dir
    script_dir = '/mnt/sdcard/sl4a/scripts/settings'
    global list
    list = []
    for dirname, dirnames, filenames in os.walk(script_dir):
        for filename in filenames:
            list.append(filename)


def show_main_menu():
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
           and "Current_profile" not in line:
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
    droid.dialogCreateAlert('Editing ' + list[file_index], 'Chose any number of items and then press OK')
    droid.dialogSetPositiveButtonText('Done')
    droid.dialogSetNegativeButtonText('Cancel')
    droid.dialogSetMultiChoiceItems(settings, dispValues)
    droid.dialogShow()
    response = droid.dialogGetResponse().result
    if 'negative' not in response[u'which']:
        selectedResult = droid.dialogGetSelectedItems().result
        write_settings(file_index, selectedResult)
    edit_profile()

def write_settings(file_index,selectedResult,set_profile=False):
    """
        Write settings for the profile
    """
    i = 0
    fin = open(script_dir + '/' + list[file_index], 'r')
    fout = open(script_dir + '/' + list[file_index]+'NEW', 'w')
    for line in fin:
        if line != "\n":
            if "Profile_location" in line or "Interval" in line \
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
        Will call find_profile function in LOCATER_PROFILE class. If return value is:
        a. none, then prompt the user to enter the name of the new profile.
        b. profile found, then prompt the user that the profile already existed, exit
           the menu by hitting OK.
   """
    wifi_main_add_profile()
    # done - TODO: Call poll location function here
    if flag == True:
        # done - TODO: If polling function return true then prompt the user to enter the profile name.  If false then show error message dialog box.
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
                #TODO: The following function call should provide x and y returned by the poll locator function call.
                #TODO: The lan and lon will be used to update the profile file.  The put_new_profile function call should be passed in filename, x, y.
                #TODO: For now I am only passing in profile name
                put_new_profile(res)
            else:
                droid.dialogCreateAlert('Are you sure to override the existing ' + res + ' profile?', 'Chose OK to confirm')
                droid.dialogSetPositiveButtonText('OK')
                droid.dialogSetNegativeButtonText('Cancel')
                droid.dialogShow()
                response = droid.dialogGetResponse().result
                if 'negative' not in response[u'which']:
                    put_new_profile(res)
            read_settings(list.index(res))
    else:
        droid.dialogCreateAlert('You must choose at least 1 wifi network')
        droid.dialogSetNegativeButtonText('OK')
        droid.dialogShow()
        add_profile()


def put_new_profile(fileName):
    f = open(script_dir + '/' + fileName, 'w')
    f.write("Profile_location_wifi:" + repr(selected_wifi) + '\n')
    f_d = open(script_dir + '/' + "DEFAULT", 'r')
    for line in f_d:
        f.write(line)
    f.close()
    f_d.close()

def delete_profile():
    """
        When DELETE PROFILE item is hit, then show all profiles for user to select which profile to delete.
        "Are you sure to delete this profile?" will be shown. Hit OK to delete. Hit cancel to go back to
        main menu.
   """
    droid.dialogCreateAlert('Delete profile', 'Chose profile and then press OK')
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
        droid.dialogCreateAlert('Are you sure to delete the ' + list[file_index] + ' profile?', 'Chose OK to confirm')
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
    droid.dialogCreateAlert("Applying the following profile to the phone", 'Chose the profile name and then press OK')
    droid.dialogSetSingleChoiceItems(list, val)
    droid.dialogSetPositiveButtonText('OK')
    droid.dialogSetNegativeButtonText('Cancel')
    droid.dialogShow()
    response = droid.dialogGetResponse().result
    if 'negative' not in response[u'which']:
        selected = droid.dialogGetSelectedItems().result
        write_settings(val, selected, True)
        write_settings(selected[0], selected, True)
        apply_settings(selected[0])
    show_main_menu()

def apply_settings(profile_index):
    fin = open(script_dir + '/' + list[profile_index], 'r')
    for line in fin:
        if "Airplane Mode" in line:
            curr = line.split(':')[1]
            if curr.strip("\n") == "True":
                droid.toggleAirplaneMode(True)
            else:
                droid.toogleAirplaneMode(False)
        elif "Bluetooth On" in line:
            curr = line.split(':')[1]
            if curr.strip("\n") == "True":
                droid.toggleBluetoothState(True)
            else:
                droid.toggleBluetoothState(False)
        elif "Ringer Silent" in line:
            curr = line.split(':')[1]
            if curr.strip("\n") == "True":
                droid.toggleRingerSilentMode(True)
            else:
                droid.toggleRingerSilentMode(False)
        elif "Screen Off" in line:
            curr = line.split(':')[1]
            if curr.strip("\n") == "True":
                droid.setScreenBrightness(0)
            else:
                droid.setScreenBrightness(255)
        elif "Wifi On" in line:
            curr = line.split(':')[1]
            if curr.strip("\n") == "True":
                droid.toggleWifiState(True)
            else:
                droid.toggleWifiState(False)
    fin.close()

if __name__ == "__main__":
    sys.exit(main())


