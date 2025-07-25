import torch
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from PIL import Image
import numpy as np
import cv2
import os

class CrackDetector:
    def __init__(self, model_path="ml_models/model_final.pth"):
        self.cfg = get_cfg()
        self._setup_config(model_path)
        self.predictor = DefaultPredictor(self.cfg)
        
        # Setup metadata untuk visualisasi
        MetadataCatalog.get("crack_dataset").thing_classes = ["crack"]
    
    def _setup_config(self, model_path):
        """Setup configuration untuk model Detectron2"""
        self.cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"))
        self.cfg.MODEL.WEIGHTS = model_path
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # Hanya 1 kelas (retakan)
        self.cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    def predict(self, image_path, save_annotated=True, output_dir="static/uploads"):
        """
        Melakukan prediksi pada gambar dan menyimpan gambar dengan annotasi
        
        Args:
            image_path (str): Path ke gambar yang akan diprediksi
            save_annotated (bool): Apakah akan menyimpan gambar dengan annotasi
            output_dir (str): Directory untuk menyimpan gambar hasil annotasi
            
        Returns:
            dict: {
                'detected': bool,
                'num_detections': int,
                'predictions': list[dict],
                'annotated_image_path': str  # Path ke gambar dengan annotasi
            }
        """
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        outputs = self.predictor(img_rgb)
        instances = outputs["instances"]
        
        detections = []
        annotated_image_path = None
        
        if len(instances) > 0:
            boxes = instances.pred_boxes.tensor.cpu().numpy()
            scores = instances.scores.cpu().numpy()
            
            for box, score in zip(boxes, scores):
                detections.append({
                    'bbox': box.tolist(),
                    'score': float(score)
                })
        
        # Buat gambar dengan annotasi
        if save_annotated:
            v = Visualizer(img_rgb, MetadataCatalog.get("crack_dataset"), scale=1.0)
            v = v.draw_instance_predictions(instances.to("cpu"))
            
            # Simpan gambar hasil annotasi
            filename = os.path.basename(image_path)
            name, ext = os.path.splitext(filename)
            annotated_filename = f"{name}_annotated{ext}"
            annotated_path = os.path.join(output_dir, annotated_filename)
            
            # Convert dari RGB ke BGR untuk cv2
            annotated_img = cv2.cvtColor(v.get_image(), cv2.COLOR_RGB2BGR)
            cv2.imwrite(annotated_path, annotated_img)
            
            annotated_image_path = f"uploads/{annotated_filename}"
        
        return {
            'detected': len(instances) > 0,
            'num_detections': len(instances),
            'predictions': detections,
            'annotated_image_path': annotated_image_path
        }