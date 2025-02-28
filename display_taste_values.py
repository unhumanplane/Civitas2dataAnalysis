import json
import pandas as pd
from tabulate import tabulate
from recipe_analyzer import RecipeAnalyzer

def main():
    """显示每个配方的口味数值"""
    # 加载测试结果
    print("\n加载测试结果数据...")
    try:
        with open('taste_happiness_results.json', 'r', encoding='utf-8') as f:
            results = json.load(f)
    except FileNotFoundError:
        print("未找到测试结果文件，请先运行测试")
        return
    
    if not results:
        print("测试结果为空")
        return
    
    analyzer = RecipeAnalyzer()
    
    # 创建数据表格
    data = []
    
    print("\n=== 配方口味数值分析 ===\n")
    
    # 按照测试组织结果，首先按口味类型分组
    taste_groups = {}
    for result in results:
        taste_type = result['taste_type']
        if taste_type not in taste_groups:
            taste_groups[taste_type] = []
        taste_groups[taste_type].append(result)
    
    # 处理每个口味组
    for taste_type, group_results in taste_groups.items():
        print(f"\n【{taste_type}口味组】")
        
        # 按食材分组
        ingredient_groups = {}
        for result in group_results:
            ing_id = result['ingredient_id']
            ing_name = result['ingredient_name']
            key = f"{ing_id}_{ing_name}"
            if key not in ingredient_groups:
                ingredient_groups[key] = []
            ingredient_groups[key].append(result)
        
        # 显示每个食材的不同用量结果
        for ing_key, ing_results in ingredient_groups.items():
            ing_id, ing_name = ing_key.split('_', 1)
            print(f"\n食材: {ing_name}")
            
            # 创建表格数据
            table_data = []
            for result in sorted(ing_results, key=lambda x: x['amount']):
                amount = result['amount']
                happiness = result['happiness']
                taste_values = result['taste_values']
                
                row = [
                    f"{amount}",
                    f"{happiness:.2f}",
                    f"{taste_values['acid']:.2f}",
                    f"{taste_values['sweet']:.2f}",
                    f"{taste_values['bitter']:.2f}",
                    f"{taste_values['spice']:.2f}",
                    f"{taste_values['salt']:.2f}"
                ]
                table_data.append(row)
            
            # 显示表格
            headers = ["用量", "幸福度", "酸", "甜", "苦", "辣", "咸"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            # 计算相关性
            if len(ing_results) > 1:
                amounts = [r['amount'] for r in ing_results]
                happiness_values = [r['happiness'] for r in ing_results]
                
                # 简单判断是否随着用量增加幸福度也增加
                increasing = all(happiness_values[i] <= happiness_values[i+1] for i in range(len(happiness_values)-1))
                decreasing = all(happiness_values[i] >= happiness_values[i+1] for i in range(len(happiness_values)-1))
                
                if increasing:
                    trend = "随着用量增加，幸福度上升"
                elif decreasing:
                    trend = "随着用量增加，幸福度下降"
                else:
                    trend = "幸福度与用量关系不明确"
                
                print(f"趋势: {trend}")
    
    # 创建整体对照表
    print("\n\n=== 所有配方口味数值对照表 ===\n")
    
    all_data = []
    for result in results:
        taste_type = result['taste_type']
        ing_name = result['ingredient_name']
        amount = result['amount']
        happiness = result['happiness']
        taste_values = result['taste_values']
        
        # 构建基础食材部分的描述
        base_parts = ["野菜(1.0)", "麦酒(1.0)"]  # 假设基础食材固定
        recipe_parts = base_parts + [f"{ing_name}({amount})"]
        recipe_desc = " + ".join(recipe_parts)
        
        row = [
            taste_type,
            ing_name,
            amount,
            happiness,
            taste_values['acid'],
            taste_values['sweet'],
            taste_values['bitter'],
            taste_values['spice'],
            taste_values['salt'],
            recipe_desc
        ]
        all_data.append(row)
    
    # 按幸福度排序
    all_data.sort(key=lambda x: x[3], reverse=True)
    
    # 创建DataFrame
    df = pd.DataFrame(all_data, columns=[
        "口味类型", "测试食材", "食材用量", "幸福度", 
        "酸值", "甜值", "苦值", "辣值", "咸值", "配方描述"
    ])
    
    # 显示DataFrame
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(df.to_string(index=False))
    
    # 分析最高幸福度配方的口味特点
    top_recipe = df.iloc[0]
    print(f"\n\n幸福度最高的配方: {top_recipe['配方描述']}")
    print(f"幸福度: {top_recipe['幸福度']:.2f}")
    print("\n口味特点:")
    tastes = {
        "酸值": top_recipe["酸值"],
        "甜值": top_recipe["甜值"],
        "苦值": top_recipe["苦值"],
        "辣值": top_recipe["辣值"],
        "咸值": top_recipe["咸值"]
    }
    for taste, value in sorted(tastes.items(), key=lambda x: x[1], reverse=True):
        print(f"- {taste}: {value:.2f}")


if __name__ == "__main__":
    main()
