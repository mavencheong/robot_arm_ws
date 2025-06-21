import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import URDFLoader from 'urdf-loader';
import mqtt from 'mqtt';

// Scene setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(2, 2, 2);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Lighting
scene.add(new THREE.AmbientLight(0xffffff, 0.3));
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(5, 5, 5);
scene.add(dirLight);

const gridHelper = new THREE.GridHelper(2, 20); // 2 units wide, 20 subdivisions
scene.add(gridHelper);

const axesHelper = new THREE.AxesHelper(0.5); // size in units
axesHelper.rotation.x = -Math.PI / 2; // Match robot rotation
scene.add(axesHelper);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.update();
let  endEffector
// URDF Loading
const loader = new URDFLoader();
loader.load(
  'urdf/gazebo_robot_arm.urdf', // Adjust path as needed
  function (robot) {
    robot.rotation.x = -Math.PI / 2;
    scene.add(robot);

    // Animate a joint (optional)
    const joint = robot.joints['joint_1']; // Replace with real joint name
    let angle = 0;

    robot.traverse((node) => {
        if (node.isURDFJoint || node.isURDFLink) {
        const axesHelper = new THREE.AxesHelper(0.1); // size = 5 cm
        node.add(axesHelper);
        }
    });


    // function animate() {
    //   requestAnimationFrame(animate);

    // //   if (joint) {
    // //     angle += 0.01;
    // //     joint.setJointValue(Math.sin(angle));
    // //   }

    //   controls.update();
    //   renderer.render(scene, camera);
    // }

    // animate();
    endEffector = robot.getObjectByName('link_6_1'); 
  },
  undefined,
  function (err) {
    console.error("Error loading URDF:", err);
  }
);

const options = {
  connectTimeout: 4000,
  clientId: 'threejs_client_' + Math.random().toString(16).substr(2, 8),
  keepalive: 60,
  clean: true,
};

const mqttClient = mqtt.connect('ws://localhost:9001', options); // Port 9001 is default for WebSocket MQTT

mqttClient.on('connect', () => {
  console.log('✅ MQTT Connected');
  mqttClient.subscribe('robot/joints', (err) => {
    if (err) {
      console.error('Subscribe error:', err);
    }
  });
});

mqttClient.on('message', (topic, message) => {
  const data = JSON.parse(message.toString());
  console.log('📥 MQTT Data:', data);

//   // Example: Update joint values
//   if (robot && robot.joints) {
//     if (data.joint1 && robot.joints['joint1']) {
//       robot.joints['joint1'].setJointValue(data.joint1);
//     }
//     if (data.joint2 && robot.joints['joint2']) {
//       robot.joints['joint2'].setJointValue(data.joint2);
//     }
//   }
});

mqttClient.on('error', (err) => {
  console.error('MQTT Error:', err);
});


// Animate loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}


document.getElementById('btn-center').addEventListener('click', () => {
//   let endEffector = robot.getObjectByName("link_6_1");

endEffector.updateMatrixWorld(true);
const position = new THREE.Vector3();
const quaternion = new THREE.Quaternion();
const rotation = new THREE.Euler();

// Get world position and orientation
endEffector.getWorldPosition(position);
endEffector.getWorldQuaternion(quaternion);
rotation.setFromQuaternion(quaternion, 'ZYX');


    console.log(endEffector, position, quaternion)
});


animate();

// Handle window resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
