from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
import logging
import traceback
import sys
import torch
from .model_utils import HerbRecognizer

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # 确保日志输出到控制台
)
logger = logging.getLogger(__name__)

# 初始化模型识别器
MODEL_PATH = os.path.join(settings.BASE_DIR, 'recognition', 'models', '完整模型_ResNet50模型_epoch_13.pth')
CLASS_NAMES_PATH = os.path.join(settings.BASE_DIR, 'recognition', 'class_names.json')

logger.debug(f"Model path: {MODEL_PATH}")
logger.debug(f"Class names path: {CLASS_NAMES_PATH}")

# 检查文件是否存在
if not os.path.exists(MODEL_PATH):
    logger.error(f"Model file not found at path: {MODEL_PATH}")
    logger.error(f"Current working directory: {os.getcwd()}")
    logger.error(f"Directory contents: {os.listdir(os.path.dirname(MODEL_PATH))}")
if not os.path.exists(CLASS_NAMES_PATH):
    logger.error(f"Class names file not found at path: {CLASS_NAMES_PATH}")
    logger.error(f"Current working directory: {os.getcwd()}")
    logger.error(f"Directory contents: {os.listdir(os.path.dirname(CLASS_NAMES_PATH))}")

# 尝试加载模型
try:
    logger.debug("Attempting to initialize HerbRecognizer")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"PyTorch version: {torch.__version__}")
    logger.debug(f"CUDA available: {torch.cuda.is_available()}")
    
    recognizer = HerbRecognizer(MODEL_PATH, CLASS_NAMES_PATH)
    logger.info("模型识别器初始化成功")
except Exception as e:
    logger.error(f"模型识别器初始化失败: {str(e)}")
    logger.error("初始化失败时的完整堆栈跟踪:")
    logger.error(traceback.format_exc())
    logger.error(f"Exception type: {type(e)}")
    logger.error(f"Exception args: {e.args}")
    recognizer = None

@api_view(['GET'])
def get_model_info(request):
    """获取模型信息"""
    try:
        if recognizer is None:
            return Response({
                'success': False,
                'error': '模型未正确加载'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        info = HerbRecognizer.get_model_info(MODEL_PATH)
        if info:
            return Response({
                'success': True,
                'data': info
            })
        else:
            return Response({
                'success': False,
                'error': '无法获取模型信息'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f'获取模型信息时出错: {str(e)}')
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def upload_image(request):
    """处理图片上传和识别请求"""
    try:
        # 检查模型是否正确加载
        if recognizer is None:
            logger.error("模型未正确加载，无法处理请求")
            return Response({
                'success': False,
                'error': '模型未正确加载，请检查服务器日志'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # 获取上传的图片
        image_file = request.FILES.get('file')
        if not image_file:
            logger.error("未收到图片文件")
            return Response({
                'success': False,
                'error': '未收到图片文件'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.debug(f"收到图片文件: {image_file.name}, 大小: {image_file.size} bytes")
        
        # 验证文件类型
        if not image_file.content_type in ['image/jpeg', 'image/png']:
            logger.error(f"不支持的文件类型: {image_file.content_type}")
            return Response({
                'success': False,
                'error': '仅支持JPG/PNG格式图片'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证文件大小（5MB）
        if image_file.size > 5 * 1024 * 1024:
            logger.error(f"文件大小超过限制: {image_file.size} bytes")
            return Response({
                'success': False,
                'error': '图片大小不能超过5MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 进行预测
        logger.debug("开始进行图片识别")
        results = recognizer.predict(image_file)
        if results is None:
            logger.error("识别过程返回空结果")
            return Response({
                'success': False,
                'error': '识别过程出错'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.debug(f"识别成功，返回 {len(results)} 个结果")
        return Response({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"处理图片上传时出错: {str(e)}")
        logger.error("错误堆栈跟踪:")
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 