from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.db import connection
from .models import Herb
import json
import traceback
import logging

logger = logging.getLogger(__name__)

class HerbSearchView(APIView):
    def post(self, request):
        try:
            keyword = request.data.get('keyword', '')
            print(f"收到搜索请求，关键词: {keyword}")

            if not keyword:
                print("关键词为空，返回空结果")
                return Response({'error': '请输入搜索关键词'}, status=status.HTTP_400_BAD_REQUEST)

            # 构建查询条件
            query = Q()
            
            # 1. 先查找药名匹配的
            name_query = Q(name__icontains=keyword)
            name_results = Herb.objects.filter(name_query)
            print(f"1. 药名匹配结果数: {name_results.count()}")
            for herb in name_results:
                print(f"药名匹配: {herb.name}")
            
            # 2. 再查找别名匹配的（排除已经在药名中匹配的）
            alias_query = Q(alias__icontains=keyword)
            alias_results = Herb.objects.filter(alias_query).exclude(name__in=name_results.values_list('name', flat=True))
            print(f"2. 别名匹配结果数: {alias_results.count()}")
            for herb in alias_results:
                print(f"别名匹配: {herb.name} (别名: {herb.alias})")

            # 3. 最后查找其他字段匹配的（排除已经匹配的）
            other_query = (
                Q(effect__icontains=keyword) |
                Q(indication__icontains=keyword) |
                Q(effect_class__icontains=keyword) |
                Q(taste__icontains=keyword) |
                Q(meridian__icontains=keyword)
            )
            excluded_names = list(name_results.values_list('name', flat=True)) + list(alias_results.values_list('name', flat=True))
            other_results = Herb.objects.filter(other_query).exclude(name__in=excluded_names)
            print(f"3. 其他字段匹配结果数: {other_results.count()}")
            for herb in other_results:
                print(f"其他匹配: {herb.name}")

            # 合并所有结果
            all_results = list(name_results) + list(alias_results) + list(other_results)
            print(f"4. 总匹配结果数: {len(all_results)}")

            # 转换为字典列表
            herbs_list = []
            for herb in all_results:
                herb_dict = {
                    'name': herb.name,
                    'alias': herb.alias,
                    'taste': herb.taste,
                    'meridian': herb.meridian,
                    'effect': herb.effect,
                    'indication': herb.indication,
                    'usage': herb.usage,
                    'contraindication': herb.contraindication,
                    'source': herb.source,
                    'collection': herb.collection,
                    'effect_class': herb.effect_class,
                    'pharmacology': herb.pharmacology,
                    'chemistry': herb.chemistry,
                    'prescription': herb.prescription,
                    'theory': herb.theory,
                    'research': herb.research,
                    'taxonomy': herb.taxonomy,
                    'distribution': herb.distribution,
                    'morphology': herb.morphology,
                    'identification': herb.identification,
                    'cultivation': herb.cultivation,
                    'environment': herb.environment
                }
                herbs_list.append(herb_dict)

            if not herbs_list:
                print("\n未找到匹配结果")
                return Response({'error': '未找到相关中药信息'}, status=status.HTTP_404_NOT_FOUND)

            # 返回所匹配的结果
            response_data = {
                'success': True,
                'data': herbs_list,
                'count': len(herbs_list)
            }
            print(f"5. 返回数据条数: {len(herbs_list)}")
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            print(f"错误详情: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HerbSuggestView(APIView):
    def post(self, request):
        try:
            keyword = request.data.get('keyword', '')
            print(f"\n{'='*50}")
            print(f"搜索建议请求")
            print(f"关键词: {keyword}")
            print(f"{'='*50}")

            if not keyword:
                return Response({'success': True, 'data': []})

            # 直接使用一个查询获取所有匹配的记录
            query = Q(name__icontains=keyword) | Q(alias__icontains=keyword) | Q(effect_class__icontains=keyword)
            herbs = Herb.objects.filter(query).order_by('name')

            # 记录 SQL 查询
            print(f"\nSQL查询: {herbs.query}")
            
            # 获取并记录所有匹配的记录
            herbs_list = list(herbs)  # 执行查询
            print(f"\n查询到的记录数: {len(herbs_list)}")
            
            # 记录每条记录的详细信息
            print("\n匹配的记录:")
            for herb in herbs_list:
                print(f"  - 药名: {herb.name}")
                print(f"    别名: {herb.alias}")
                print(f"    功效分类: {herb.effect_class}")

            # 转换为响应格式
            suggestions = []
            for herb in herbs_list:
                suggestion = {
                    'name': herb.name,
                    'alias': herb.alias if herb.alias else '',
                    'effect_class': herb.effect_class if herb.effect_class else '',
                    'effect': herb.effect[:100] + '...' if herb.effect and len(herb.effect) > 100 else herb.effect,
                    'taste': herb.taste if herb.taste else '',
                    'meridian': herb.meridian if herb.meridian else ''
                }
                suggestions.append(suggestion)

            # 记录最终结果
            print(f"\n最终返回结果数: {len(suggestions)}")
            
            # 记录所有执行的SQL查询
            for query in connection.queries:
                print(f"\n执行的SQL: {query['sql']}")
                print(f"耗时: {query['time']}秒")

            response_data = {
                'success': True,
                'data': suggestions,
                'total_count': len(suggestions),
                'sql_query': str(herbs.query)
            }

            print(f"\n响应数据:")
            print(f"总数: {response_data['total_count']}")
            print(f"SQL: {response_data['sql_query']}")
            print(f"{'='*50}\n")

            return Response(response_data)

        except Exception as e:
            print(f"\n搜索建议发生错误: {str(e)}")
            print(f"错误详情: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 