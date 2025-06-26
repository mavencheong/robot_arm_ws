import freenect
import cv2
import numpy as np
from ultralytics import YOLO

# ===== Kinect v1 Default Intrinsics =====
fx = 594.21
fy = 591.04
cx = 339.5
cy = 242.7

# ===== Load YOLOv8 (You can use yolov8n.pt, yolov8s.pt, or your custom model) =====
model = YOLO("yolov8n.pt")

# ===== Kinect Capture =====
def get_rgb():
    rgb, _ = freenect.sync_get_video()
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

def get_depth():
    depth, _ = freenect.sync_get_depth()
    return depth.astype(np.uint16)

# ===== Convert 2D pixel + depth to 3D point =====
def pixel_to_point(u, v, depth_val_mm):
    z = depth_val_mm / 1000.0  # mm → meters
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    return x, y, z

# ===== Main Loop =====
def main():
    while True:
        rgb = get_rgb()
        depth = get_depth()

        results = model(rgb)

        for det in results[0].boxes.data:
            x1, y1, x2, y2, conf, cls = det.cpu().numpy()
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            x_center = (x1 + x2) // 2
            y_center = (y1 + y2) // 2

            # ===== Use median depth from box instead of single pixel =====
            box_depth = depth[y1:y2, x1:x2]
            valid_depths = box_depth[box_depth > 0]
            if len(valid_depths) == 0:
                continue
            depth_val = np.median(valid_depths)

            # ===== Convert to 3D =====
            x3d, y3d, z3d = pixel_to_point(x_center, y_center, depth_val)

            # ===== Draw Results =====
            label = model.names[int(cls)]
            cv2.rectangle(rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(rgb, (x_center, y_center), 4, (0, 0, 255), -1)

            text = f"{label} @ ({x3d:.2f}, {y3d:.2f}, {z3d:.2f})m"
            cv2.putText(rgb, text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        # ===== Show the Image =====
        cv2.imshow("Kinect + YOLOv8 + 3D", rgb)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
