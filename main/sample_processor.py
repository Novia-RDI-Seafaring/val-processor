# main.py

import zenoh
import logging
import warnings
import atexit
import json
import val_standard_pb2  # Import the generated Protobuf classes
from google.protobuf import json_format
from google.protobuf import descriptor
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

# Callback functions
def sub_measurement_properties_data(sample):
    """
    Callback function for MeasurementPropertiesMessage messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    try:
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

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
    except json_format.ParseError as e:
        logger.error(f"Protobuf parsing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def sub_exercise_state_data(sample):
    """
    Callback function for ExerciseState messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    try:
        json_data = json.loads(json_string)
        message = val_standard_pb2.ExerciseState()

        # Extract publish_stamp
        if 'publish_stamp' in json_data:
            message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
            message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

        # Extract exercise_state
        if 'exercise_state' in json_data and 'state' in json_data['exercise_state']:
            state_str = json_data['exercise_state']['state'].upper()
            try:
                message.state = val_standard_pb2.ExerciseState.State.Value(state_str)
            except ValueError:
                message.state = val_standard_pb2.ExerciseState.UNKNOWN
        else:
            message.state = val_standard_pb2.ExerciseState.UNKNOWN

        logger.info(f"Received ExerciseState: {message}")
        # Handle the message as needed

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def sub_ais_vessel_data(sample):
    """
    Callback function for AISVesselMessage messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    try:
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

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
    except json_format.ParseError as e:
        logger.error(f"Protobuf parsing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def sub_vessels_data(sample):
    """
    Callback function for Vessels messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    try:
        json_data = json.loads(json_string)
        message = val_standard_pb2.Vessels()

        # Extract publish_stamp
        if 'publish_stamp' in json_data:
            message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
            message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

        # Extract vessels
        if 'vessels' in json_data:
            for vessel_data in json_data['vessels']:
                vessel_message = val_standard_pb2.Vessel()
                # Map enum fields if necessary
                if 'type' in vessel_data:
                    type_str = vessel_data['type']
                    try:
                        vessel_data['type'] = val_standard_pb2.Vessel.VesselType.Value(type_str)
                    except ValueError:
                        vessel_data['type'] = val_standard_pb2.Vessel.UNKNOWN
                json_format.ParseDict(vessel_data, vessel_message)
                message.vessels.append(vessel_message)
        else:
            logger.error("No 'vessels' key found in the message.")

        logger.info(f"Received Vessels: {message}")
        # Handle the message as needed

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
    except json_format.ParseError as e:
        logger.error(f"Protobuf parsing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def sub_measurement_value_data(sample):
    """
    Callback function for MeasurementValue messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    try:
        json_data = json.loads(json_string)
        message = val_standard_pb2.MeasurementValue()

        # Extract mmsi and publish_stamp
        message.mmsi = json_data.get('mmsi', 0)
        if 'publish_stamp' in json_data:
            message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
            message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

        # Extract measurement
        if 'measurement' in json_data:
            measurement_data = json_data['measurement']
            json_format.ParseDict(measurement_data, message.measurement)
        else:
            logger.error("No 'measurement' key found in the message.")

        logger.info(f"Received MeasurementValue: {message}")
        # Handle the message as needed

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
    except json_format.ParseError as e:
        logger.error(f"Protobuf parsing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def sub_location_message_data(sample):
    """
    Callback function for LocationMessage messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    try:
        json_data = json.loads(json_string)
        message = val_standard_pb2.LocationMessage()

        # Extract mmsi and publish_stamp
        message.mmsi = json_data.get('mmsi', 0)
        if 'publish_stamp' in json_data:
            message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
            message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

        # Extract location
        if 'location' in json_data:
            location_data = json_data['location']
            # Map enum fields if necessary
            if 'quality' in location_data:
                quality_str = location_data['quality']
                try:
                    location_data['quality'] = val_standard_pb2.Location.Quality.Value(quality_str)
                except ValueError:
                    location_data['quality'] = val_standard_pb2.Location.NO_FIX
            json_format.ParseDict(location_data, message.location)
        else:
            logger.error("No 'location' key found in the message.")

        logger.info(f"Received LocationMessage: {message}")
        # Handle the message as needed

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
    except json_format.ParseError as e:
        logger.error(f"Protobuf parsing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

# def sub_alerts_data(sample):
#     """
#     Callback function for Alerts messages.
#     """
#     try:
#         json_string = sample.payload.decode('utf-8')
#     except UnicodeDecodeError:
#         json_string = sample.payload.decode('utf-8', errors='replace')
#         logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

#     try:
#         json_data = json.loads(json_string)
#         message = val_standard_pb2.Alerts()

#         # Extract mmsi and publish_stamp
#         message.mmsi = json_data.get('mmsi', 0)
#         if 'publish_stamp' in json_data:
#             message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
#             message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

#         # Extract alerts
#         if 'alerts' in json_data:
#             for alert_data in json_data['alerts']:
#                 # Check if 'alert' key exists and extract it
#                 if 'alert' in alert_data:
#                     alert_fields = alert_data['alert']
#                 else:
#                     alert_fields = alert_data  # Assume alert_data contains the fields directly

#                 alert_message = val_standard_pb2.Alert()

#                 # Map enum fields if necessary
#                 alert_enum_fields = {
#                     'category': val_standard_pb2.Alert.Category,
#                     'priority': val_standard_pb2.Alert.Priority,
#                     'ack_scheme': val_standard_pb2.Alert.AckScheme,
#                     'audio': val_standard_pb2.Alert.Audio,
#                     'visual': val_standard_pb2.Alert.Visual,
#                 }

#                 for field, enum_type in alert_enum_fields.items():
#                     if field in alert_fields:
#                         enum_str = alert_fields[field]
#                         try:
#                             alert_fields[field] = enum_type.Value(enum_str)
#                         except ValueError:
#                             alert_fields[field] = enum_type.Value('UNKNOWN')

#                 # Parse activation_time
#                 if 'activation_time' in alert_fields:
#                     activation_time_data = alert_fields['activation_time']
#                     activation_time = val_standard_pb2.Timestamp()
#                     activation_time.sec = activation_time_data.get('sec', 0)
#                     activation_time.nanosec = activation_time_data.get('nanosec', 0)
#                     alert_fields['activation_time'] = activation_time

#                 json_format.ParseDict(alert_fields, alert_message)
#                 message.alerts.append(alert_message)
#         else:
#             logger.error("No 'alerts' key found in the message.")

#         logger.info(f"Received Alerts: {message}")
#         # Handle the message as needed

#     except json.JSONDecodeError as e:
#         logger.error(f"JSON decoding error: {e}")
#     except json_format.ParseError as e:
#         logger.error(f"Protobuf parsing error: {e}")
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")

#updated:
def sub_alerts_data(sample):
    """
    Callback function for Alerts messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    try:
        json_data = json.loads(json_string)
        message = val_standard_pb2.Alerts()

        # Extract mmsi and publish_stamp
        message.mmsi = json_data.get('mmsi', 0)
        if 'publish_stamp' in json_data:
            message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
            message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

        # Extract health
        if 'health' in json_data:
            health_str = json_data['health'].upper()
            try:
                message.health = val_standard_pb2.Alerts.Health.Value(health_str)
            except ValueError:
                message.health = val_standard_pb2.Alerts.Health.Value('UNKNOWN')
        else:
            message.health = val_standard_pb2.Alerts.Health.Value('UNKNOWN')

        # Extract alerts
        if 'alerts' in json_data:
            for alert_data in json_data['alerts']:
                # Check if 'alert' key exists and extract it
                if 'alert' in alert_data:
                    alert_fields = alert_data['alert']
                else:
                    alert_fields = alert_data  # Assume alert_data contains the fields directly

                alert_message = val_standard_pb2.Alert()

                # Map enum fields if necessary
                alert_enum_fields = {
                    'category': val_standard_pb2.Alert.Category,
                    'priority': val_standard_pb2.Alert.Priority,
                    'ack_scheme': val_standard_pb2.Alert.AckScheme,
                    'audio': val_standard_pb2.Alert.Audio,
                    'visual': val_standard_pb2.Alert.Visual,
                }

                for field, enum_type in alert_enum_fields.items():
                    if field in alert_fields:
                        enum_str = alert_fields[field].upper()
                        try:
                            alert_fields[field] = enum_type.Value(enum_str)
                        except ValueError:
                            alert_fields[field] = enum_type.Value('UNKNOWN')

                # Parse activation_time
                if 'activation_time' in alert_fields:
                    activation_time_data = alert_fields['activation_time']
                    activation_time = val_standard_pb2.Timestamp()
                    activation_time.sec = activation_time_data.get('sec', 0)
                    activation_time.nanosec = activation_time_data.get('nanosec', 0)
                    alert_fields['activation_time'] = activation_time

                json_format.ParseDict(alert_fields, alert_message)
                message.alerts.append(alert_message)
        else:
            logger.error("No 'alerts' key found in the message.")

        logger.info(f"Received Alerts: {message}")
        # Handle the message as needed

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
    except json_format.ParseError as e:
        logger.error(f"Protobuf parsing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

# def sub_vessel_statics_data(sample):
#     """
#     Callback function for VesselStaticsMessage messages.
#     """
#     try:
#         json_string = sample.payload.decode('utf-8')
#     except UnicodeDecodeError:
#         json_string = sample.payload.decode('utf-8', errors='replace')
#         logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

#     try:
#         json_data = json.loads(json_string)
#         message = val_standard_pb2.VesselStaticsMessage()

#         # Extract mmsi and publish_stamp
#         message.mmsi = json_data.get('mmsi', 0)
#         if 'publish_stamp' in json_data:
#             message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
#             message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

#         # Extract vessel_statics
#         if 'vessel_statics' in json_data:
#             vessel_statics_data = json_data['vessel_statics']
#             json_format.ParseDict(vessel_statics_data, message.statics)
#         else:
#             logger.error("No 'vessel_statics' key found in the message.")

#         logger.info(f"Received VesselStaticsMessage: {message}")
#         # Handle the message as needed

#     except json.JSONDecodeError as e:
#         logger.error(f"JSON decoding error: {e}")
#     except json_format.ParseError as e:
#         logger.error(f"Protobuf parsing error: {e}")
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")

#updated:
def sub_vessel_statics_data(sample):
    """
    Callback function for VesselStaticsMessage messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    try:
        json_data = json.loads(json_string)
        message = val_standard_pb2.VesselStaticsMessage()

        # Extract mmsi and publish_stamp
        message.mmsi = json_data.get('mmsi', 0)
        if 'publish_stamp' in json_data:
            message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
            message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

        # Extract vessel_statics
        if 'vessel_statics' in json_data:
            vessel_statics_data = json_data['vessel_statics']

            # Handle enum fields if any
            enum_fields = {
                'model': val_standard_pb2.VesselStatics.Model,
                'propulsion_type': val_standard_pb2.VesselStatics.PropulsionType,
            }

            for field, enum_type in enum_fields.items():
                if field in vessel_statics_data:
                    enum_str = vessel_statics_data[field]
                    try:
                        vessel_statics_data[field] = enum_type.Value(enum_str.upper())
                    except ValueError:
                        vessel_statics_data[field] = enum_type.Value('UNKNOWN')

            json_format.ParseDict(vessel_statics_data, message.statics)
        else:
            logger.error("No 'vessel_statics' key found in the message.")

        logger.info(f"Received VesselStaticsMessage: {message}")
        # Handle the message as needed

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
    except json_format.ParseError as e:
        logger.error(f"Protobuf parsing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def sub_assignments_data(sample):
    """
    Callback function for Assignments messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    try:
        json_data = json.loads(json_string)
        message = val_standard_pb2.Assignments()

        # Extract publish_stamp
        if 'publish_stamp' in json_data:
            message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
            message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

        # Extract assignments
        if 'assignments' in json_data:
            for assignment_data in json_data['assignments']:
                # Check if 'assignment' key exists and extract it
                if 'assignment' in assignment_data:
                    assignment_fields = assignment_data['assignment']
                else:
                    assignment_fields = assignment_data  # Assume assignment_data contains the fields directly

                assignment_message = val_standard_pb2.Assignment()

                # Map enum fields if necessary
                if 'state' in assignment_fields:
                    state_str = assignment_fields['state']
                    try:
                        assignment_fields['state'] = val_standard_pb2.Assignment.State.Value(state_str)
                    except ValueError:
                        assignment_fields['state'] = val_standard_pb2.Assignment.UNKNOWN

                json_format.ParseDict(assignment_fields, assignment_message)
                message.assignments.append(assignment_message)
        else:
            logger.error("No 'assignments' key found in the message.")

        logger.info(f"Received Assignments: {message}")
        # Handle the message as needed

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
    except json_format.ParseError as e:
        logger.error(f"Protobuf parsing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def sub_vessel_envelope_data(sample):
    """
    Callback function for VesselEnvelope messages.
    """
    try:
        json_string = sample.payload.decode('utf-8')
    except UnicodeDecodeError:
        json_string = sample.payload.decode('utf-8', errors='replace')
        logger.warning(f"Failed to decode payload as UTF-8 for key: {sample.key_expr}")

    try:
        json_data = json.loads(json_string)
        message = val_standard_pb2.VesselEnvelope()

        # Extract mmsi
        message.mmsi = json_data.get('mmsi', 0)

        # Extract publish_stamp
        if 'publish_stamp' in json_data:
            message.publish_stamp.sec = json_data['publish_stamp'].get('sec', 0)
            message.publish_stamp.nanosec = json_data['publish_stamp'].get('nanosec', 0)

        # Extract other fields if present in the envelope
        if 'measurement_properties_messages' in json_data:
            for mp_data in json_data['measurement_properties_messages']:
                mp_message = val_standard_pb2.MeasurementPropertiesMessage()
                json_format.ParseDict(mp_data, mp_message)
                message.measurement_properties_messages.append(mp_message)

        if 'measurement_values' in json_data:
            for mv_data in json_data['measurement_values']:
                mv_message = val_standard_pb2.MeasurementValue()
                json_format.ParseDict(mv_data, mv_message)
                message.measurement_values.append(mv_message)

        if 'ais_vessel_message' in json_data:
            json_format.ParseDict(json_data['ais_vessel_message'], message.ais_vessel_message)

        if 'vessel_statics_message' in json_data:
            json_format.ParseDict(json_data['vessel_statics_message'], message.vessel_statics_message)

        if 'location_message' in json_data:
            json_format.ParseDict(json_data['location_message'], message.location_message)

        if 'alerts' in json_data:
            for alert_data in json_data['alerts']:
                alert_message = val_standard_pb2.Alert()
                json_format.ParseDict(alert_data, alert_message)
                message.alerts.append(alert_message)

        if 'exercise_state' in json_data:
            json_format.ParseDict(json_data['exercise_state'], message.exercise_state)

        if 'assignments' in json_data:
            json_format.ParseDict(json_data['assignments'], message.assignments)

        if 'autopilot_settings' in json_data:
            for ap_data in json_data['autopilot_settings']:
                ap_message = val_standard_pb2.AutopilotSettings()
                json_format.ParseDict(ap_data, ap_message)
                message.autopilot_settings.append(ap_message)

        logger.info(f"Received VesselEnvelope: {message}")
        # Handle the message as needed

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
    except json_format.ParseError as e:
        logger.error(f"Protobuf parsing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

# 
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

    # Vessels
    key_expr_vessels = "val/amoc/vessels"
    sub_vessels = session.declare_subscriber(
        key_expr_vessels,
        sub_vessels_data,
    )
    subscriptions.append(sub_vessels)
    logger.info(f"Subscribed to: {key_expr_vessels}")

    # MeasurementValue
    key_expr_measurement_value = "val/amoc/**/value" # "val/amoc/**/measurement"
    sub_measurement_value = session.declare_subscriber(
        key_expr_measurement_value,
        sub_measurement_value_data,
    )
    subscriptions.append(sub_measurement_value)
    logger.info(f"Subscribed to: {key_expr_measurement_value}")

    # LocationMessage
    key_expr_location_message = "val/amoc/**/location"
    sub_location_message = session.declare_subscriber(
        key_expr_location_message,
        sub_location_message_data,
    )
    subscriptions.append(sub_location_message)
    logger.info(f"Subscribed to: {key_expr_location_message}")

    # Alerts
    key_expr_alerts = "val/amoc/**"
    sub_alerts = session.declare_subscriber(
        key_expr_alerts,
        sub_alerts_data,
    )
    subscriptions.append(sub_alerts)
    logger.info(f"Subscribed to: {key_expr_alerts}")

    # VesselStaticsMessage
    key_expr_vessel_statics = "val/amoc/**/vessel_statics"
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
    
    # VesselEnvelope
    key_expr_vessel_envelope = "val/amoc/**/vessel_envelope"
    sub_vessel_envelope = session.declare_subscriber(
        key_expr_vessel_envelope,
        sub_vessel_envelope_data,
    )
    subscriptions.append(sub_vessel_envelope)
    logger.info(f"Subscribed to: {key_expr_vessel_envelope}")


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
