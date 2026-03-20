

import cv2
import numpy as np
from ultralytics import YOLO

# -----------------------------
# Load YOLO model (your trained model)
# -----------------------------
model = YOLO("best.pt")  # Use your custom-trained model

# -----------------------------
# Load stereo images
# -----------------------------
imgL = cv2.imread("left.jpg")
imgR = cv2.imread("right.jpg")

if imgL is None or imgR is None:
	raise FileNotFoundError("Could not load left.jpg or right.jpg. Check file paths.")

grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

# -----------------------------
# Stereo disparity (for visualization, not used in new matching method)
# -----------------------------
stereo = cv2.StereoBM_create(numDisparities=64, blockSize=15)
disparity = stereo.compute(grayL, grayR).astype(np.float32) / 16.0

# -----------------------------
# Camera parameters (replace with real calibration for best results)
# -----------------------------
f = 700      # focal length (pixels)
B = 0.1      # baseline (meters)

# -----------------------------
# Run YOLO on both images
# -----------------------------
resultsL = model(imgL)
resultsR = model(imgR)

# Find blue cube class index (assuming class names are in model.names)
blue_cube_class = None
if hasattr(model, 'names'):
	for k, v in model.names.items():
		if 'blue' in v.lower() and 'cube' in v.lower():
			blue_cube_class = k
			break

# Get blue cube detections from both images
def get_blue_cubes(results, blue_cube_class):
	cubes = []
	for r in results:
		boxes = r.boxes
		for box in boxes:
			cls = int(box.cls[0]) if hasattr(box, 'cls') else None
			if blue_cube_class is not None and cls != blue_cube_class:
				continue
			x1, y1, x2, y2 = map(int, box.xyxy[0])
			u = (x1 + x2) // 2
			v = (y1 + y2) // 2
			cubes.append({'box': (x1, y1, x2, y2), 'center': (u, v)})
	return cubes

cubesL = get_blue_cubes(resultsL, blue_cube_class)
cubesR = get_blue_cubes(resultsR, blue_cube_class)

# Match cubes by vertical proximity (y) and minimal horizontal disparity (x)
def match_cubes(cubesL, cubesR, max_y_diff=20, max_x_diff=200):
	matches = []
	usedR = set()
	for i, cL in enumerate(cubesL):
		uL, vL = cL['center']
		best_j = -1
		best_dx = None
		for j, cR in enumerate(cubesR):
			if j in usedR:
				continue
			uR, vR = cR['center']
			if abs(vL - vR) > max_y_diff:
				continue
			dx = uL - uR
			if dx <= 0 or dx > max_x_diff:
				continue
			if best_dx is None or dx < best_dx:
				best_dx = dx
				best_j = j
		if best_j >= 0:
			matches.append((cL, cubesR[best_j], best_dx))
			usedR.add(best_j)
	return matches

matches = match_cubes(cubesL, cubesR)

if not matches:
	print("No matching blue cubes detected in both images.")
else:
	for cL, cR, disparity_px in matches:
		uL, vL = cL['center']
		uR, vR = cR['center']
		# Depth calculation: Z = f * B / disparity
		if disparity_px == 0:
			Z = float('inf')
		else:
			Z = f * B / disparity_px
		# Draw boxes and lines
		x1, y1, x2, y2 = cL['box']
		cv2.rectangle(imgL, (x1, y1), (x2, y2), (0, 255, 255), 2)
		label = f"Blue Cube Z={Z:.2f}m"
		cv2.putText(imgL, label, (x1, y1-10),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
		print(f"3D position (blue cube): X={uL}, Y={vL}, Z={Z:.2f} meters (disparity: {disparity_px})")

# -----------------------------
# Show results
# -----------------------------
cv2.imshow("Detection + Depth", imgL)
cv2.waitKey(0)
cv2.destroyAllWindows()
