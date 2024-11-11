# main.py

import zenoh
import logging
import warnings
import atexit
import json
import utils  # Import the utility functions
import val_standard_pb2  # Import the generated Protobuf classes
from google.protobuf import json_format
import argparse
import time

# Initialize logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)
logging.captureWarnings(True)
warnings.filterwarnings("once")

# Global variables
session = None

def parse_args():
    parser = argparse.ArgumentParser(description='Subscribe over zenoh')
    parser.add_argument('-k', '--key', default='val/**', help='Key expression to subscribe to')
    parser.add_argument('-r', '--router_address', default='tcp/127.0.0.1:7447', help='Zenoh router address')
    return parser.parse_args()

# Adjusted callback functions
def sub_measurement_properties_data(sample):
    """
    Callback function for MeasurementPropertiesMessage messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    json_data = json.loads(json_string)
    message = val_standard_pb2.MeasurementPropertiesMessage()

    # Extract mmsi and publish_stamp
    message.mmsi = json_data.get('mmsi', 0)
    if 'publish_stamp' in json_data:
        message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
        message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

    # Extract measurement_properties
    if 'measurement_properties' in json_data:
        measurement_properties_data = json_data['measurement_properties']
        json_format.ParseDict(measurement_properties_data, message.measurement_properties)
    else:
        logger.error("No 'measurement_properties' key found in the message.")

    logger.info(f"Received MeasurementPropertiesMessage: {message}")
    # Handle the message as needed

def sub_exercise_state_data(sample):
    """
    Callback function for ExerciseState messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    json_data = json.loads(json_string)
    message = val_standard_pb2.ExerciseState()

    # Extract publish_stamp
    if 'publish_stamp' in json_data:
        message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
        message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

    # Extract exercise_state
    if 'exercise_state' in json_data and 'state' in json_data['exercise_state']:
        state_str = json_data['exercise_state']['state'].upper()
        if state_str in val_standard_pb2.ExerciseState.State.keys():
            message.state = val_standard_pb2.ExerciseState.State.Value(state_str)
        else:
            message.state = val_standard_pb2.ExerciseState.UNKNOWN
    else:
        message.state = val_standard_pb2.ExerciseState.UNKNOWN

    logger.info(f"Received ExerciseState: {message}")
    # Handle the message as needed

def sub_ais_vessel_data(sample):
    """
    Callback function for AISVesselMessage messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    json_data = json.loads(json_string)
    message = val_standard_pb2.AISVesselMessage()

    # Extract mmsi and publish_stamp
    message.ais_vessel.mmsi = json_data.get('mmsi', 0)
    if 'publish_stamp' in json_data:
        message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
        message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

    # Extract ais_vessel data
    if 'ais_vessel' in json_data:
        ais_vessel_data = json_data['ais_vessel']
        json_format.ParseDict(ais_vessel_data, message.ais_vessel)
    else:
        logger.error("No 'ais_vessel' key found in the message.")

    logger.info(f"Received AISVesselMessage: {message}")
    # Handle the message as needed

# Adjust other callback functions based on the structure of the received messages

def sub_vessel_data(sample):
    """
    Callback function for Vessel messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    json_data = json.loads(json_string)
    message = val_standard_pb2.Vessel()

    # Extract mmsi and publish_stamp
    message.mmsi = json_data.get('mmsi', 0)
    if 'publish_stamp' in json_data:
        message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
        message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

    # Extract vessel data
    if 'vessel' in json_data:
        vessel_data = json_data['vessel']
        json_format.ParseDict(vessel_data, message)
    else:
        logger.error("No 'vessel' key found in the message.")

    logger.info(f"Received Vessel: {message}")
    # Handle the message
    
def sub_measurement_value_data(sample):
    """
    Callback function for MeasurementValue messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    json_data = json.loads(json_string)
    message = val_standard_pb2.MeasurementValue()

    # Extract mmsi and publish_stamp
    message.mmsi = json_data.get('mmsi', 0)
    if 'publish_stamp' in json_data:
        message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
        message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

    # Extract measurement value
    if 'measurement' in json_data:
        measurement_data = json_data['measurement']
        json_format.ParseDict(measurement_data, message.measurement)
    else:
        logger.error("No 'measurement' key found in the message.")

    logger.info(f"Received MeasurementValue: {message}")
    # Handle the message as needed
    
def sub_location_data(sample):
    """
    Callback function for Location messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    json_data = json.loads(json_string)
    message = val_standard_pb2.Location()

    # Extract mmsi and publish_stamp
    message.mmsi = json_data.get('mmsi', 0)
    if 'publish_stamp' in json_data:
        message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
        message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

    # Extract location data
    if 'location' in json_data:
        location_data = json_data['location']
        json_format.ParseDict(location_data, message)
    else:
        logger.error("No 'location' key found in the message.")

    logger.info(f"Received Location: {message}")
    # Handle the message as needed
    
def sub_alerts_data(sample):
    """
    Callback function for Alerts messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    json_data = json.loads(json_string)
    message = val_standard_pb2.Alerts()

    # Extract mmsi and publish_stamp
    message.mmsi = json_data.get('mmsi', 0)
    if 'publish_stamp' in json_data:
        message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
        message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

    # Extract alerts data
    if 'alerts' in json_data:
        alerts_data = json_data['alerts']
        json_format.ParseDict(alerts_data, message)
    else:
        logger.error("No 'alerts' key found in the message.")

    logger.info(f"Received Alerts: {message}")
    # Handle the message as needed

def sub_vessel_statics_data(sample):
    """
    Callback function for VesselStatics messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    json_data = json.loads(json_string)
    message = val_standard_pb2.VesselStatics()

    # Extract mmsi and publish_stamp
    message.mmsi = json_data.get('mmsi', 0)
    if 'publish_stamp' in json_data:
        message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
        message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

    # Extract vessel statics data
    if 'vessel_statics' in json_data:
        vessel_statics_data = json_data['vessel_statics']
        json_format.ParseDict(vessel_statics_data, message)
    else:
        logger.error("No 'vessel_statics' key found in the message.")

    logger.info(f"Received VesselStatics: {message}")
    # Handle the message as needed

def sub_assignments_data(sample):
    """
    Callback function for Assignments messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    json_data = json.loads(json_string)
    message = val_standard_pb2.Assignments()

    # Extract mmsi and publish_stamp
    message.mmsi = json_data.get('mmsi', 0)
    if 'publish_stamp' in json_data:
        message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
        message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

    # Extract assignments data
    if 'assignments' in json_data:
        assignments_data = json_data['assignments']
        json_format.ParseDict(assignments_data, message)
    else:
        logger.error("No 'assignments' key found in the message.")

    logger.info(f"Received Assignments: {message}")
    # Handle the message as needed







def main():
    global session

    args = parse_args()

    # Initialize Zenoh session
    logger.info(f"Configuring Zenoh with key: {args.key}, router: {args.router_address}")
    conf = zenoh.Config.from_json5(json.dumps({
        "mode": "client",
        "connect": {"endpoints": [args.router_address]}
    }))
    logger.info("Opening Zenoh session...")
    session = zenoh.open(conf)
    logger.info("Zenoh session opened successfully")

    def _on_exit():
        session.close()

    atexit.register(_on_exit)
    logger.info(f"Zenoh session established: {session.info()}")

    # Declare subscribers
    subscriptions = []

    # Subscribe to specific topics with adjusted callback functions
    # MeasurementPropertiesMessage
    key_expr_measurement_properties = "val/amoc/**/properties"
    sub_measurement_properties = session.declare_subscriber(
        key_expr_measurement_properties,
        sub_measurement_properties_data,
    )
    subscriptions.append(sub_measurement_properties)
    logger.info(f"Subscribed to: {key_expr_measurement_properties}")

    # ExerciseState
    key_expr_exercise_state = "val/amoc/exercise_state"
    sub_exercise_state = session.declare_subscriber(
        key_expr_exercise_state,
        sub_exercise_state_data,
    )
    subscriptions.append(sub_exercise_state)
    logger.info(f"Subscribed to: {key_expr_exercise_state}")

    # AISVesselMessage
    key_expr_ais_vessel = "val/amoc/**/aisvessel"
    sub_ais_vessel = session.declare_subscriber(
        key_expr_ais_vessel,
        sub_ais_vessel_data,
    )
    subscriptions.append(sub_ais_vessel)
    logger.info(f"Subscribed to: {key_expr_ais_vessel}")

    # Vessel
    key_expr_vessel = "val/amoc/vessel"
    sub_vessel = session.declare_subscriber(
        key_expr_vessel,
        sub_vessel_data,
    )
    subscriptions.append(sub_vessel)
    logger.info(f"Subscribed to: {key_expr_vessel}")
    
    # MeasurementValue
    key_expr_measurement_value = "val/amoc/**/value"
    sub_measurement_value = session.declare_subscriber(
        key_expr_measurement_value,
        sub_measurement_value_data,
    )
    subscriptions.append(sub_measurement_value)
    logger.info(f"Subscribed to: {key_expr_measurement_value}")
    
    # Location
    key_expr_location = "val/amoc/**/location"
    sub_location = session.declare_subscriber(
        key_expr_location,
        sub_location_data,
    )
    subscriptions.append(sub_location)
    logger.info(f"Subscribed to: {key_expr_location}")
    
    # Alerts
    key_expr_alerts = "val/amoc/**/alerts"
    sub_alerts = session.declare_subscriber(
        key_expr_alerts,
        sub_alerts_data,
    )
    subscriptions.append(sub_alerts)
    logger.info(f"Subscribed to: {key_expr_alerts}")
    
    # VesselStatics
    key_expr_vessel_statics = "val/amoc/**/vessel/statics"
    sub_vessel_statics = session.declare_subscriber(
        key_expr_vessel_statics,
        sub_vessel_statics_data,
    )
    subscriptions.append(sub_vessel_statics)
    logger.info(f"Subscribed to: {key_expr_vessel_statics}")
    
    # Assignments
    key_expr_assignments = "val/amoc/assignments"
    sub_assignments = session.declare_subscriber(
        key_expr_assignments,
        sub_assignments_data,
    )
    subscriptions.append(sub_assignments)
    logger.info(f"Subscribed to: {key_expr_assignments}")
    
    

    # Continue with other subscriptions as needed
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Closing session...")
        for sub in subscriptions:
            sub.undeclare()
        session.close()
        logger.info("Session closed")

if __name__ == "__main__":
    main()
