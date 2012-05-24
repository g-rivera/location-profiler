import time, ast
import android
import locator_menu

droid = android.Android()

wifistate = droid.checkWifiState().result
networks = []
selected_wifi = []
bg_networks = []
flag = True
source_dir = '/mnt/sdcard/sl4a/scripts/settings'

def wifi_scan():
    """
        Checks wifi state, toggles. Brings up 'scanning' alert.
    """
    if wifistate == False:
        droid.toggleWifiState()
        droid.dialogCreateSpinnerProgress("SCANNING", "Finding Wifi Networks")
        droid.dialogShow()
        time.sleep(8)
        droid.wifiStartScan()
    else:
        droid.dialogCreateSpinnerProgress("SCANNING", "Finding Wifi Networks")
        droid.dialogShow()
        droid.wifiStartScan()

def clean_networks_for_output(networklist):
    """
        Removes un-necessary info from wifi scan results
    """
    for i in networklist:
        del i['level']
        del i['capabilities']
        del i['frequency']

def wifi_dialog(networklist):
    """
        Displays dialog with list of available wifi networks.
    """
    title = 'Select Wifi Network(s) to Associate with Profile'
    droid.dialogCreateAlert(title)
    droid.dialogSetMultiChoiceItems(networklist)
    droid.dialogSetPositiveButtonText('Select')
    droid.dialogShow()
    droid.dialogGetResponse()
    choice = droid.dialogGetSelectedItems().result

    for i in choice:
        selected_wifi.append(networklist[i])

def wifi_main_add_profile():
    """
	Combines all subroutines of wifi module. This function gets called by
        add_profile() in locater_menu module. Toggles wifi off after scan.
    """
    wifi_scan()
    networks = droid.wifiGetScanResults().result
    clean_networks_for_output(networks)
    wifi_dialog(networks)
    droid.toggleWifiState()
    if len(selected_wifi) > 0:
        flag = True
    else: flag = False

def wifi_log(latest_scan_results):
    """
	This function writes the latest scan results to a log file. The results
        are written directly into the file as a list of dictionaries using
        repr(). Each time there is a scan, the file is overwritten with the
        latest results.
    """
    log = open(source_dir + '/log','w')
    log.write(repr(latest_scan_results))
    log.close()

def parse_log():
    """
	Parses log file and returns list of dictionaries that contains
        wifi network info. Assign parse_log() to a varaiable to do the
        comparison.
    """
    file = open(source_dir + '/log','r')
    line = file.read()
    line.strip('\n')
    wifi_list = ast.literal_eval(line)
    return wifi_list

def wifi_bg_scanner():
    """
	Prototype background scanner function. Checks if wifi is on.
	Toggles wifi, does the wifi scan, collects results into bg_networks
        variable, and then writes the list of dictionaries into the log file.
    """
    while True:
        if wifistate == False:
            droid.toggleWifiState()
            time.sleep(8)
            droid.wifiStartScan()
            bg_networks = droid.wifiGetScanResults().result
            clean_networks_for_output(bg_networks)
            wifi_log(bg_networks)
            droid.toggleWifiState()
        else:
            droid.wifiStartScan()
            time.sleep(5)
            bg_networks = droid.wifiGetScanResults().result
            clean_networks_for_output(bg_networks)
            wifi_log(bg_networks)
            droid.toggleWifiState()
        time.sleep(30)
        log = parse_log()
        print log

if __name__ == '__main__':
    # run wifi_stuff.py alone to see how the logger behaves
    wifi_bg_scanner()
