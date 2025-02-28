import requests
import json
import time
import urllib3
from tabulate import tabulate
import os
import math

# 禁用不安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RecipeAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.base_url = "https://api.civitas2.top"
        
        # 设置代理
        self.session.proxies = {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }
        
        # 设置完整的headers
        self.session.headers.update({
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'api.civitas2.top',
            'Origin': 'https://civitas2.top',
            'Referer': 'https://civitas2.top/',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
        })
        
        # 设置cookies
        self.session.cookies.update({
            'Hm_lvt_0c4ee6b640823273fd178db09bbb3397': '1740490881',
            'sessionid': 'vtxnxtv7txz9j5a76hxazjcalq2skbo0',
            'Hm_lpvt_0c4ee6b640823273fd178db09bbb3397': '1740490881'
        })
        
        # 创建数据存储目录
        self.data_dir = "recipe_analysis_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 获取食材列表
        print("\n获取食材列表...")
        response = self.session.get(f"{self.base_url}/get_diet_material/")
        data = response.json()
        
        # 保存原始数据用于调试（带时间戳）
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f'raw_ingredients_{timestamp}.json'
        with open(os.path.join(self.data_dir, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已保存原始数据到 {filename}")
        
        # 打印原始JSON到控制台
        print("\n=== 原始JSON数据 ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        if response.status_code == 200 and data.get('status') == 1:
            # 从原始数据直接生成表格
            raw_datalist = data['data']['datalist']
            raw_datadict = data['data']['datadict']
            
            table_data = []
            for item in raw_datalist:
                item_id = str(item['id'])
                props = raw_datadict.get(item_id, {}).get('1', {})  # 1代表生食属性
                
                table_data.append([
                    item['id'],
                    item['name'],
                    props.get('type_of', '未知'),
                    f"{float(props.get('stamina', 0)):.2f}",
                    f"{float(props.get('health', 0)):.2f}",
                    f"{float(props.get('starvation', 0)):.2f}",
                    f"{float(props.get('acid', 0)):.2f}",
                    f"{float(props.get('sweet', 0)):.2f}",
                    f"{float(props.get('bitter', 0)):.2f}",
                    f"{float(props.get('spice', 0)):.2f}",
                    f"{float(props.get('salt', 0)):.2f}",
                    f"{props.get('min_count', 0.1):.2f}",
                    f"{props.get('max_count', 5.0):.2f}"
                ])
            
            headers = ["ID", "名称", "类型", "精力", "健康", "饥饿", 
                      "酸", "甜", "苦", "辣", "咸", "最小", "最大"]
            print("\n=== 重构食材表格 ===")
            print(tabulate(table_data, headers=headers, tablefmt="simple_grid", numalign="right"))
            
            self.ingredient_list = data['data']['datalist']
            self.ingredient_prop = data['data']['datadict']
            
            # 初始化后自动执行验证
            self.validate_ingredient_data()
        else:
            self.ingredient_list = []
            self.ingredient_prop = {}

    def get_timestamp(self):
        """获取当前时间戳，格式为年月日-时分秒"""
        return time.strftime("%Y%m%d-%H%M%S", time.localtime())

    def validate_ingredient_data(self):
        """验证原始食材数据与表格数据的匹配性"""
        try:
            with open('raw_ingredients.json', 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            raw_ingredients = raw_data['data']['datalist']
            raw_properties = raw_data['data']['datadict']

            # 生成验证表格
            validation_errors = []
            for item in raw_ingredients:
                item_id = item['id']
                
                # 检查ID是否存在属性字典
                if str(item_id) not in raw_properties:
                    validation_errors.append([item_id, item['name'], '缺失属性数据'])
                    continue

                # 检查基础属性完整性
                props = raw_properties[str(item_id)].get('1', {})
                required_fields = ['stamina', 'health', 'starvation']
                for field in required_fields:
                    if field not in props:
                        validation_errors.append([item_id, item['name'], f'缺失{field}字段'])

            # 打印验证结果
            print("\n=== 数据验证结果 ===")
            if validation_errors:
                print(tabulate(
                    validation_errors,
                    headers=['ID', '名称', '问题'],
                    tablefmt='simple',
                    numalign='right'
                ))
            else:
                print("所有数据匹配成功，未发现异常")

        except Exception as e:
            print(f"数据验证失败: {str(e)}")

    def analyze_efficiency(self, combo_results, total_amount):
        """分析配方效率（值/用量比）"""
        if not combo_results:
            return 0, 0, 0
        
        happiness_ratio = combo_results['happiness'] / total_amount if total_amount > 0 else 0
        health_ratio = combo_results['health'] / total_amount if total_amount > 0 else 0
        stamina_ratio = combo_results['stamina'] / total_amount if total_amount > 0 else 0
        
        return happiness_ratio, health_ratio, stamina_ratio

    def analyze_taste_combination(self, ingredients):
        """测试食材组合的效果"""
        materials = []
        ingredient_names = []
        total_amount = 0
        
        # 过滤掉用量为0的食材
        valid_ingredients = [(ing_id, amount) for ing_id, amount in ingredients if amount > 0]
        if not valid_ingredients:
            return None  # 如果没有有效食材，直接返回
        
        for ingredient_id, amount in valid_ingredients:
            total_amount += amount
            ingredient_name = next((item['name'] for item in self.ingredient_list if item['id'] == ingredient_id), '未知')
            materials.append({"id": ingredient_id, "number": amount, "quality": 1})
            ingredient_names.append(f"{ingredient_name}({amount})")
        
        print(f"\n配方: {' + '.join(ingredient_names)}")
        
        # 创建表格数据
        table_data = []
        best_result = {
            'method': '',
            'happiness': 0,
            'health': 0,
            'stamina': 0,
            'efficiency': 0
        }
        
        for treatment, method in [(1, "凉拌"), (2, "水煮"), (3, "油炸")]:
            data = {
                "materials": json.dumps(materials),
                "treatment": treatment
            }
            
            response = self.session.post(f"{self.base_url}/recipe_prediction_new/", data=data)
            
            try:
                response_data = response.json()
                if response_data["status"] == 1:
                    results = response_data["data"]
                    
                    # 计算效率
                    happiness_ratio = results['happiness']/total_amount
                    health_ratio = results['health']/total_amount
                    stamina_ratio = results['stamina']/total_amount
                    total_efficiency = happiness_ratio + health_ratio + stamina_ratio
                    
                    # 更新最佳结果
                    if total_efficiency > best_result['efficiency']:
                        best_result = {
                            'method': method,
                            'happiness': results['happiness'],
                            'health': results['health'],
                            'stamina': results['stamina'],
                            'efficiency': total_efficiency
                        }
                    
                    # 提取口味信息
                    flavor = results.get('taste', '未知')
                    
                    # 添加到表格数据
                    table_data.append([
                        method,
                        f"{results['happiness']:.2f}",
                        f"{results['health']:.2f}",
                        f"{results['stamina']:.2f}",
                        f"{results['starvation']:.2f}",
                        f"{happiness_ratio:.2f}",
                        f"{health_ratio:.2f}",
                        f"{stamina_ratio:.2f}",
                        flavor
                    ])
                else:
                    print(f"请求失败: {response_data.get('msg', '未知错误')}")
            except Exception as e:
                print(f"处理响应时出错: {str(e)}")
        
        # 打印表格
        headers = ["烹饪方式", "幸福度", "健康", "精力", "饱食度", 
                  "幸福效率", "健康效率", "精力效率", "口味"]
        print("\n=== 烹饪效果分析 ===")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # 打印最佳结果
        print(f"\n最佳烹饪方式: {best_result['method']}")
        print(f"总效率: {best_result['efficiency']:.2f}")
        
        return table_data

    def save_analysis_results(self, analysis_type, data, base_ingredients=None):
        """保存分析结果到文件
        
        Args:
            analysis_type: 分析类型，如'combination', 'trend', 'contribution'
            data: 要保存的数据
            base_ingredients: 基础食材列表（可选）
        """
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        # 准备元数据
        metadata = {
            'timestamp': timestamp,
            'analysis_type': analysis_type,
            'base_ingredients': []
        }
        
        if base_ingredients:
            for ing_id, amount in base_ingredients:
                ing_name = self.get_ingredient_name(ing_id)
                metadata['base_ingredients'].append({
                    'id': ing_id,
                    'name': ing_name,
                    'amount': amount
                })
        
        # 组合完整数据
        full_data = {
            'metadata': metadata,
            'results': data
        }
        
        # 生成文件名
        if base_ingredients:
            ingredients_str = '_'.join([f"{ing_id}" for ing_id, _ in base_ingredients])
            filename = f"{analysis_type}_{ingredients_str}_{timestamp}.json"
        else:
            filename = f"{analysis_type}_{timestamp}.json"
        
        # 保存到文件
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n分析结果已保存到: {filename}")
        return filepath

    def analyze_ingredient_combinations(self, base_ingredients, step=0.5):
        """遍历不同食材搭配的效果分析
        
        Args:
            base_ingredients: 基础食材列表，格式为[(id, amount)]
            step: 遍历步长，默认0.5（仅用于小于等于1的用量）
        """
        best_combo = {
            'ingredients': None,
            'method': '',
            'happiness': 0,
            'health': 0,
            'stamina': 0,
            'efficiency': 0,
            'taste_balance': 0
        }
        
        # 记录所有尝试过的组合结果
        all_combinations = []
        
        # 为每个食材创建数量范围
        ranges = {}
        print("\n计算食材用量范围...")
        for ing_id, amount in base_ingredients:
            props = self.ingredient_prop.get(str(ing_id), {}).get('1', {})
            min_count = float(props.get('min_count', 0.1))
            max_count = float(props.get('max_count', 5.0))
            
            # 确保范围是合适步长的整数倍
            if min_count <= 1:
                min_count = round(min_count / step) * step
            else:
                min_count = round(min_count / 2) * 2
                if min_count < 1:  # 如果四舍五入后小于1，则设为1
                    min_count = 1
            
            if max_count <= 1:
                max_count = round(max_count / step) * step
            else:
                max_count = round(max_count / 2) * 2
            
            ranges[ing_id] = (min_count, max_count)
            print(f"食材 {self.get_ingredient_name(ing_id)}: {min_count} - {max_count}")
        
        # 生成用量列表的函数
        def generate_amounts(min_val, max_val):
            amounts = []
            # 处理小于等于1的部分
            if min_val <= 1:
                amounts.extend([round(x * step, 1) for x in range(int(min_val/step), min(int(1/step) + 1, int(max_val/step) + 1))])
            
            # 处理大于1的部分
            if max_val > 1:
                # 从1开始，用2作为间隔生成奇数：1,3,5...
                start = 1
                for amount in range(start, int(max_val) + 1, 2):
                    if amount >= min_val:
                        amounts.append(amount)
            
            return sorted(set(amounts))  # 去重并排序
        
        # 计算总组合数
        total_combinations = 1
        for ing_id, _ in base_ingredients:
            min_count, max_count = ranges[ing_id]
            amounts = generate_amounts(min_count, max_count)
            total_combinations *= len(amounts)
        
        print(f"\n预计需要尝试 {total_combinations} 种组合...")
        
        def calculate_taste_balance(ingredients):
            """计算口味平衡度"""
            # 将0用量改为0.1
            adjusted_ingredients = [(ing_id, 0.1 if amount == 0 else amount) for ing_id, amount in ingredients]
            
            total_tastes = {'acid': 0, 'sweet': 0, 'bitter': 0, 'spice': 0, 'salt': 0}
            for ing_id, amount in adjusted_ingredients:
                props = self.ingredient_prop.get(str(ing_id), {}).get('1', {})
                for taste in total_tastes:
                    total_tastes[taste] += float(props.get(taste, 0)) * amount
            
            # 计算口味的标准差（值越小表示越平衡）
            values = list(total_tastes.values())
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            return 1 / (1 + (variance ** 0.5))  # 转换为0-1之间的值，越大越平衡
        
        def try_combinations(current_combo, remaining_ingredients):
            if not remaining_ingredients:
                # 将0用量改为0.1
                adjusted_combo = [(ing_id, 0.1 if amount == 0 else amount) for ing_id, amount in current_combo]
                
                taste_balance = calculate_taste_balance(adjusted_combo)
                results = self.analyze_taste_combination(adjusted_combo)
                
                if results:
                    last_row = results[-1]
                    combo_result = {
                        'ingredients': [{
                            'id': ing_id,
                            'name': self.get_ingredient_name(ing_id),
                            'amount': amount
                        } for ing_id, amount in adjusted_combo],
                        'method': last_row[0],
                        'happiness': float(last_row[1]),
                        'health': float(last_row[2]),
                        'stamina': float(last_row[3]),
                        'starvation': float(last_row[4]),
                        'taste_balance': taste_balance,
                        'efficiency_ratios': {
                            'happiness': float(last_row[5]),
                            'health': float(last_row[6]),
                            'stamina': float(last_row[7])
                        },
                        'taste': last_row[8]
                    }
                    all_combinations.append(combo_result)
                    
                    total_efficiency = sum(float(x) for x in last_row[5:8])
                    combined_score = total_efficiency * (1 + taste_balance * 0.5)
                    
                    if combined_score > best_combo['efficiency']:
                        best_combo.update({
                            'ingredients': adjusted_combo,
                            'method': last_row[0],
                            'happiness': float(last_row[1]),
                            'health': float(last_row[2]),
                            'stamina': float(last_row[3]),
                            'efficiency': combined_score,
                            'taste_balance': taste_balance
                        })
                        # 打印当前最佳组合
                        print("\n发现新的最佳组合:")
                        for ing_id, amount in adjusted_combo:
                            print(f"{self.get_ingredient_name(ing_id)}: {amount}")
                        print(f"效率: {combined_score:.2f}")
                return
            
            ing_id, _ = remaining_ingredients[0]
            min_amount, max_amount = ranges[ing_id]
            
            # 使用新的用量生成函数
            for amount in generate_amounts(min_amount, max_amount):
                new_combo = current_combo + [(ing_id, amount)]
                try_combinations(new_combo, remaining_ingredients[1:])
        
        try_combinations([], base_ingredients)
        
        # 保存分析结果
        analysis_data = {
            'best_combination': best_combo,
            'all_combinations': all_combinations,
            'parameters': {
                'step': step
            }
        }
        self.save_analysis_results('combination', analysis_data, base_ingredients)
        
        # 打印最佳组合结果
        print("\n=== 最佳食材组合 ===")
        for ing_id, amount in best_combo['ingredients']:
            ing_name = next((item['name'] for item in self.ingredient_list if item['id'] == ing_id), '未知')
            print(f"{ing_name}: {amount}")
        print(f"烹饪方式: {best_combo['method']}")
        print(f"幸福度: {best_combo['happiness']:.2f}")
        print(f"健康: {best_combo['health']:.2f}")
        print(f"精力: {best_combo['stamina']:.2f}")
        print(f"口味平衡度: {best_combo['taste_balance']:.2f}")
        print(f"综合评分: {best_combo['efficiency']:.2f}")
        
        return best_combo

    def analyze_taste_trends(self, base_ingredients, target_attribute, step=0.5):
        """分析某个属性随食材用量变化的趋势
        
        Args:
            base_ingredients: 基础食材列表，格式为[(id, amount)]
            target_attribute: 目标属性，如'happiness', 'health', 'stamina'
            step: 遍历步长，默认0.5
        """
        trends = {}
        
        for ing_id, _ in base_ingredients:
            ing_name = next((item['name'] for item in self.ingredient_list if item['id'] == ing_id), '未知')
            props = self.ingredient_prop.get(str(ing_id), {}).get('1', {})
            min_count = float(props.get('min_count', 0.1))  # 最小值改为0.1
            max_count = float(props.get('max_count', 5.0))
            
            # 记录不同用量下的属性值
            amounts = []
            values = []
            
            # 固定其他食材用量为1.0，只变化当前食材
            for amount in [round(x * step, 1) for x in range(int(min_count/step), int(max_count/step) + 1)]:
                test_ingredients = []
                for test_id, base_amount in base_ingredients:
                    if test_id == ing_id:
                        test_ingredients.append((test_id, amount))
                    else:
                        test_ingredients.append((test_id, base_amount))
                
                results = self.analyze_taste_combination(test_ingredients)
                if results:
                    last_row = results[-1]
                    if target_attribute == 'happiness':
                        value = float(last_row[1])
                    elif target_attribute == 'health':
                        value = float(last_row[2])
                    elif target_attribute == 'stamina':
                        value = float(last_row[3])
                    
                    amounts.append(amount)
                    values.append(value)
            
            trends[ing_name] = {
                'amounts': amounts,
                'values': values
            }
        
        # 保存趋势分析结果
        analysis_data = {
            'target_attribute': target_attribute,
            'trends': trends,
            'parameters': {
                'step': step
            }
        }
        self.save_analysis_results('trend', analysis_data, base_ingredients)
        
        # 打印趋势分析结果
        print(f"\n=== {target_attribute}随食材用量变化趋势 ===")
        for ing_name, data in trends.items():
            print(f"\n{ing_name}:")
            print("用量\t属性值")
            for amount, value in zip(data['amounts'], data['values']):
                print(f"{amount:.1f}\t{value:.2f}")
        
        return trends

    def get_ingredient_name(self, ingredient_id: int) -> str:
        """获取食材名称"""
        for ingredient in self.ingredient_list:
            if ingredient['id'] == ingredient_id:
                return ingredient['name']
        return "未知"

def main():
    analyzer = RecipeAnalyzer()
    
    combinations = [
        # 测试不同用量的野菜
        [(18, 0.1)],                # 1. 野菜0.1
        [(18, 0.3)],                # 2. 野菜0.3
        [(18, 0.5)],                # 3. 野菜0.5
        [(18, 1.0)],                # 4. 野菜1.0
        [(18, 3.0)],                # 5. 野菜3.0
        [(18, 5.0)],                # 6. 野菜5.0
    ]
    
    print("\n=== 测试野菜性价比 ===")
    for i, combo in enumerate(combinations, 1):
        print(f"\n{'='*40}")
        print(f"配方 {i}")
        analyzer.analyze_taste_combination([(ing_id, 0.1 if amount == 0 else amount) for ing_id, amount in combo])

    # 测试食材组合
    base_ingredients = [(18, 1.0), (19, 1.0)]
    analyzer.analyze_ingredient_combinations(base_ingredients)

    # 示例：分析多个食材组合
    test_combinations = [
        [(18, 1.0), (19, 1.0)],  # 组合1
        [(18, 1.0), (20, 1.0)],  # 组合2
        [(19, 1.0), (20, 1.0)]   # 组合3
    ]
    
    results = []
    for i, combo in enumerate(test_combinations, 1):
        print(f"\n分析组合 {i}")
        result = analyzer.analyze_ingredient_combinations(combo)
        analyzer.analyze_taste_trends(combo, 'happiness')
        results.append(result)
    
    # 保存所有组合的比较结果
    comparison_data = {
        'combinations': test_combinations,
        'results': results
    }
    analyzer.save_analysis_results('comparison', comparison_data)

if __name__ == "__main__":
    main()
