from django.http import JsonResponse
from api.models import Herb
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json

def add_cors_headers(response):
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
    response["Access-Control-Max-Age"] = "1728000"
    return response

@csrf_exempt
def search_by_category(request):
    if request.method == "OPTIONS":
        response = JsonResponse({})
        return add_cors_headers(response)

    try:
        if request.method == "POST":
            data = json.loads(request.body)
            category_type = data.get('type', '')
            sub_category = data.get('subCategory', '')
            print(f"Received category type: {category_type}, sub category: {sub_category}")
            
            if not category_type or not sub_category:
                response = JsonResponse({
                    'success': False,
                    'error': 'Category information not provided',
                    'data': []
                }, status=200)
                return add_cors_headers(response)

            # 根据不同分类类型进行查询
            if category_type == 'taste':
                # 按性味查询
                results = list(Herb.objects.filter(
                    taste__icontains=sub_category
                ).values(
                    'name', 'alias', 'taste', 'meridian', 'effect',
                    'indication', 'usage', 'contraindication'
                ).order_by('name'))
                
            elif category_type == 'meridian':
                # 按归经查询
                results = list(Herb.objects.filter(
                    meridian__icontains=sub_category
                ).values(
                    'name', 'alias', 'taste', 'meridian', 'effect',
                    'indication', 'usage', 'contraindication'
                ).order_by('name'))
            else:
                results = []

            print(f"Found {len(results)} results for {category_type} - {sub_category}")
            
            response = JsonResponse({
                'success': True,
                'data': results,
                'category_type': category_type,
                'sub_category': sub_category,
                'count': len(results)
            }, status=200)
            return add_cors_headers(response)

    except Exception as e:
        print(f"Category search error: {str(e)}")
        response = JsonResponse({
            'success': False,
            'error': str(e),
            'data': []
        }, status=200)
        return add_cors_headers(response) 