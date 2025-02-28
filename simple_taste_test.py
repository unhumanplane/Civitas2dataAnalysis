from recipe_analyzer import RecipeAnalyzer
import json
import os

def main():
    """测试幸福度和口味参数关系的简化版本"""
    analyzer = RecipeAnalyzer()
    
    # 确保有食材数据
    if not analyzer.ingredient_list:
        print("需要重新加载食材数据...")
    
    print("\n=== 测试口味参数对幸福度的影响 ===")
    
    # 基础食材
    base_ingredients = [(18, 1.0), (19, 1.0)]
    base_names = [analyzer.get_ingredient_name(ing_id) for ing_id, _ in base_ingredients]
    print(f"基础食材: {', '.join(base_names)}")
    
    # 测试结果数据结构
    results = []
    
    # 食材用量测试范围
    test_amounts = [0.5, 1.0, 3.0]
    
    # 找出各种口味特征明显的食材
    taste_representatives = {
        'acid': [],
        'sweet': [],
        'bitter': [],
        'spice': [],
        'salt': []
    }
    
    # 查找每种口味特征明显的食材（最多2个）
    for taste in taste_representatives:
        print(f"\n寻找 {taste} 特征明显的食材...")
        
        taste_foods = []
        for ingredient in analyzer.ingredient_list:
            ing_id = ingredient['id']
            props = analyzer.ingredient_prop.get(str(ing_id), {}).get('1', {})
            taste_value = float(props.get(taste, 0))
            
            if taste_value > 0.5:
                taste_foods.append((ing_id, ingredient['name'], taste_value))
        
        # 按口味值排序
        taste_foods.sort(key=lambda x: x[2], reverse=True)
        
        # 选取前2个
        for i, (ing_id, name, value) in enumerate(taste_foods[:2]):
            print(f"- {name}: {value}")
            taste_representatives[taste].append(ing_id)
    
    # 对每种口味的代表食材进行测试
    print("\n\n=== 开始测试各口味食材与幸福度的关系 ===")
    
    for taste, ing_ids in taste_representatives.items():
        if not ing_ids:
            print(f"\n没有找到 {taste} 口味特征明显的食材，跳过")
            continue
            
        print(f"\n测试 {taste} 口味...")
        
        for ing_id in ing_ids:
            ing_name = analyzer.get_ingredient_name(ing_id)
            print(f"\n  测试食材: {ing_name}")
            
            # 测试不同用量
            for amount in test_amounts:
                test_combo = base_ingredients + [(ing_id, amount)]
                combo_str = ", ".join([f"{analyzer.get_ingredient_name(id)}({amt})" for id, amt in test_combo])
                
                print(f"\n    配方: {combo_str}")
                results_table = analyzer.analyze_taste_combination(test_combo)
                
                # 记录结果
                if results_table:
                    last_row = results_table[-1]
                    happiness = float(last_row[1])
                    
                    # 计算当前组合的总口味值
                    total_tastes = {'acid': 0, 'sweet': 0, 'bitter': 0, 'spice': 0, 'salt': 0}
                    for test_ing_id, test_amount in test_combo:
                        ing_props = analyzer.ingredient_prop.get(str(test_ing_id), {}).get('1', {})
                        for t in total_tastes:
                            total_tastes[t] += float(ing_props.get(t, 0)) * test_amount
                    
                    results.append({
                        'taste_type': taste,
                        'ingredient_id': ing_id,
                        'ingredient_name': ing_name,
                        'amount': amount,
                        'happiness': happiness,
                        'taste_values': total_tastes
                    })
    
    # 分析结果
    print("\n\n=== 分析结果 ===")
    
    # 按口味类型分组并分析
    taste_correlations = {}
    
    for taste in taste_representatives:
        taste_data = [r for r in results if r['taste_type'] == taste]
        if not taste_data:
            continue
            
        # 计算口味值和幸福度的关系
        taste_values = [d['taste_values'][taste] for d in taste_data]
        happiness_values = [d['happiness'] for d in taste_data]
        
        # 简单计算相关性（值越大代表关系越明显）
        if len(taste_values) > 1 and len(set(taste_values)) > 1:
            # 简单计算：是否随着口味值增加，幸福度也增加
            positive_relation = sum(1 for i in range(len(taste_values)-1) 
                                  if (taste_values[i+1] > taste_values[i] and 
                                      happiness_values[i+1] > happiness_values[i]))
            relation_strength = positive_relation / (len(taste_values)-1)
            taste_correlations[taste] = relation_strength
    
    # 输出结果
    print("\n口味与幸福度的关系强度 (0-1，值越高表示正相关越强):")
    for taste, strength in sorted(taste_correlations.items(), key=lambda x: x[1], reverse=True):
        print(f"{taste}: {strength:.2f}")
    
    # 总结
    print("\n总结：")
    if taste_correlations:
        best_taste = max(taste_correlations.items(), key=lambda x: x[1])[0]
        print(f"- {best_taste} 口味与幸福度的正相关关系最强")
        print(f"- 要提高幸福度，可以适当增加食谱中的 {best_taste} 口味")
    else:
        print("- 没有足够的数据得出明确结论")
    
    # 保存结果
    with open('taste_happiness_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n详细结果已保存到 taste_happiness_results.json")


if __name__ == "__main__":
    main()
