# utils.py

import logging
from google.protobuf import json_format
import val_standard_pb2  # Import the generated Protobuf classes
import json

def parse_message(json_string, message_type, root_key=None, merge_top_level_keys=[]):
    """
    Parses a JSON string into the specified Protobuf message type.

    Args:
        json_string (str): The JSON string to parse.
        message_type (Message): The Protobuf message class.
        root_key (str): The root key under which the main data is nested.
        merge_top_level_keys (list of str): List of keys to merge from top-level into nested data.

    Returns:
        message: An instance of the Protobuf message.
    """
    try:
        json_data = json.loads(json_string)
        if root_key:
            if root_key in json_data:
                nested_data = json_data[root_key]
            else:
                logging.error(f"Key '{root_key}' not found in JSON data")
                return None
            # Merge specified top-level keys into nested data
            for key in merge_top_level_keys:
                if key in json_data:
                    nested_data[key] = json_data[key]
            json_data = nested_data  # Now json_data is the nested data with merged top-level keys
        message = message_type()
        json_format.ParseDict(json_data, message)
        return message
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error: {e}")
    except json_format.ParseError as e:
        logging.error(f"Protobuf parsing error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    return None



def publish_message(session, key, message):
    """
    Serializes and publishes a Protobuf message to a Zenoh key.

    Args:
        session: The Zenoh session.
        key (str): The Zenoh key expression to publish to.
        message: The Protobuf message to serialize and publish.
    """
    try:
        serialized_message = message.SerializeToString()
        session.put(key, serialized_message)
        logging.info(f"Published message to {key}")
    except Exception as e:
        logging.error(f"Error publishing message to {key}: {e}")
