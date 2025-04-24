import torch
import torchvision.transforms as transforms
from PIL import Image
import json
import os
import logging
from pathlib import Path
import torchvision.models as models
import traceback
import sys
import torch.nn as nn

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # 确保日志输出到控制台
)
logger = logging.getLogger(__name__)

class HerbRecognizer:
    def __init__(self, model_path, class_names_path):
        """
        初始化识别器
        Args:
            model_path: 模型文件路径
            class_names_path: 类别名称映射文件路径
        """
        logger.debug(f"Initializing HerbRecognizer with model_path: {model_path}")
        logger.debug(f"Initializing HerbRecognizer with class_names_path: {class_names_path}")
        logger.debug(f"Python version: {sys.version}")
        logger.debug(f"PyTorch version: {torch.__version__}")
        logger.debug(f"CUDA available: {torch.cuda.is_available()}")
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f'Using device: {self.device}')
        
        # 检查文件是否存在
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at path: {model_path}")
            logger.error(f"Current working directory: {os.getcwd()}")
            logger.error(f"Directory contents: {os.listdir(os.path.dirname(model_path))}")
            raise FileNotFoundError(f'Model file not found: {model_path}')
        if not os.path.exists(class_names_path):
            logger.error(f"Class names file not found at path: {class_names_path}")
            logger.error(f"Current working directory: {os.getcwd()}")
            logger.error(f"Directory contents: {os.listdir(os.path.dirname(class_names_path))}")
            raise FileNotFoundError(f'Class names file not found: {class_names_path}')
        
        try:
            # 加载类别名称映射
            logger.debug('Loading class names...')
            with open(class_names_path, 'r', encoding='utf-8') as f:
                self.class_names = json.load(f)
            logger.debug(f"Loaded {len(self.class_names)} class names")
            
            # 加载完整模型
            logger.debug('Loading complete model...')
            logger.debug(f"Model file size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
            
            try:
                # 加载完整检查点
                checkpoint = torch.load(model_path, map_location=self.device)
                
                # 获取模型
                self.model = checkpoint['model']
                self.model = self.model.to(self.device)
                self.model.eval()
                
                # 保存其他训练状态（如果需要）
                self.optimizer_state = checkpoint.get('optimizer_state_dict')
                self.scheduler_state = checkpoint.get('scheduler_state_dict')
                self.best_val_acc = checkpoint.get('best_val_acc')
                
                logger.debug("Complete model loaded successfully")
                logger.debug("Model set to eval mode")
                
            except Exception as e:
                logger.error(f"Error loading complete model: {str(e)}")
                logger.error(f"Exception type: {type(e)}")
                logger.error(f"Exception args: {e.args}")
                logger.error("Model loading traceback:")
                logger.error(traceback.format_exc())
                raise
            
            logger.info(f'Model loaded successfully with {len(self.class_names)} classes')
            
        except Exception as e:
            logger.error(f'Error in HerbRecognizer initialization: {str(e)}')
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception args: {e.args}")
            logger.error("Full traceback:")
            logger.error(traceback.format_exc())
            raise
        
        # 定义图像预处理
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        logger.debug("Image transforms initialized")
    
    def predict(self, image_file, top_k=5):
        """
        对输入图片进行预测
        Args:
            image_file: 图片文件对象或路径
            top_k: 返回前k个预测结果
        Returns:
            list: 包含dict的列表，每个dict包含name和similarity
        """
        try:
            # 打开并预处理图片
            if isinstance(image_file, str):
                image = Image.open(image_file)
            else:
                image = Image.open(image_file.file)
            
            # 确保图片是RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 转换为tensor并添加batch维度
            image_tensor = self.transform(image).unsqueeze(0)
            image_tensor = image_tensor.to(self.device)
            
            # 进行预测
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
            
            # 获取top-k结果
            top_prob, top_indices = torch.topk(probabilities, min(top_k, len(self.class_names)))
            
            # 构建结果列表
            results = []
            for prob, idx in zip(top_prob[0], top_indices[0]):
                class_idx = str(idx.item())
                if class_idx in self.class_names:
                    results.append({
                        'name': self.class_names[class_idx],
                        'similarity': float(prob)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f'Error during prediction: {str(e)}')
            return None
    
    @staticmethod
    def get_model_info(model_path):
        """
        获取模型信息
        Args:
            model_path: 模型文件路径
        Returns:
            dict: 包含模型信息的字典
        """
        try:
            checkpoint = torch.load(model_path, map_location='cpu')
            model = checkpoint['model']
            info = {
                'architecture': model.__class__.__name__,
                'file_size': Path(model_path).stat().st_size / (1024 * 1024),  # MB
                'num_parameters': sum(p.numel() for p in model.parameters()),
                'device': 'cuda' if torch.cuda.is_available() else 'cpu',
                'best_val_acc': checkpoint.get('best_val_acc', 'N/A')
            }
            return info
        except Exception as e:
            logger.error(f'Error getting model info: {str(e)}')
            return None 