import os
import pytest
from unittest import mock
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './scritps')))
from yolov5_detector import YOLODetector
from database_setup import DatabaseManager

from logger import get_logger

# Mock YOLOv5 detection model
class MockYOLOv5:
    def __init__(self, model_path):
        self.names = ["background", "person", "car"]  # Example class names
        
    def __call__(self, image):
        # Simulate the detection of one object in the image
        return mock.Mock(
            xywh=[[[10, 20, 100, 200, 0.95, 1]]],  # Mock result (x, y, w, h, confidence, class_id)
        )

# Mock DatabaseManager to avoid actual database interaction
class MockDatabaseManager:
    def __init__(self):
        self.insert_called = False
    
    def create_yolo_detection_table(self):
        pass  # No database interaction
    
    def insert_yolo_detection(self, detections):
        self.insert_called = True
        # Check if the correct structure is passed
        assert isinstance(detections, list)
        assert isinstance(detections[0], dict)
        assert "image_name" in detections[0]
        assert "object_class" in detections[0]
        assert "confidence_score" in detections[0]
        assert "bounding_box" in detections[0]

# Test case for detecting objects with a valid image
@pytest.fixture
def yolo_detector():
    # Mock the YOLOv5 and DatabaseManager to create the detector
    mock_model = MockYOLOv5("mock_model_path")
    mock_db_manager = MockDatabaseManager()
    return YOLODetector("mock_model_path", mock_db_manager)

# Test: Image detection works and returns the expected structure
def test_detect_objects(yolo_detector):
    # Mock the image reading function to return a dummy image
    with mock.patch("cv2.imread", return_value="dummy_image"):
        detections = yolo_detector.detect_objects("dummy_image_path.jpg")
        
    # Assert that detections is not empty
    assert len(detections) > 0
    assert "image_name" in detections[0]
    assert "object_class" in detections[0]
    assert "confidence_score" in detections[0]
    assert "bounding_box" in detections[0]
    assert detections[0]["object_class"] == "person"  # Based on our mock class names

# Test: No object detected (empty result)
def test_no_objects_detected(yolo_detector):
    # Mock YOLOv5 to return no detections
    with mock.patch.object(yolo_detector.model, "__call__", return_value=mock.Mock(xywh=[[]])):
        detections = yolo_detector.detect_objects("empty_image_path.jpg")
        assert len(detections) == 0  # No objects detected

# Test: Process and save detections works
def test_process_and_save_detections(yolo_detector):
    # Mock image folder and list of images
    with mock.patch("os.listdir", return_value=["image1.jpg", "image2.jpg"]):
        with mock.patch("cv2.imread", return_value="dummy_image"):
            # Mock the insert_yolo_detection method to track calls
            yolo_detector.db_manager.insert_yolo_detection = mock.MagicMock()
            
            yolo_detector.process_and_save_detections("/mock/image/folder")
            
            # Assert that the detection results were inserted into the database
            yolo_detector.db_manager.insert_yolo_detection.assert_called()
            assert yolo_detector.db_manager.insert_called

# Test: Error handling when image cannot be loaded
def test_image_load_failure(yolo_detector):
    # Mock cv2.imread to return None (image not found)
    with mock.patch("cv2.imread", return_value=None):
        detections = yolo_detector.detect_objects("invalid_image_path.jpg")
        
    # Assert no detections and that error was logged
    assert len(detections) == 0
    # Ensure logging occurs by asserting calls to logger
    yolo_detector.logger.error.assert_called_with("Failed to load image: invalid_image_path.jpg")

# Test: Logging when no objects are detected in an image
def test_no_detection_logging(yolo_detector):
    with mock.patch("cv2.imread", return_value="dummy_image"):
        with mock.patch.object(yolo_detector.model, "__call__", return_value=mock.Mock(xywh=[[]])):
            # Mock logging
            with mock.patch.object(yolo_detector.logger, "warning") as mock_warning:
                yolo_detector.detect_objects("image_with_no_detection.jpg")
                mock_warning.assert_called_with("No objects detected in image_with_no_detection.jpg.")

# Test: Ensure database manager insert method is called with correct data
def test_insert_detection_data():
    mock_db_manager = MockDatabaseManager()
    detections = [{
        "image_name": "image1.jpg",
        "object_class": "car",
        "confidence_score": 0.95,
        "bounding_box": {"x_min": 10, "y_min": 20, "width": 100, "height": 200},
        "timestamp": datetime.now()
    }]
    
    mock_db_manager.insert_yolo_detection(detections)
    
    # Check that insert_yolo_detection was called and data is correct
    assert mock_db_manager.insert_called

