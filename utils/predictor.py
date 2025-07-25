import torch
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo
from PIL import Image
import numpy as np

class CrackDetector:
    def __init__(self, model_path="ml_models/model_final.pth"):
        self.cfg = get_cfg()
        self._setup_config(model_path)
        self.predictor = DefaultPredictor(self.cfg)
    
    def _setup_config(self, model_path):
        """Setup configuration untuk model Detectron2"""
        self.cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"))
        self.cfg.MODEL.WEIGHTS = model_path
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # Hanya 1 kelas (retakan)
        self.cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    def predict(self, image_path):
        """
        Melakukan prediksi pada gambar
        
        Args:
            image_path (str): Path ke gambar yang akan diprediksi
            
        Returns:
            dict: {
                'detected': bool,
                'num_detections': int,
                'predictions': list[dict]  # Informasi deteksi
            }
        """
        img = Image.open(image_path)
        img_array = np.array(img)
        
        outputs = self.predictor(img_array)
        instances = outputs["instances"]
        
        detections = []
        if len(instances) > 0:
            boxes = instances.pred_boxes.tensor.cpu().numpy()
            scores = instances.scores.cpu().numpy()
            
            for box, score in zip(boxes, scores):
                detections.append({
                    'bbox': box.tolist(),
                    'score': float(score)
                })
        
        return {
            'detected': len(instances) > 0,
            'num_detections': len(instances),
            'predictions': detections
        }