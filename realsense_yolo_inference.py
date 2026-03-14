import pyrealsense2 as rs
import numpy as np
import cv2
from ultralytics import YOLO

def main():
    # Load YOLO model
    print("Loading YOLO model...")
    model = YOLO('best.pt')
    print("Model loaded successfully!")
    
    # Configure Intel RealSense D455 camera
    pipeline = rs.pipeline()
    config = rs.config()
    
    # Enable color stream (1280x720 at 30fps - adjust as needed)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    
    # Optionally enable depth stream for distance measurements
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    
    # Start streaming
    print("Starting RealSense camera...")
    pipeline.start(config)
    print("Camera started successfully!")
    
    try:
        while True:
            # Wait for frames
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
            
            if not color_frame:
                continue
            
            # Convert images to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())
            
            # Run YOLO inference
            results = model(color_image, verbose=False)
            
            # Visualize results on the frame
            annotated_frame = results[0].plot()
            
            # Optional: Display depth information for detected objects
            if depth_frame:
                for result in results[0].boxes.data:
                    x1, y1, x2, y2, conf, cls = result
                    # Get center point of bounding box
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)
                    
                    # Get depth at center point (in meters)
                    depth = depth_frame.get_distance(center_x, center_y)
                    
                    # Display depth information on frame
                    label = f"{model.names[int(cls)]} {conf:.2f} - {depth:.2f}m"
                    cv2.putText(annotated_frame, label, (int(x1), int(y1) - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Display FPS
            fps = 1000 / results[0].speed['inference']
            cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show the frame
            cv2.imshow('RealSense D455 - YOLO Object Detection', annotated_frame)
            
            # Break loop with 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        # Stop streaming
        pipeline.stop()
        cv2.destroyAllWindows()
        print("Camera stopped and windows closed.")

if __name__ == "__main__":
    main()
