import json
import pandas as pd

def main():
    """显示配方口味数值表"""
    # 读取测试结果
    try:
        with open('taste_happiness_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("未找到测试结果文件")
        return
    
    # 提取需要的数据
    rows = []
    for item in data:
        row = {
            '测试食材': item['ingredient_name'],
            '用量': item['amount'],
            '幸福度': item['happiness'],
            '酸': item['taste_values']['acid'],
            '甜': item['taste_values']['sweet'],
            '苦': item['taste_values']['bitter'],
            '辣': item['taste_values']['spice'],
            '咸': item['taste_values']['salt'],
            '口味特征': item['taste_type']
        }
        rows.append(row)
    
    # 创建DataFrame
    df = pd.DataFrame(rows)
    
    # 按幸福度排序
    df = df.sort_values('幸福度', ascending=False)
    
    # 格式化输出
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    
    print("\n配方口味数值表（按幸福度降序排列）：")
    print(df)
    
    # 输出前五个最高幸福度配方
    print("\n\n前五个最高幸福度配方：")
    top5 = df.head(5)
    for idx, row in top5.iterrows():
        print(f"\n配方：野菜(1.0) + 麦酒(1.0) + {row['测试食材']}({row['用量']})")
        print(f"幸福度：{row['幸福度']:.2f}")
        print(f"口味成分：酸({row['酸']:.1f}) 甜({row['甜']:.1f}) 苦({row['苦']:.1f}) 辣({row['辣']:.1f}) 咸({row['咸']:.1f})")

if __name__ == "__main__":
    main()
