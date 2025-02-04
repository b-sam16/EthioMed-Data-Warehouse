import os
import cv2
import json
import torch
import datetime
from database_setup import DatabaseManager  # Import DatabaseManager from your database setup module
from yolov5 import YOLOv5

# Ensure the src folder is in the Python path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from logger import get_logger  # Import your logger

class YOLODetector:
    def __init__(self, model_path, db_manager):
        """Initialize with the path to the YOLO model and DatabaseManager."""
        self.logger = get_logger("yolo_detection")  # Set up logger for this module
        self.model = YOLOv5(model_path)  # Load the YOLOv5 model
        self.db_manager = db_manager
        self.logger.info("YOLO model loaded successfully.")

    def detect_objects(self, image_path):
        """Run YOLO detection on a single image."""
        self.logger.info(f"Processing image: {image_path}")
        image = cv2.imread(image_path)
        
        if image is None:
            self.logger.error(f"Failed to load image: {image_path}")
            return []

        results = self.model(image)  # Run YOLOv5 detection
        detections = []
        
        for *box, conf, cls in results.xywh[0]:  # Extract the bounding box, confidence, and class
            # Prepare detection data
            detection = {
                "image_name": os.path.basename(image_path),
                "object_class": self.model.names[int(cls)],  # Get the class name from YOLOv5's names
                "confidence_score": conf.item(),
                "bounding_box": {
                    "x_min": box[0].item(),
                    "y_min": box[1].item(),
                    "width": box[2].item(),
                    "height": box[3].item()
                },
                "timestamp": datetime.datetime.now()
            }
            detections.append(detection)
        
        self.logger.info(f"Detection completed for image: {image_path}")
        return detections

    def process_and_save_detections(self, image_folder):
        """Process all images in a folder and save the detection results."""
        self.logger.info(f"Starting object detection for images in folder: {image_folder}")
        
        for image_file in os.listdir(image_folder):
            if image_file.endswith(('.jpg', '.png', '.jpeg')):
                image_path = os.path.join(image_folder, image_file)
                try:
                    detections = self.detect_objects(image_path)
                    if detections:
                        self.db_manager.insert_yolo_detection(detections)  # Insert detection results into DB
                        self.logger.info(f"Detection results for {image_file} inserted into database.")
                    else:
                        self.logger.warning(f"No objects detected in {image_file}.")
                except Exception as e:
                    self.logger.error(f"Error processing image {image_file}: {e}")
        
        self.logger.info("Object detection process completed for all images.")

def main():
    # Initialize the database manager
    db_manager = DatabaseManager()

    # Ensure the table for YOLO detections exists
    db_manager.create_yolo_detection_table()

    # Specify the folder containing the images
    image_folder = "./data/photos/chemed"  # Change path to your images folder
    if not os.path.exists(image_folder):
        db_manager.logger.error(f"Image folder {image_folder} does not exist.")
        return

    # Initialize the YOLO detector with the path to the pre-trained model
    model_path = "./yolov5s.pt"  # Path to your YOLO model file
    if not os.path.exists(model_path):
        db_manager.logger.error(f"Model file {model_path} not found.")
        return

    yolo_detector = YOLODetector(model_path, db_manager)

    # Run object detection and store results
    yolo_detector.process_and_save_detections(image_folder)

    print("Detection and storage completed successfully!")

if __name__ == "__main__":
    main()
