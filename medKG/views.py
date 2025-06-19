from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from py2neo import Graph, Node
from fuzzywuzzy import fuzz
import jieba.posseg as pseg
import json

graph = Graph("bolt://localhost:7687", auth=("neo4j", "123"))

def login_view(request):
    return render(request, 'login.html')

def main(request):
    return render(request, 'main.html')

def regist(request):
    return render(request, 'register.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not username or not password:
            return JsonResponse({'status': 'error', 'message': '用户名或密码不能为空'})
        node = Node("User", username=username, password=password)
        graph.create(node)
    return render(request, 'login.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        cypher = 'MATCH (n:User) WHERE n.username = $username AND n.password = $password RETURN n'
        result = graph.run(cypher, parameters={'username': username, 'password': password})
        if result.data():
            return redirect('main')
        else:
            return JsonResponse({'status': 'error', 'message': '用户名或密码错误'})
    return render(request, 'login.html')

def question(request):
    return render(request, 'search_form.html')

def kngraph(request):
    return render(request, 'kngraph.html')


# 问答

def AssignFoodIntension(text):
    patterns = {
        'query_ingredients_by_dish': ['xx都有哪些原材料', 'xx包含什么', 'xx的原料'],
        'query_dishes_by_ingredient': ['xx能做什么菜', '包含xx的菜', '用xx做什么'],
        'query_nutrition_by_dish': ['xx营养指数多少', 'xx减肥指数', 'xx养颜指数'],
        'query_nutrition_by_ingredient': ['xx含有什么营养', 'xx的营养成分'],
        'query_high_slim_dishes': ['减肥效果好的菜', '适合减肥的菜', '减肥指数高'],
        'query_high_nutrition_dishes': ['蛋白质高的菜', '营养指数高']
    }

    if len(text.strip()) <= 4:
        return 'query_ingredients_by_dish'

    scores = {
        key: max(fuzz.partial_ratio(text, s.replace('xx', '')) for s in samples)
        for key, samples in patterns.items()
    }
    return max(scores, key=scores.get)

def extract_entity(text):
    words = pseg.cut(text)
    for word, flag in words:
        if flag in ['n', 'nz']:
            return word
    return ''


def SearchGraph(entity, intent):
    if intent == 'query_ingredients_by_dish':
        cypher = f'''
            MATCH (d:菜品 {{名称: "{entity}"}})-[:包含]->(i:食材)
            RETURN i.名称 AS 食材
        '''
        result = graph.run(cypher).data()
        if result:
            items = "、".join([r['食材'] for r in result])
            return f"{entity} 的原材料包括：{items}"
        else:
            return f"{entity} 暂无原材料信息"

    elif intent == 'query_dishes_by_ingredient':
        cypher = f'''
            MATCH (d:菜品)-[:包含]->(i:食材 {{名称: "{entity}"}})
            RETURN d.名称 AS 菜品
        '''
        result = graph.run(cypher).data()
        if result:
            items = "、".join([r['菜品'] for r in result])
            return f"含有 {entity} 的菜有：{items}"
        else:
            return f"未找到含有 {entity} 的菜品"

    elif intent == 'query_nutrition_by_dish':
        cypher = f'''
            MATCH (d:菜品 {{名称: "{entity}"}})
            RETURN d.营养指数 AS 营养, d.减肥指数 AS 减肥, d.养颜指数 AS 养颜
        '''
        result = graph.run(cypher).data()
        if result and result[0]['营养'] is not None:
            r = result[0]
            return f"{entity} 的营养指数为 {r['营养']}，减肥指数为 {r['减肥']}，养颜指数为 {r['养颜']}"
        else:
            return f"{entity} 暂无指数信息"

    elif intent == 'query_nutrition_by_ingredient':
        cypher = f'''
            MATCH (i:食材 {{名称: "{entity}"}})-[r:含有营养素]->(n:营养素)
            RETURN n.类型 AS 营养素, r.数值 AS 数值
        '''
        result = graph.run(cypher).data()
        if result:
            items = "、".join([f"{r['营养素']}({r['数值']})" for r in result])
            return f"{entity} 含有营养成分：{items}"
        else:
            return f"{entity} 暂无营养信息"

    elif intent == 'query_high_slim_dishes':
        cypher = '''
            MATCH (d:菜品)-[r:减肥指数]->(:指数)
            RETURN d.名称 AS 菜品, r.值 AS 指数 ORDER BY r.值 DESC LIMIT 5
        '''
        result = graph.run(cypher).data()
        return "推荐减肥菜品：" + "、".join([f"{r['菜品']}({r['指数']})" for r in result])

    elif intent == 'query_high_nutrition_dishes':
        cypher = '''
            MATCH (d:菜品)-[r:营养指数]->(:指数)
            RETURN d.名称 AS 菜品, r.值 AS 指数 ORDER BY r.值 DESC LIMIT 5
        '''
        result = graph.run(cypher).data()
        return "营养指数高的菜品：" + "、".join([f"{r['菜品']}({r['指数']})" for r in result])

    else:
        return "暂不支持该问题类型"


def intelligentCommunicationSystem(queryText):
    intent = AssignFoodIntension(queryText)
    entity = extract_entity(queryText)

    if not entity and 'high' not in intent:
        return "请说明具体菜品或食材名称"

    result = SearchGraph(entity, intent)
    return result


@csrf_exempt
def qa_api(request):
    if request.method == 'POST':
        try:
            query = json.loads(request.body)['query']
        except:
            query = request.POST.get('query', '')
        answer = intelligentCommunicationSystem(query)
        return JsonResponse({'answer': answer})
    else:
        return JsonResponse({'error': '仅支持POST请求'})


def get_suggestions_from_knowledge_graph(query):
    if query.strip() == '' or len(query.strip()) < 2:
        return []

    cypher_dish = f'''
        MATCH (d:菜品)
        WHERE d.名称 CONTAINS "{query}"
        RETURN d.名称 AS name LIMIT 10
    '''
    cypher_ingredient = f'''
        MATCH (i:食材)
        WHERE i.名称 CONTAINS "{query}"
        RETURN i.名称 AS name LIMIT 10
    '''

    dish_result = graph.run(cypher_dish).data()
    ing_result = graph.run(cypher_ingredient).data()

    return list({r['name'] for r in (dish_result + ing_result)})


def suggestions_api(request):
    query = request.GET.get('query', '')
    suggestions = get_suggestions_from_knowledge_graph(query)
    return JsonResponse(suggestions, safe=False)
