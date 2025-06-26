import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { FontLoader } from 'three/examples/jsm/loaders/FontLoader.js';
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js';
import URDFLoader from 'urdf-loader';
import mqtt from 'mqtt';


const options = {
  connectTimeout: 4000,
  clientId: 'threejs_client_' + Math.random().toString(16).substr(2, 8),
  keepalive: 60,
  clean: true,
};


const mqttClient = mqtt.connect('ws://localhost:9001', options); // Port 9001 is default for WebSocket MQTT
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

// Function to create 2D text sprite
function createTextSprite(text, color) {
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  context.font = '48px Arial';
  context.fillStyle = color;
  context.fillText(text, 10, 50);

  const texture = new THREE.CanvasTexture(canvas);
  const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true });
  const sprite = new THREE.Sprite(spriteMaterial);
  sprite.scale.set(0.2, 0.1, 1); // adjust size
  return sprite;
}

// Create and position label sprites
const labelX = createTextSprite('X', '#ff0000');
labelX.position.set(0.5, 0, 0);  // slightly beyond X axis
axesHelper.add(labelX);           // attach to axes

const labelY = createTextSprite('Y', '#00ff00');
labelY.position.set(0, 0.5, 0);  // slightly beyond Y axis
axesHelper.add(labelY);

const labelZ = createTextSprite('Z', '#0000ff');
labelZ.position.set(0, 0, 0.5);  // slightly beyond Z axis
axesHelper.add(labelZ);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.update();
let endEffector
let base;
let joints = [];
let moveStartTime = null;
let jointTargets = {};
let jointStarts = {};
let jointNames = [];
let jointSpeeds = 0.15; // radians per second
let myrobot;
let moveDuration = 0.5; // seconds
// URDF Loading
const loader = new URDFLoader();
loader.load(
  'urdf/gazebo_robot_arm.urdf', // Adjust path as needed
  function (robot) {
    
    robot.rotation.x = -Math.PI / 2;
    robot.position.y = 0.06
    // robot.position.z = 1
    scene.add(robot);
    myrobot=  robot
    // Animate a joint (optional)

    joints.push(robot.joints['joint_1'])
    joints.push(robot.joints['joint_2'])
    joints.push(robot.joints['joint_3'])
    joints.push(robot.joints['joint_4'])
    joints.push(robot.joints['joint_5'])
    joints.push(robot.joints['joint_6'])
    joints.push(robot.joints['joint_7'])
    jointNames.push(...Object.keys(robot.joints));
    jointNames.forEach(name => {
        jointStarts[name] = robot.joints[name].angle;
        jointTargets[name] = robot.joints[name].angle;
    });

    const joint = robot.joints['joint_5']; // Replace with real joint name
    let angle = 0;

    robot.traverse((node) => {

      if (node.isURDFJoint || node.isURDFLink) {
        const axesHelper = new THREE.AxesHelper(0.2); // size = 5 cm
        node.add(axesHelper);
      }
    });

    angle = -90 * (Math.PI / 180);


    //URDF <--> THREEJS XYZ mapping
    //=============================
    // Z <==> Y
    // X <==> X
    // Y <==> Z

    // joint.setJointValue(angle);

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

    const sphere = new THREE.Mesh(
      new THREE.SphereGeometry(0.01),
      new THREE.MeshBasicMaterial({ color: 0xff0000 })
    );


    endEffector = robot.getObjectByName('link_7_1');

    endEffector.getWorldPosition(sphere.position);

    base = robot.getObjectByName('base_link');
    const position = new THREE.Vector3();
    base.getWorldPosition(position);


    scene.add(sphere);

    animate();
  },
  undefined,
  function (err) {
    console.error("Error loading URDF:", err);
  }
);



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

  if (data?.joints){

    moveToJointTargets([
      data.joints.joint_1,
      data.joints.joint_2,
      data.joints.joint_3,
      data.joints.joint_4,
      data.joints.joint_5,
      data.joints.joint_6,
      data.joints.joint_7   
    ])
    // jointTargets['joint_1'] = data.joints.joint_1;
    // jointTargets['joint_2'] = data.joints.joint_2;
    // jointTargets['joint_3'] = data.joints.joint_3;
    // jointTargets['joint_4'] = data.joints.joint_4;
    // jointTargets['joint_5'] = data.joints.joint_5;
    // jointTargets['joint_6'] = data.joints.joint_6;
    
  }
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
// function animate() {
//   requestAnimationFrame(animate);
//   renderer.render(scene, camera);
// }


document.getElementById('btn-center').addEventListener('click', () => {

  let data = getEndEffectorPositionAndEularAndJointsAngle();

  console.log(data)

  mqttClient.publish('robot/command', JSON.stringify({
    joints: {
      joint_1: 0.0,
      joint_2: 0.0,
      joint_3: 0.0,
      joint_4: 0.0,
      joint_5: 0.0,
      joint_6: 0.0,
      joint_7: 0.0
    },
    move: 'fk'
  }))

});

document.getElementById('btn-movexplus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.position.x = currentPosition.position.x + getMovementUnit(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-movexminus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.position.x = currentPosition.position.x - getMovementUnit(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})


document.getElementById('btn-moveyplus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.position.y = currentPosition.position.y + getMovementUnit(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-moveyminus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.position.y = currentPosition.position.y - getMovementUnit(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})


document.getElementById('btn-movezplus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.position.z = currentPosition.position.z + getMovementUnit(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-movezminus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.position.z = currentPosition.position.z - getMovementUnit(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})




document.getElementById('btn-moverplus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();
  currentPosition.move = 'ik';
  currentPosition.eular.roll = currentPosition.eular.roll + getMovementRadian(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-moverminus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.eular.roll = currentPosition.eular.roll - getMovementRadian(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})


document.getElementById('btn-movepplus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();
  currentPosition.move = 'ik';
  currentPosition.eular.pitch = currentPosition.eular.pitch + getMovementRadian(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-movepminus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.eular.pitch = currentPosition.eular.pitch - getMovementRadian(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})



document.getElementById('btn-moveyaplus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();
  currentPosition.move = 'ik';
  currentPosition.eular.yaw = currentPosition.eular.yaw + getMovementRadian(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-moveyaminus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.eular.yaw = currentPosition.eular.yaw - getMovementRadian(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})




document.getElementById('btn-north').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();
  currentPosition.move = 'ik';
  currentPosition.position.x = currentPosition.position.x + getMovementUnit(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-south').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.position.x = currentPosition.position.x - getMovementUnit(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})



document.getElementById('btn-east').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();
  currentPosition.move = 'ik';
  currentPosition.position.y = currentPosition.position.y - getMovementUnit(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})


document.getElementById('btn-west').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.position.y = currentPosition.position.y + getMovementUnit(); //move 5cm

  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})


document.getElementById('btn-northeast').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();
  currentPosition.move = 'ik';
  currentPosition.position.x = currentPosition.position.x + getMovementUnit(); //move 5cm
  currentPosition.position.y = currentPosition.position.y - getMovementUnit(); //move 5cm
  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})



document.getElementById('btn-northwest').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();
  currentPosition.move = 'ik';
  currentPosition.position.x = currentPosition.position.x + getMovementUnit(); //move 5cm
  currentPosition.position.y = currentPosition.position.y + getMovementUnit(); //move 5cm
  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-southeast').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.position.x = currentPosition.position.x - getMovementUnit(); //move 5cm
  currentPosition.position.y = currentPosition.position.y - getMovementUnit(); //move 5cm
  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-southwest').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.move = 'ik';
  currentPosition.position.x = currentPosition.position.x - getMovementUnit(); //move 5cm
  currentPosition.position.y = currentPosition.position.y + getMovementUnit(); //move 5cm
  console.log(currentPosition)
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-joint1plus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_1"] = currentPosition.joints["joint_1"] + getMovementRadian();
  currentPosition.move = 'fk';

  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-joint1minus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_1"] = currentPosition.joints["joint_1"] - getMovementRadian();
  currentPosition.move = 'fk';
  
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})


document.getElementById('btn-joint2plus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_2"] = currentPosition.joints["joint_2"] + getMovementRadian();
  currentPosition.move = 'fk';

  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-joint2minus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_2"] = currentPosition.joints["joint_2"] - getMovementRadian();
  currentPosition.move = 'fk';
  
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})


document.getElementById('btn-joint3plus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_3"] = currentPosition.joints["joint_3"] + getMovementRadian();
  currentPosition.move = 'fk';

  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-joint3minus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_3"] = currentPosition.joints["joint_3"] - getMovementRadian();
  currentPosition.move = 'fk';
  
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})


document.getElementById('btn-joint4plus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_4"] = currentPosition.joints["joint_4"] + getMovementRadian();
  currentPosition.move = 'fk';

  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-joint4minus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_4"] = currentPosition.joints["joint_4"] - getMovementRadian();
  currentPosition.move = 'fk';
  
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})


document.getElementById('btn-joint5plus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_5"] = currentPosition.joints["joint_5"] + getMovementRadian();
  currentPosition.move = 'fk';

  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-joint5minus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_5"] = currentPosition.joints["joint_5"] - getMovementRadian();
  currentPosition.move = 'fk';
  
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})



document.getElementById('btn-joint6plus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_6"] = currentPosition.joints["joint_6"] + getMovementRadian();
  currentPosition.move = 'fk';

  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

document.getElementById('btn-joint6minus').addEventListener('click', () => {
  let currentPosition = getEndEffectorPositionAndEularAndJointsAngle();

  currentPosition.joints["joint_6"] = currentPosition.joints["joint_6"] - getMovementRadian();
  currentPosition.move = 'fk';
  
  mqttClient.publish('robot/command', JSON.stringify(currentPosition));
})

function moveToJointTargets(newAnglesArray, duration = 1.0) {
    jointNames.forEach((name, i) => {
        jointStarts[name] = myrobot.joints[name].angle;
        jointTargets[name] = newAnglesArray[i];
    });
    moveDuration = duration;
    moveStartTime = clock.getElapsedTime();
}

function getEndEffectorPositionAndEular() {
  let worldQuat = new THREE.Quaternion();
  endEffector.getWorldQuaternion(worldQuat);

  // Apply correction: rotate +90° around X to undo robot.rotation.x = -90°
  let correctionQuat = new THREE.Quaternion()
    .setFromAxisAngle(new THREE.Vector3(1, 0, 0), Math.PI / 2);

  // Important: multiply in this order
  let correctedQuat = correctionQuat.clone().multiply(worldQuat);

  // Convert corrected quaternion to Euler angles
  let urdfEuler = new THREE.Euler().setFromQuaternion(correctedQuat, 'XYZ');

  let position = new THREE.Vector3();
  endEffector.getWorldPosition(position)




  return {
    position: {
      x: position.x,
      y: -position.z,
      z: position.y - 0.06
    },
    eular: {
      roll: urdfEuler.x,
      pitch: urdfEuler.y,
      yaw: urdfEuler.z
    }
  }
}


function getEndEffectorPositionAndEularAndJointsAngle(){
  let position = getEndEffectorPositionAndEular();

  position.joints = {
    joint_1: myrobot.joints['joint_1'].angle,
    joint_2: myrobot.joints['joint_2'].angle,
    joint_3: myrobot.joints['joint_3'].angle,
    joint_4: myrobot.joints['joint_4'].angle,
    joint_5: myrobot.joints['joint_5'].angle,
    joint_6: myrobot.joints['joint_6'].angle,
    joint_7: myrobot.joints['joint_7'].angle
  }

  return position;
}

function getMovementUnit(){
  console.log(document.getElementById('txt-unit').value / 1000)
  return parseFloat(document.getElementById('txt-unit').value / 1000);
}

function getMovementRadian(){
  
  return parseFloat(((document.getElementById('txt-degree').value *  Math.PI ) / 180).toFixed(3))
}


function setTargetAngles(anglesArray) {
    jointNames.forEach((name, i) => {
        jointTargets[name] = anglesArray[i];
    });
}
function easeInOut(t) {
     return t * t * t * (t * (6 * t - 15) + 10);
}

const clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const elapsed = clock.getElapsedTime();
    let changed = false;

    if (moveStartTime !== null) {
        let t = (elapsed - moveStartTime) / moveDuration;
        t = Math.min(Math.max(t, 0), 1);  // Clamp between 0–1
        const easedT = easeInOut(t);

        jointNames.forEach(name => {
            const start = jointStarts[name];
            const target = jointTargets[name];
            const current = start + (target - start) * easedT;

            if (start != target){
              changed = true;
            }
            myrobot.joints[name].setJointValue(current);
        });

        if (t >= 1.0) moveStartTime = null;  // Done
    }

    if (changed){
      updateDisplay();
    }
    
    renderer.render(scene, camera);
}


function updateDisplay(){
  let position = getEndEffectorPositionAndEularAndJointsAngle();

  
  document.getElementById("pos-x").textContent = toMM(position.position.x)
  document.getElementById("pos-y").textContent = toMM(position.position.y)
  document.getElementById("pos-z").textContent = toMM(position.position.z)
  document.getElementById("ori-roll").textContent = angleToDegreee(position.eular.roll)
  document.getElementById("ori-pitch").textContent = angleToDegreee(position.eular.pitch)
  document.getElementById("ori-yaw").textContent = angleToDegreee(position.eular.yaw)
 
  document.getElementById("joint-1").textContent = angleToDegreee(position.joints["joint_1"])
  document.getElementById("joint-2").textContent = angleToDegreee(position.joints["joint_2"])
  document.getElementById("joint-3").textContent = angleToDegreee(position.joints["joint_3"])
  document.getElementById("joint-4").textContent = angleToDegreee(position.joints["joint_4"])
  document.getElementById("joint-5").textContent = angleToDegreee(position.joints["joint_5"])
  document.getElementById("joint-6").textContent = angleToDegreee(position.joints["joint_6"])
  
}

function angleToDegreee(radians) {


  if (radians == 0){
    return 0.000;
  }
  return  (radians * (180 / Math.PI)).toFixed(3)
}

function toMM(value){
  return (value * 1000).toFixed(3)
}

// 

// Handle window resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
