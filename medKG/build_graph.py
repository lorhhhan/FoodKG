from py2neo import Graph, Node, Relationship
import pandas as pd

graph = Graph("bolt://localhost:7687", auth=("neo4j", "123"))
graph.run("MATCH (n) DETACH DELETE n")  # 清空数据库

# 读取数据
dish_df = pd.read_csv("data\kg_dish_nodes.csv")
# dish_df = pd.read_csv("data\kg_dish_nodes.csv", encoding='gbk')
ingredient_df = pd.read_csv("data\kg_ingredient_nodes.csv")
nutrition_df = pd.read_csv("data\kg_nutrition_nodes.csv")
# nutrition_df = pd.read_csv("data\kg_nutrition_nodes.csv", encoding='gbk')
edge_df = pd.read_csv("data\kg_dish_ingredient_edges.csv")

# 菜品节点
dish_nodes = {}
for _, row in dish_df.iterrows():
    node = Node("菜品", 名称=row["dish"])

    # 新增热量属性
    if "calories" in row and pd.notna(row["calories"]):
        node["热量"] = row["calories"]

    graph.create(node)
    dish_nodes[row["dish"]] = node

# 食材节点
ingredient_nodes = {}
for _, row in ingredient_df.iterrows():
    node = Node("食材", 名称=row["ingredient"])
    graph.create(node)
    ingredient_nodes[row["ingredient"]] = node

# 营养素节点及关系
for _, row in nutrition_df.iterrows():
    ing_name = row["ingredient"]
    ing_node = ingredient_nodes.get(ing_name)
    if not ing_node:
        continue
    for nutrient in ["calorie", "protein", "carbohydrate", "fat"]:
        value = row.get(nutrient)
        if pd.notna(value):
            nut_node = Node("营养素",
                            类型={"calorie": "热量", "protein": "蛋白质", "carbohydrate": "碳水化合物", "fat": "脂肪"}[
                                nutrient])
            graph.merge(nut_node, "营养素", "类型")
            rel = Relationship(ing_node, "含有营养素", nut_node, 数值=value)
            graph.create(rel)

# 菜品-食材关系
for _, row in edge_df.iterrows():
    dish = dish_nodes.get(row["dish"])
    ing = ingredient_nodes.get(row["ingredient"])
    if dish and ing:
        graph.create(Relationship(dish, "包含", ing))

# 指数节点
index_types = {
    "减肥指数": "slim_index",
    "营养指数": "nutrition_index",
    "养颜指数": "beauty_index",
    "热量": "calories"
}
for index_label in index_types.keys():
    graph.merge(Node("指数", 名称=index_label), "指数", "名称")

# 菜品-指数关系
for _, row in dish_df.iterrows():
    dish_node = dish_nodes.get(row["dish"])
    for label, col in index_types.items():
        index_node = graph.nodes.match("指数", 名称=label).first()
        val = row[col]
        if pd.notna(val):
            rel = Relationship(dish_node, label, index_node, 值=val)
            graph.create(rel)
# 输出成功信息
print("数据导入完成")