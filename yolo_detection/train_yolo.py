"""
YOLO Training Script
Fine-tune YOLO model on CARLA dataset
"""

import sys
from pathlib import Path
from ultralytics import YOLO
from loguru import logger

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from config import config


def train_yolo(
    base_model: str = "yolov8n.pt",
    data_yaml: str = "./datasets/carla_vehicles/data.yaml",
    epochs: int = 100,
    batch_size: int = 16,
    image_size: int = 640,
    device: str = "cuda",
    project: str = "./runs/train",
    name: str = "carla_vehicles"
):
    """
    Train YOLO model on CARLA vehicle dataset
    
    Args:
        base_model: Base YOLO model to fine-tune
        data_yaml: Path to dataset YAML file
        epochs: Number of training epochs
        batch_size: Training batch size
        image_size: Input image size
        device: 'cuda' or 'cpu'
        project: Project directory for results
        name: Experiment name
    """
    logger.info("Starting YOLO training...")
    logger.info(f"Base model: {base_model}")
    logger.info(f"Dataset: {data_yaml}")
    logger.info(f"Epochs: {epochs}, Batch size: {batch_size}")
    
    model = YOLO(base_model)
    
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=image_size,
        device=device,
        project=project,
        name=name,
        patience=50,
        save=True,
        plots=True,
        verbose=True
    )
    
    logger.success("Training complete!")
    logger.info(f"Best weights saved to: {project}/{name}/weights/best.pt")
    
    return results


def validate_model(model_path: str, data_yaml: str, device: str = "cuda"):
    """
    Validate trained model
    
    Args:
        model_path: Path to trained model weights
        data_yaml: Path to dataset YAML
        device: 'cuda' or 'cpu'
    """
    logger.info(f"Validating model: {model_path}")
    
    model = YOLO(model_path)
    results = model.val(data=data_yaml, device=device)
    
    logger.info(f"mAP50: {results.box.map50:.4f}")
    logger.info(f"mAP50-95: {results.box.map:.4f}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train YOLO on CARLA dataset")
    parser.add_argument("--model", default="yolov8n.pt", help="Base model")
    parser.add_argument("--data", default="./datasets/carla_vehicles/data.yaml", help="Dataset YAML")
    parser.add_argument("--epochs", type=int, default=100, help="Training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--device", default="cuda", help="Device (cuda/cpu)")
    parser.add_argument("--validate", help="Path to model to validate (skips training)")
    
    args = parser.parse_args()
    
    if args.validate:
        validate_model(args.validate, args.data, args.device)
    else:
        train_yolo(
            base_model=args.model,
            data_yaml=args.data,
            epochs=args.epochs,
            batch_size=args.batch,
            device=args.device
        )
