import json
from tabulate import tabulate

def main():
    """以简洁表格形式显示配方的口味数值"""
    print("\n加载测试结果数据...")
    try:
        with open('taste_happiness_results.json', 'r', encoding='utf-8') as f:
            results = json.load(f)
    except FileNotFoundError:
        print("未找到测试结果文件")
        return
    
    if not results:
        print("测试结果为空")
        return
    
    # 对结果按幸福度排序
    results.sort(key=lambda x: x['happiness'], reverse=True)
    
    # 准备表格数据
    table_data = []
    for result in results:
        taste_type = result['taste_type']
        ing_name = result['ingredient_name']
        amount = result['amount']
        happiness = result['happiness']
        tastes = result['taste_values']
        
        # 构建配方描述
        recipe = f"野菜(1) + 麦酒(1) + {ing_name}({amount})"
        
        row = [
            recipe,
            f"{happiness:.2f}",
            f"{tastes['acid']:.1f}",
            f"{tastes['sweet']:.1f}",
            f"{tastes['bitter']:.1f}",
            f"{tastes['spice']:.1f}",
            f"{tastes['salt']:.1f}",
            taste_type
        ]
        table_data.append(row)
    
    # 显示表格
    headers = ["配方", "幸福度", "酸", "甜", "苦", "辣", "咸", "特征口味"]
    print("\n所有配方的口味数值（按幸福度降序排列）:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # 分析口味特征
    avg_tastes = {"acid": 0, "sweet": 0, "bitter": 0, "spice": 0, "salt": 0}
    top_tastes = {"acid": 0, "sweet": 0, "bitter": 0, "spice": 0, "salt": 0}
    
    # 计算平均口味值和前3个配方的口味值
    for i, result in enumerate(results):
        tastes = result['taste_values']
        for taste in avg_tastes:
            avg_tastes[taste] += tastes[taste] / len(results)
            if i < 3:  # 前3个配方
                top_tastes[taste] += tastes[taste] / 3
    
    # 显示高幸福度配方的口味特征
    print("\n高幸福度配方的口味特征（前3个配方平均值）:")
    for taste, value in sorted(top_tastes.items(), key=lambda x: x[1], reverse=True):
        avg = avg_tastes[taste]
        diff = ((value - avg) / avg * 100) if avg > 0 else 0
        status = "高" if value > avg else "低" if value < avg else "中"
        
        print(f"{taste}味: {value:.1f} ({status}, 与平均值相差 {abs(diff):.1f}%)")

if __name__ == "__main__":
    main()
