from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt
from scipy.spatial.transform import Rotation as R
import ikpy.chain
import json
import numpy as np

# MQTT Settings
broker = 'localhost'         # Replace with your broker IP/domain
port = 1883                  # Use 9001 for WebSocket
topic_sub = 'robot/command'     # Topic to subscribe
topic_pub = 'robot/joints'      # T


client = mqtt.Client(transport='websockets')
client.connect(broker, 9001, 60)

robot = ikpy.chain.Chain.from_urdf_file("./urdf/gazebo_robot_arm.urdf", active_links_mask=[False, True, True, True, True, True, True, True])


def inverse_kinematics(end_effector_position, end_effector_orientation):
    ik = robot.inverse_kinematics(target_position=end_effector_position, target_orientation=end_effector_orientation, orientation_mode="z")
    print(ik)

    return ik

# Optional: define callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker.")
        client.subscribe(topic_sub)
        print(f"Subscribed to `{topic_sub}`")
    else:
        print(f"Failed to connect: return code {rc}")



# Define the on_message callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(payload)
    payload = json.loads(payload)

    if payload["move"] == "fk":
        joint_angles = [0] + [
             payload["joints"]["joint_1"], 
             payload["joints"]["joint_2"], 
             payload["joints"]["joint_3"], 
             payload["joints"]["joint_4"], 
             payload["joints"]["joint_5"], 
             payload["joints"]["joint_6"],
             0
        ]
        end_effector_frame = robot.forward_kinematics(joint_angles)     
        position = end_effector_frame[:3, 3] 
        rotation_matrix = end_effector_frame[:3, :3]
        r = R.from_matrix(rotation_matrix)
        rpy = r.as_euler('xyz', degrees=False) 

        data = {
            "position": {
                "x": position[0],
                "y": position[1],
                "z": position[2] 
            },
            "eular": {
                "roll": rpy[0],
                "pitch": rpy[1],
                "yaw": rpy[2]
            },
            "joints": {
                "joint_1": payload["joints"]["joint_1"],
                "joint_2": payload["joints"]["joint_2"],
                "joint_3": payload["joints"]["joint_3"],
                "joint_4": payload["joints"]["joint_4"],
                "joint_5": payload["joints"]["joint_5"],
                "joint_6": payload["joints"]["joint_6"],
            }
        }

    elif payload["move"] == "ik":

        # Desired end effector position (in meters)
        target_position = [
            payload["position"]["x"],
            payload["position"]["y"],
            payload["position"]["z"]
        ]

        # Desired end effector orientation (as rotation matrix)
        rotation = R.from_euler('xyz', [
            payload["eular"]["roll"],
            payload["eular"]["pitch"],
            payload["eular"]["yaw"]])
        target_orientation = rotation.as_matrix()  # 3

        ik = robot.inverse_kinematics(target_position=target_position, target_orientation=target_orientation, orientation_mode="all")
    
        data = {
            "joints": {
                "joint_1": ik[1].item(),
                "joint_2": ik[2].item(),
                "joint_3": ik[3].item(),
                "joint_4": ik[4].item(),
                "joint_5": ik[5].item(),
                "joint_6": ik[6].item(),
            }
        }

    print ("Public 111")
    client.publish(topic_pub, json.dumps(data))


client.on_connect = on_connect
client.on_message = on_message

client.loop_start()

app = Flask(__name__)




if __name__ == '__main__':
    app.run(debug=False, port=5000, use_reloader=False)
