FOOD KNOWLEDGE GRAPH

数据目录 data/
包含构建图谱用的节点表、边表、食材词表等；

build_graph.py
构建知识图谱，读取 CSV 文件，连接 Neo4j，构建食材、菜品、营养素节点及其之间的关系。

views.py
包含问答接口 /api/qa/、模糊匹配 /api/suggestions/、用户登录、图谱查询等逻辑。

templates/
与 Django 配套使用的 HTML 页面，配合路由和视图完成前端展示。

运行：
先运行build_graph.py构建知识图谱
终端python manage.py runserver
http://127.0.0.1:8000/main 进入页面

