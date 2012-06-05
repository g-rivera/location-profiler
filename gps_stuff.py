import android
import time
import math

def poll_gps(wait_timeout=20,droid=android.Android()):
    """
    Poll the GPS receiver for current coordinates
    
    preconditions: 
            
    gps location is discoverable
    wait_timeout is a number
    
    postcondition:
    a dictionary containing latitude ('lat') and longitude('lng') is returned
    if location is discoverable
    
    if gps location is not discoverable, returns an empty dict		
    
    """
    #Get an Android
    
    avg_lat=0
    avg_lng=0
    ret_val={}
    print "hello"

    #Attempt to get gurrent location
    droid.startLocating()
    
    time.sleep(wait_timeout)
      
    current_location=droid.readLocation()
    droid.stopLocating()
    
    if current_location<>():
        
        try:
            #We will only use GPS location -- 'coarse' location
            #is just too innacurate.
            ret_val['lat']=current_location[1]['gps']['latitude']
            ret_val['lng']=current_location[1]['gps']['longitude']
            ret_val['accuracy']=current_location[1]['gps']['accuracy']
        except KeyError:
            return {}

        return ret_val
    


def calc_distance(present_location, profile_location):
    """
        Calculates distance (in meters) between two points given as
        (lat, long) pairs based on Haversine formula.
        http://en.wikipedia.org/wiki/Haversine_formula

        Precondition:
            Lattitude and longitude are valid cartographical coordinates
            expressed as tuples in this format: (float(lattitude), float(longitude))

            example:
                 seattle = (47.621800, -122.350300)
                 redmond = (47.674200, -122.120300)

                 calc_distance(seattle,redmond) -> 18.18973623112346

        Post condition:
            Returns the result of the calculation in meters (float)

            If the coordinates exceed ? 180.0, a VALUE_ERROR is raised.
    """
    # need to add exceptions

    # define present location and comparison location (profile loc)
    lat1, lon1 = present_location
    lat2, lon2 = profile_location
    radius = 6378100 # meters

    # Haversine formula calculation
    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = radius * c

    return distance
    # program logic in main loop to determine minimum distance using this result  
