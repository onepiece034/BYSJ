import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class DeepSeekClient:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_API_BASE_URL.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        logger.info(f"Initialized DeepSeekClient with base URL: {self.base_url}")

    def _make_request(self, method, endpoint, data=None):
        """统一的请求处理方法"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"准备发送请求到: {url}")
        logger.info(f"请求方法: {method}")
        logger.info(f"请求头: {headers}")
        if data:
            logger.info(f"请求数据: {data}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data
            )
            
            logger.info(f"收到响应 - 状态码: {response.status_code}")
            logger.info(f"响应头: {dict(response.headers)}")
            
            if response.status_code != 200:
                error_msg = f"API请求失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            logger.info(f"响应数据: {response_data}")
            return response_data
            
        except requests.exceptions.RequestException as e:
            error_msg = f"请求异常: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - 响应: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def chat(self, messages, model='deepseek-chat', temperature=0.7, max_tokens=2000, frequency_penalty=0, presence_penalty=0, top_p=1):
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            top_p: 采样概率阈值
            
        Returns:
            API响应
        """
        logger.info(f"开始聊天请求 - 使用模型: {model}")
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "top_p": top_p
        }
        
        # 如果是 deepseek-reasoner 模型,添加特殊参数
        if model == 'deepseek-reasoner':
            logger.info("使用 deepseek-reasoner 模型,添加特殊参数")
            data.update({
                "stream": False,
                "reasoning": True
            })
        
        logger.info(f"发送聊天请求数据: {data}")
        
        try:
            response = self._make_request('POST', '/v1/chat/completions', data)
            logger.info(f"收到聊天响应: {response}")
            
            # 检查是否包含推理链内容
            if model == 'deepseek-reasoner':
                if 'reasoning_content' in response:
                    logger.info("找到推理链内容")
                else:
                    logger.warning("未找到推理链内容")
            
            return response
            
        except Exception as e:
            logger.error(f"聊天请求失败: {str(e)}")
            raise

    def list_models(self):
        """
        获取可用的模型列表
        """
        return self._make_request('GET', '/models')

    def get_balance(self):
        """
        查询账户余额
        """
        try:
            logger.info("开始请求余额信息")
            response = self._make_request('GET', '/user/balance')
            logger.info(f"收到余额响应: {response}")
            
            # 检查响应格式
            if not isinstance(response, dict):
                logger.error(f"余额响应格式错误: {type(response)}")
                return {
                    'balance_infos': [{
                        'currency': 'CNY',
                        'total_balance': '0.00',
                        'granted_balance': '0.00',
                        'topped_up_balance': '0.00'
                    }]
                }
            
            # 检查响应中是否包含balance_infos字段
            if 'balance_infos' not in response:
                logger.error(f"余额响应中缺少balance_infos字段: {response}")
                return {
                    'balance_infos': [{
                        'currency': 'CNY',
                        'total_balance': '0.00',
                        'granted_balance': '0.00',
                        'topped_up_balance': '0.00'
                    }]
                }
            
            return response
        except Exception as e:
            logger.error(f"获取余额失败: {str(e)}")
            return {
                'balance_infos': [{
                    'currency': 'CNY',
                    'total_balance': '0.00',
                    'granted_balance': '0.00',
                    'topped_up_balance': '0.00'
                }]
            } 