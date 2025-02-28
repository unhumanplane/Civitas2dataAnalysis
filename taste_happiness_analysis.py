import os
import json
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from recipe_analyzer import RecipeAnalyzer
import pandas as pd
from scipy.stats import pearsonr
from tabulate import tabulate

# 配置matplotlib支持中文显示
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题

class TasteHappinessAnalyzer:
    """分析口味参数与幸福度之间的关系"""

    def __init__(self):
        self.analyzer = RecipeAnalyzer()
        self.data_dir = "taste_analysis_data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # 确保analyzer已经初始化
        if not self.analyzer.ingredient_list:
            self.analyzer.fetch_ingredient_list()
        if not self.analyzer.ingredient_prop:
            self.analyzer.fetch_ingredient_properties()
        
    def run_controlled_tests(self, base_ingredients, taste_to_test=None, max_ingredients=3):
        """运行控制变量测试
        
        Args:
            base_ingredients: 基础食材列表，格式为[(id, amount)]
            taste_to_test: 要测试的特定口味，如果为None则测试所有口味
            max_ingredients: 每种口味测试的最大食材数量
        """
        all_tastes = ['acid', 'sweet', 'bitter', 'spice', 'salt']
        tastes_to_test = [taste_to_test] if taste_to_test else all_tastes
        
        results = []
        
        print(f"\n开始测试口味与幸福度关系...\n")
        print(f"基础食材:")
        for ing_id, amount in base_ingredients:
            print(f"- {self.analyzer.get_ingredient_name(ing_id)}: {amount}")
        
        # 获取所有可用食材
        all_ingredients = self.analyzer.ingredient_list
        
        for taste in tastes_to_test:
            print(f"\n\n测试 {taste} 对幸福度的影响...")
            
            # 找出在目标口味上得分高的食材
            high_taste_ingredients = []
            for ingredient in all_ingredients:
                ing_id = ingredient['id']
                props = self.analyzer.ingredient_prop.get(str(ing_id), {}).get('1', {})
                taste_value = float(props.get(taste, 0))
                
                if taste_value > 0.5:  # 只选择在该口味上有明显特点的食材
                    high_taste_ingredients.append({
                        'id': ing_id,
                        'name': ingredient['name'],
                        'taste_value': taste_value
                    })
            
            # 按口味值排序
            high_taste_ingredients.sort(key=lambda x: x['taste_value'], reverse=True)
            
            # 选择口味值高的食材，但限制数量
            test_ingredients = high_taste_ingredients[:max_ingredients]
            
            if not test_ingredients:
                print(f"没有找到在 {taste} 口味上得分高的食材，跳过此口味测试")
                continue
            
            print(f"\n为 {taste} 口味测试选择了以下食材:")
            for ing in test_ingredients:
                print(f"- {ing['name']}: {taste}值 = {ing['taste_value']}")
            
            # 对每个测试食材进行不同用量的测试
            taste_test_results = []
            for test_ing in test_ingredients:
                ing_id = test_ing['id']
                print(f"\n测试食材 {test_ing['name']} 的不同用量...")
                
                # 测试不同用量
                for amount in [0.5, 1.0, 3.0]:  # 简化测试用量
                    test_combo = base_ingredients + [(ing_id, amount)]
                    results_table = self.analyzer.analyze_taste_combination(test_combo)
                    
                    if results_table:
                        last_row = results_table[-1]
                        happiness = float(last_row[1])
                        efficiency = float(last_row[5])
                        
                        # 计算当前组合的总口味值
                        total_tastes = {'acid': 0, 'sweet': 0, 'bitter': 0, 'spice': 0, 'salt': 0}
                        for test_ing_id, test_amount in test_combo:
                            ing_props = self.analyzer.ingredient_prop.get(str(test_ing_id), {}).get('1', {})
                            for t in total_tastes:
                                total_tastes[t] += float(ing_props.get(t, 0)) * test_amount
                        
                        test_result = {
                            'taste_type': taste,
                            'ingredient_id': ing_id,
                            'ingredient_name': test_ing['name'],
                            'amount': amount,
                            'happiness': happiness,
                            'efficiency': efficiency,
                            'taste_values': total_tastes
                        }
                        taste_test_results.append(test_result)
                        
                        print(f"  用量 {amount}: 幸福度 = {happiness:.2f}, 效率 = {efficiency:.2f}, {taste}值 = {total_tastes[taste]:.2f}")
            
            results.extend(taste_test_results)
        
        # 保存测试结果
        timestamp = self.analyzer.get_timestamp()
        filename = f"{self.data_dir}/taste_happiness_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试结果已保存到 {filename}")
        return results
    
    def analyze_correlation(self, results=None):
        """分析口味值与幸福度的相关性
        
        Args:
            results: 测试结果，如果为None则加载最新的结果文件
        """
        if results is None:
            # 加载最新的测试结果
            files = sorted([f for f in os.listdir(self.data_dir) if f.startswith('taste_happiness_')])
            if not files:
                print("没有找到测试结果文件")
                return
            
            latest_file = os.path.join(self.data_dir, files[-1])
            with open(latest_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
        
        if not results:
            print("没有足够的测试数据进行分析")
            return
        
        print("\n\n分析口味与幸福度的相关性...\n")
        
        # 准备数据进行相关性分析
        df = pd.DataFrame(results)
        
        # 将嵌套的taste_values字典转换为单独的列
        taste_df = pd.json_normalize(df['taste_values'])
        analysis_df = pd.concat([df.drop('taste_values', axis=1), taste_df], axis=1)
        
        # 分析每种口味与幸福度的相关性
        correlations = []
        all_tastes = ['acid', 'sweet', 'bitter', 'spice', 'salt']
        
        for taste in all_tastes:
            # 计算皮尔逊相关系数
            corr, p_value = pearsonr(analysis_df[taste], analysis_df['happiness'])
            correlations.append({
                'taste': taste,
                'correlation': corr,
                'p_value': p_value,
                'significance': '显著' if p_value < 0.05 else '不显著'
            })
        
        # 打印相关性结果
        corr_df = pd.DataFrame(correlations)
        print(tabulate(corr_df, headers='keys', tablefmt='grid', showindex=False))
        
        # 创建相关性图表
        plt.figure(figsize=(10, 6))
        bars = plt.bar(corr_df['taste'], corr_df['correlation'], color=['blue' if x < 0.05 else 'lightblue' for x in corr_df['p_value']])
        
        # 添加标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.2f}', ha='center', va='bottom')
        
        plt.axhline(y=0, color='r', linestyle='-', alpha=0.3)
        plt.xlabel('口味')
        plt.ylabel('与幸福度的相关系数')
        plt.title('各种口味与幸福度的相关性分析')
        
        # 保存图表
        plot_file = f"{self.data_dir}/taste_correlation_plot_{self.analyzer.get_timestamp()}.png"
        plt.savefig(plot_file)
        plt.close()
        
        print(f"\n相关性分析图表已保存到 {plot_file}")
        
        return correlations
    
    def analyze_taste_impact(self, results=None):
        """分析不同用量下口味对幸福度的影响曲线
        
        Args:
            results: 测试结果，如果为None则加载最新的结果文件
        """
        if results is None:
            # 加载最新的测试结果
            files = sorted([f for f in os.listdir(self.data_dir) if f.startswith('taste_happiness_')])
            if not files:
                print("没有找到测试结果文件")
                return
            
            latest_file = os.path.join(self.data_dir, files[-1])
            with open(latest_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
        
        if not results:
            print("没有足够的测试数据进行分析")
            return
        
        print("\n\n分析不同口味值对幸福度的影响曲线...\n")
        
        # 将数据转换为DataFrame
        df = pd.DataFrame(results)
        
        # 将嵌套的taste_values字典转换为单独的列
        taste_df = pd.json_normalize(df['taste_values'])
        analysis_df = pd.concat([df.drop('taste_values', axis=1), taste_df], axis=1)
        
        # 按口味类型分组
        taste_types = analysis_df['taste_type'].unique()
        
        plt.figure(figsize=(15, 10))
        
        for i, taste in enumerate(taste_types, 1):
            taste_data = analysis_df[analysis_df['taste_type'] == taste]
            
            plt.subplot(len(taste_types), 1, i)
            
            # 按口味值大小排序
            taste_data = taste_data.sort_values(by=taste)
            
            plt.scatter(taste_data[taste], taste_data['happiness'], alpha=0.7)
            
            # 添加趋势线
            z = np.polyfit(taste_data[taste], taste_data['happiness'], 1)
            p = np.poly1d(z)
            plt.plot(taste_data[taste], p(taste_data[taste]), "r--", alpha=0.7)
            
            plt.title(f'{taste}值与幸福度关系')
            plt.xlabel(f'{taste}值')
            plt.ylabel('幸福度')
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        plot_file = f"{self.data_dir}/taste_impact_curves_{self.analyzer.get_timestamp()}.png"
        plt.savefig(plot_file)
        plt.close()
        
        print(f"\n口味影响曲线图表已保存到 {plot_file}")
        
        return True


def main():
    """主函数"""
    print("\n=== 开始测试口味与幸福度的关系 ===\n")
    
    analyzer = TasteHappinessAnalyzer()
    
    # 使用基础食材进行测试
    # 可以根据需要调整基础食材
    base_ingredients = [(18, 1.0), (19, 1.0)]  # 示例：使用ID为18和19的食材作为基础
    
    print("\n使用以下基础食材:")
    for ing_id, amount in base_ingredients:
        print(f"- {analyzer.analyzer.get_ingredient_name(ing_id)}: {amount}")
    
    # 运行测试
    results = analyzer.run_controlled_tests(base_ingredients, max_ingredients=2)
    
    # 分析相关性
    if results:
        analyzer.analyze_correlation(results)
    
    # 分析口味影响曲线
    if results:
        analyzer.analyze_taste_impact(results)
    
    print("\n=== 测试完成 ===\n")


if __name__ == "__main__":
    main()
