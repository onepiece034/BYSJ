import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ChatMessage
from .deepseek_client import DeepSeekClient
from django.conf import settings

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """
    处理聊天请求
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        messages = data.get('messages', [])
        if not messages:
            return JsonResponse({
                'status': 'error',
                'message': '消息不能为空'
            }, status=400)

        # 获取聊天参数
        model = data.get('model', 'deepseek-chat')
        temperature = float(data.get('temperature', 1.0))
        max_tokens = int(data.get('max_tokens', 2048))
        frequency_penalty = float(data.get('frequency_penalty', 0))
        presence_penalty = float(data.get('presence_penalty', 0))
        top_p = float(data.get('top_p', 1))

        # 验证和清理消息序列
        cleaned_messages = []
        last_role = None
        for msg in messages:
            current_role = msg.get('role')
            if current_role == last_role:
                # 如果角色相同，合并消息内容
                if cleaned_messages:
                    cleaned_messages[-1]['content'] += '\n' + msg.get('content', '')
                continue
            cleaned_messages.append(msg)
            last_role = current_role

        if not cleaned_messages:
            return JsonResponse({
                'status': 'error',
                'message': '无效的消息序列'
            }, status=400)

        # 初始化客户端
        client = DeepSeekClient()
        
        # 发送请求到DeepSeek API
        try:
            response = client.chat(
                messages=cleaned_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                top_p=top_p
            )
            
            # 检查响应格式
            if not isinstance(response, dict):
                raise ValueError("Invalid response format from API")
                
            choices = response.get('choices', [])
            if not choices:
                raise ValueError("No choices in API response")
                
            assistant_message = choices[0].get('message', {})
            if not assistant_message:
                raise ValueError("No message in API response")
                
            content = assistant_message.get('content', '')
            if not content:
                raise ValueError("Empty content in API response")

            # 获取思维链内容（如果存在）
            reasoning_content = assistant_message.get('reasoning_content', '')
            logger.info(f"模型: {model}, 思维链内容: {reasoning_content[:100] if reasoning_content else '无'}")
            
            # 保存消息到数据库
            try:
                ChatMessage.objects.create(
                    role='user',
                    content=cleaned_messages[-1]['content'],
                    model_type=model
                )
                ChatMessage.objects.create(
                    role='assistant',
                    content=content,
                    reasoning_content=reasoning_content if model == 'deepseek-reasoner' else None,
                    model_type=model
                )
                logger.info(f"消息已保存到数据库，模型类型: {model}, 思维链内容: {reasoning_content[:100] if reasoning_content else '无'}")
            except Exception as e:
                logger.error(f"Failed to save messages to database: {str(e)}")
                # 继续执行，不影响返回响应

            # 返回前端期望的格式
            response_data = {
                'choices': [{
                    'message': {
                        'content': content
                    }
                }]
            }
            
            # 如果是deepseek-reasoner模型，添加思维链内容
            if model == 'deepseek-reasoner' and reasoning_content:
                response_data['choices'][0]['message']['reasoning_content'] = reasoning_content
                logger.info(f"返回给前端的数据包含思维链内容: {reasoning_content[:100]}...")
            else:
                logger.info("返回给前端的数据不包含思维链内容")
                
            return JsonResponse(response_data)

        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'API请求失败: {str(e)}'
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': '无效的JSON格式'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def chat_history(request):
    """
    获取聊天历史记录
    """
    try:
        messages = ChatMessage.objects.all().order_by('created_at')
        return JsonResponse({
            'status': 'success',
            'data': [{
                'role': msg.role,
                'content': msg.content,
                'reasoning_content': msg.reasoning_content,
                'created_at': msg.created_at.isoformat()
            } for msg in messages]
        })
    except Exception as e:
        logger.error(f"Failed to get chat history: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'获取聊天历史失败: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def list_models(request):
    """
    获取可用的模型列表
    """
    try:
        client = DeepSeekClient()
        response = client.list_models()
        
        if not isinstance(response, dict):
            raise ValueError("Invalid response format from API")
            
        models = response.get('data', [])
        if not models:
            raise ValueError("No models in API response")
            
        return JsonResponse({
            'status': 'success',
            'data': models
        })
        
    except Exception as e:
        logger.error(f"Failed to get models: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'获取模型列表失败: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def get_balance(request):
    """
    查询账户余额
    """
    try:
        logger.info("开始获取余额")
        client = DeepSeekClient()
        response = client.get_balance()
        
        logger.info(f"DeepSeek API 原始响应: {response}")
        
        if not isinstance(response, dict):
            logger.error(f"API响应格式错误: {type(response)}")
            raise ValueError("Invalid response format from API")
            
        # 检查响应中是否包含balance_infos字段
        if 'balance_infos' not in response:
            logger.error(f"API响应中缺少balance_infos字段: {response}")
            # 返回一个默认的余额信息，而不是抛出错误
            return JsonResponse({
                'balance_infos': [{
                    'currency': 'CNY',
                    'total_balance': '0.00',
                    'granted_balance': '0.00',
                    'topped_up_balance': '0.00'
                }]
            })
            
        balance_infos = response.get('balance_infos', [])
        logger.info(f"解析出的余额信息: {balance_infos}")
        
        if not balance_infos:
            logger.warning("未找到余额信息，返回默认值")
            # 返回一个默认的余额信息，而不是抛出错误
            return JsonResponse({
                'balance_infos': [{
                    'currency': 'CNY',
                    'total_balance': '0.00',
                    'granted_balance': '0.00',
                    'topped_up_balance': '0.00'
                }]
            })
            
        # 返回前端期望的格式
        response_data = {
            'balance_infos': balance_infos
        }
        logger.info(f"返回给前端的数据: {response_data}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"获取余额失败: {str(e)}")
        # 返回一个默认的余额信息，而不是抛出错误
        return JsonResponse({
            'balance_infos': [{
                'currency': 'CNY',
                'total_balance': '0.00',
                'granted_balance': '0.00',
                'topped_up_balance': '0.00'
            }]
        }) 