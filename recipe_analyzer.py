import requests
import json
import time
import urllib3
from tabulate import tabulate

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
        
        # 获取食材列表
        print("\n获取食材列表...")
        response = self.session.get(f"{self.base_url}/get_diet_material/")
        data = response.json()
        
        # 保存原始数据用于调试（带时间戳）
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f'raw_ingredients_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
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
        
        for ingredient_id, amount in ingredients:
            total_amount += amount
            ingredient_name = next((item['name'] for item in self.ingredient_list if item['id'] == ingredient_id), '未知')
            materials.append({"id": ingredient_id, "number": amount, "quality": 1})
            ingredient_names.append(f"{ingredient_name}({amount})")
        
        print(f"\n配方: {' + '.join(ingredient_names)}")
        
        # 创建表格数据
        table_data = []
        
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
                    # 打印完整的返回数据结构，用于调试
                    print(f"API返回数据: {json.dumps(results, ensure_ascii=False, indent=2)}")
                    
                    # 提取或默认为空的口味信息
                    flavor = results.get('taste', '未知')
                    
                    # 添加到表格数据
                    table_data.append([
                        method,
                        f"{results['happiness']:.2f}",
                        f"{results['health']:.2f}",
                        f"{results['stamina']:.2f}",
                        f"{results['starvation']:.2f}",
                        f"{results['happiness']/total_amount:.2f}",
                        f"{results['health']/total_amount:.2f}",
                        f"{results['stamina']/total_amount:.2f}",
                        flavor
                    ])
                    
                    # 保留原来的输出
                    print(f"\n【{method}】")
                    print(f"属性: 幸福感={results['happiness']:.2f}, 健康值={results['health']:.2f}, 精力值={results['stamina']:.2f}, 饥饿度={results['starvation']:.2f}")
                    print(f"性价比: 幸福感={results['happiness']/total_amount:.2f}, 健康值={results['health']/total_amount:.2f}, 精力值={results['stamina']/total_amount:.2f}")
                    print(f"口味: {flavor}")
            except Exception as e:
                print(f"处理响应时出错: {e}")
        
        # 打印表格
        if table_data:
            headers = ["烹饪方式", "幸福感", "健康值", "精力值", "饥饿度", "幸福感/量", "健康值/量", "精力值/量", "口味"]
            print("\n=== 烹饪方式比较 ===")
            print(tabulate(table_data, headers=headers, tablefmt="grid", numalign="right"))

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
        analyzer.analyze_taste_combination(combo)

if __name__ == "__main__":
    main()
