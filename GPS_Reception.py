import threading
import telnetlib
import pynmea2
from flask import Flask, render_template, jsonify
import math

app = Flask(__name__)

# Global variables to store the latest GPS data for two devices
latest_data_1 = {
    "latitude": None,
    "longitude": None,
    "elevation": None,
    "speed": None
}

latest_data_2 = {
    "latitude": None,
    "longitude": None,
    "elevation": None,
    "speed": None
}

# Global variable to store collision alert
collision_alert = None

# Update the latest GPS data for device 1
def update_latest_data_1(latitude, longitude, elevation=None, speed=None):
    global latest_data_1
    latest_data_1["latitude"] = latitude
    latest_data_1["longitude"] = longitude
    latest_data_1["elevation"] = elevation
    latest_data_1["speed"] = speed
    check_for_collision()
    print(f"Device 1 - Latitude: {latitude}, Longitude: {longitude}, Elevation: {elevation}, Speed: {speed}")

# Update the latest GPS data for device 2
def update_latest_data_2(latitude, longitude, elevation=None, speed=None):
    global latest_data_2
    latest_data_2["latitude"] = latitude
    latest_data_2["longitude"] = longitude
    latest_data_2["elevation"] = elevation
    latest_data_2["speed"] = speed
    check_for_collision()
    print(f"Device 2 - Latitude: {latitude}, Longitude: {longitude}, Elevation: {elevation}, Speed: {speed}")

# Check for collision based on the latest data
def check_for_collision():
    global collision_alert

    # Define the cross-section coordinates
    cross_section_lat = 44.805642  # Update with actual coordinates
    cross_section_lon = -0.604730  # Update with actual coordinates

    # Calculate distances and times to cross-section for both devices
    def calculate_distance_and_time(lat1, lon1, speed):
        if lat1 is None or lon1 is None or speed is None:
            return None, None
        # Convert speed from knots to meters per second
        speed_mps = speed * 0.514444
        distance = haversine_distance(lat1, lon1, cross_section_lat, cross_section_lon) * 1000  # Convert km to meters
        time = distance / speed_mps if speed_mps > 0 else float('inf')
        return distance, time

    distance1, time1 = calculate_distance_and_time(
        latest_data_1["latitude"], latest_data_1["longitude"], latest_data_1["speed"])
    distance2, time2 = calculate_distance_and_time(
        latest_data_2["latitude"], latest_data_2["longitude"], latest_data_2["speed"])

    if distance1 is None or distance2 is None:
        return

    threshold = 3.0  # Threshold time difference for collision alert

    if abs(time1 - time2) < threshold:
        collision_alert = f"Collision alert: Device 1 and Device 2 may collide at the cross-section!"
    else:
        collision_alert = None

# Haversine formula to calculate the distance between two points on the Earth
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Parse NMEA sentences (functions unchanged)
def parse_nmea_sentence_1(sentence):
    try:
        msg = pynmea2.parse(sentence.strip())
        # if isinstance(msg, pynmea2.types.talker.GGA):
        #     latitude = msg.latitude
        #     longitude = msg.longitude
        #     elevation = msg.altitude
        #     update_latest_data_1(latitude, longitude, elevation)
        #     # print(f"Device 1 - Latitude: {latitude}, Longitude: {longitude}, Elevation: {elevation}")
        if isinstance(msg, pynmea2.types.talker.RMC):
            latitude = msg.latitude
            longitude = msg.longitude
            speed = msg.spd_over_grnd * 1.852  # Speed over ground in km/h (1 knot = 1.852 km/h)
            update_latest_data_1(latitude, longitude, speed=speed)
            # print(f"Device 1 - Latitude: {latitude}, Longitude: {longitude}, Speed: {speed}")
    except pynmea2.ParseError as e:
        print(f"Parse error: {e}")

def parse_nmea_sentence_2(sentence):
    try:
        msg = pynmea2.parse(sentence.strip())
        # if isinstance(msg, pynmea2.types.talker.GGA):
        #     latitude = msg.latitude
        #     longitude = msg.longitude
        #     elevation = msg.altitude
        #     update_latest_data_2(latitude, longitude, elevation)
        #     print(f"Device 2 - Latitude: {latitude}, Longitude: {longitude}, Elevation: {elevation}")
        if isinstance(msg, pynmea2.types.talker.RMC):
            latitude = msg.latitude
            longitude = msg.longitude
            speed = msg.spd_over_grnd * 1.852  # Speed over ground in km/h (1 knot = 1.852 km/h)
            update_latest_data_2(latitude, longitude, speed=speed)
            # print(f"Device 2 - Latitude: {latitude}, Longitude: {longitude}, Speed: {speed}")
    except pynmea2.ParseError as e:
        print(f"Parse error: {e}")

# Telnet connection functions (functions unchanged)
def connect_to_gps_1():
    HOST = '192.168.146.34'  # IP address of your first GPS device
    PORT = 8080  # Port number for the TCP server on your first GPS device

    try:
        # Connect to the GPS device
        tn = telnetlib.Telnet(HOST, PORT)
        print("Connected to GPS device 1")

        # Receive data from the GPS device
        while True:
            data = tn.read_until(b"\n")  # Read until newline character
            data_str = data.decode('utf-8').strip()
            parse_nmea_sentence_1(data_str)  # Parse the received NMEA sentence

    except ConnectionRefusedError:
        print("Connection to device 1 refused. Make sure the GPS device is running and reachable.")
    except Exception as e:
        print(f"An error occurred with device 1: {e}")
    finally:
        # Close the connection
        tn.close()

def connect_to_gps_2():
    HOST = '192.168.146.144'  # IP address of your second GPS device
    PORT = 8080  # Port number for the TCP server on your second GPS device

    try:
        # Connect to the GPS device
        tn = telnetlib.Telnet(HOST, PORT)
        print("Connected to GPS device 2")

        # Receive data from the GPS device
        while True:
            data = tn.read_until(b"\n")  # Read until newline character
            data_str = data.decode('utf-8').strip()
            parse_nmea_sentence_2(data_str)  # Parse the received NMEA sentence

    except ConnectionRefusedError:
        print("Connection to device 2 refused. Make sure the GPS device is running and reachable.")
    except Exception as e:
        print(f"An error occurred with device 2: {e}")
    finally:
        # Close the connection
        tn.close()

# Start the GPS connections in separate threads
gps_thread_1 = threading.Thread(target=connect_to_gps_1)
gps_thread_1.start()

gps_thread_2 = threading.Thread(target=connect_to_gps_2)
gps_thread_2.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gps_data_1')
def gps_data_1():
    return jsonify(latest_data_1)

@app.route('/gps_data_2')
def gps_data_2():
    return jsonify(latest_data_2)

@app.route('/collision_alert')
def collision_alert_endpoint():
    return jsonify({"alert": collision_alert})

@app.route('/crossing_times')
def crossing_times():
    # Define the cross-section coordinates
    cross_section_lat = 44.805642  # Update with actual coordinates
    cross_section_lon = -0.604730  # Update with actual coordinates

    # Calculate distances and times to cross-section for both devices
    def calculate_distance_and_time(lat1, lon1, speed):
        if lat1 is None or lon1 is None or speed is None:
            return None, None
        # Convert speed from knots to meters per second
        speed_mps = speed * 0.514444
        distance = haversine_distance(lat1, lon1, cross_section_lat, cross_section_lon) * 1000  # Convert km to meters
        time = distance / speed_mps if speed_mps > 0 else float('inf')
        return distance, time

    distance1, time1 = calculate_distance_and_time(
        latest_data_1["latitude"], latest_data_1["longitude"], latest_data_1["speed"])
    distance2, time2 = calculate_distance_and_time(
        latest_data_2["latitude"], latest_data_2["longitude"], latest_data_2["speed"])

    return jsonify({
        "device_1": {"distance": distance1, "time": time1},
        "device_2": {"distance": distance2, "time": time2}
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
