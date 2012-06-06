import time, ast
import android

droid = android.Android()


def wifi_scan():
    """
        Checks wifi state, toggles. Scans for surrounding networks

        Pre-condition:
        If wifi antenna is off, turn it on. Else, begin scan.

        Post-condition:
        Returns a list of dicts containing network name and mac address
        of available networks.
        If no networks are fount, returns empty list.

    """
    wifistate = droid.checkWifiState().result
    
    #If wifi is off
    if wifistate == False:
        #turn it on
        droid.toggleWifiState(True)
        
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
                droid.toggleWifiState(False)
                
                
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

        Pre-condition:
        network_list argument is a list populated with available
        networks in the surrounding area.

        Post-condition:
        returns list of user-selected networks as a list of
        dictionaries.
        
    """

    #Initialize selected networks
    selected_networks=[]
    if network_list:

        #Prepare and show a pick-list consisting
        #of human readable network identifiers
        title = 'Select Wifi Network(s) to Associate with Profile'
        droid.dialogCreateAlert(title)
        display_list=[]
        for network in network_list:
            display_list.append( network['ssid'])
        droid.dialogSetMultiChoiceItems(display_list)
        droid.dialogSetPositiveButtonText('Select')
        droid.dialogShow()

        #Get the user selections
        droid.dialogGetResponse()
        for item in droid.dialogGetSelectedItems().result:
            #Add selections to returned list
            selected_networks.append(network_list[item])
            
    #Return user selections
    return selected_networks


if __name__ == '__main__':
    # Test: run wifi_stuff.py alone in the presence of 
    # a stable wifi networks and see if it ever fails
    # find it

    #mac address of stable wifi network access point
    test_mac='c0:c1:c0:ac:c1:31'
    #Number of tests to perform
    test_cnt=30
    
    for i in range(0,test_cnt):
        networks= wifi_scan()
        
        if networks==[]:
            print "FAIL--No networks"
        else:
            found_network=False
            for network in networks:
                if network['bssid']==test_mac:
                    found_network=True
                    break
            if found_network:
                print "PASS--%s found"  % test_mac
            else:
                print "FAIL--%s not found" % test_mac
           
        
        time.sleep(3)
