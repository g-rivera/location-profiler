import time, ast
import android

droid = android.Android()


def wifi_scan():
    """
        Checks wifi state, toggles. Brings up 'scanning' alert.
    """
    wifistate = droid.checkWifiState().result
    
    #If wifi is off
    if wifistate == False:
        #turn it on
        droid.toggleWifiState()
        print "turned on wifi"
        time.sleep(8)
    droid.wifiStartScan()
    network_list=droid.wifiGetScanResults().result
    if network_list:
        #if wifi was off
        if wifistate == False:
            #get the current wifi state
            wifistate = droid.checkWifiState().result

            #if wifi is still on
            if wifistate:
                droid.toggleWifiState()
                print "turned off wifi"
                
        #Removes un-necessary info from wifi scan results
        for i in network_list:
            del i['level']
            del i['capabilities']
            del i['frequency']
            
            
        return network_list
    else:
        return []

def get_selected_wifi(network_list):
    """
        Displays dialog with list of available wifi networks. 
        Appends selected networks to settings file.
    """
    selected_networks=[]
    if network_list:
        title = 'Select Wifi Network(s) to Associate with Profile'
        droid.dialogCreateAlert(title)
        display_list=[]
        for network in network_list:
            display_list.append( network['ssid'])
        droid.dialogSetMultiChoiceItems(display_list)
        droid.dialogSetPositiveButtonText('Select')
        droid.dialogShow()
        droid.dialogGetResponse()
        for item in droid.dialogGetSelectedItems().result:
            selected_networks.append(network_list[item])

    return selected_networks


if __name__ == '__main__':
    # run wifi_stuff.py alone to see how the logger behaves
    networks= wifi_scan()
    selected_networks=get_selected_wifi(networks)

