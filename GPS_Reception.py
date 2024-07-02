import threading
import telnetlib
import pynmea2
from flask import Flask, render_template, jsonify

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

# Update the latest GPS data for device 1
def update_latest_data_1(latitude, longitude, elevation=None, speed=None):
    global latest_data_1
    latest_data_1["latitude"] = latitude
    latest_data_1["longitude"] = longitude
    latest_data_1["elevation"] = elevation
    latest_data_1["speed"] = speed

# Update the latest GPS data for device 2
def update_latest_data_2(latitude, longitude, elevation=None, speed=None):
    global latest_data_2
    latest_data_2["latitude"] = latitude
    latest_data_2["longitude"] = longitude
    latest_data_2["elevation"] = elevation
    latest_data_2["speed"] = speed

# Parse NMEA sentence for device 1
def parse_nmea_sentence_1(sentence):
    try:
        msg = pynmea2.parse(sentence.strip())
        if isinstance(msg, pynmea2.types.talker.GGA):
            latitude = msg.latitude
            longitude = msg.longitude
            elevation = msg.altitude
            update_latest_data_1(latitude, longitude, elevation)
            print(f"Device 1 - Latitude: {latitude}, Longitude: {longitude}, Elevation: {elevation}")
        elif isinstance(msg, pynmea2.types.talker.RMC):
            latitude = msg.latitude
            longitude = msg.longitude
            speed = msg.spd_over_grnd  # Speed over ground in knots
            update_latest_data_1(latitude, longitude, speed=speed)
            print(f"Device 1 - Latitude: {latitude}, Longitude: {longitude}, Speed: {speed}")
    except pynmea2.ParseError as e:
        print(f"Parse error: {e}")

# Parse NMEA sentence for device 2
def parse_nmea_sentence_2(sentence):
    try:
        msg = pynmea2.parse(sentence.strip())
        if isinstance(msg, pynmea2.types.talker.GGA):
            latitude = msg.latitude
            longitude = msg.longitude
            elevation = msg.altitude
            update_latest_data_2(latitude, longitude, elevation)
            print(f"Device 2 - Latitude: {latitude}, Longitude: {longitude}, Elevation: {elevation}")
        elif isinstance(msg, pynmea2.types.talker.RMC):
            latitude = msg.latitude
            longitude = msg.longitude
            speed = msg.spd_over_grnd  # Speed over ground in knots
            update_latest_data_2(latitude, longitude, speed=speed)
            print(f"Device 2 - Latitude: {latitude}, Longitude: {longitude}, Speed: {speed}")
    except pynmea2.ParseError as e:
        print(f"Parse error: {e}")

# Telnet connection function for device 1
def connect_to_gps_1():
    HOST = '192.168.65.102'  # IP address of your first GPS device
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

# Telnet connection function for device 2
def connect_to_gps_2():
    HOST = '192.168.65.34'  # IP address of your second GPS device
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

if __name__ == '__main__':
    app.run(debug=True)
