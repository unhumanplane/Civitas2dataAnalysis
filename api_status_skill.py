import requests
import urllib3

# 禁用不安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ApiStatusSkill:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.base_url = "https://api.civitas2.top"
        self.username = None
        
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
        
        # 获取用户名
        self.get_user_name()
        
    def get_user_name(self):
        """获取用户名信息"""
        print("\n获取用户信息...")
        response = self.session.get(f"{self.base_url}/get_user_estate_list/")
        data = response.json()
        
        # 检查响应状态
        if response.status_code == 200 and data.get('status') == 1:
            user_data = data.get('data', {})
            if 'username' in user_data:
                self.username = user_data['username']
                print(f"用户名: {self.username}")
            else:
                print("未能获取用户名")
        else:
            print(f"获取用户信息失败: {data.get('message', '未知错误')}")
    
    def get_status(self):
        """获取状态信息"""
        print("\n获取状态信息...")
        response = self.session.get(f"{self.base_url}/get_status/")
        data = response.json()
        
        # 检查响应状态
        if response.status_code == 200 and data.get('status') == 1:
            status_data = data.get('data', {})
            
            # 处理今天的状态数据
            if 'today' in status_data:
                today_data = status_data['today']
                
                print("\n=== 今日状态 ===")
                if self.username:
                    print(f"用户名: {self.username}")
                
                print(f"精力: {today_data.get('stamina', 0)}")
                print(f"健康: {today_data.get('health', 0)}")
                print(f"快乐: {today_data.get('happiness', 0)}")
                print(f"饥饿度: {today_data.get('starvation', 0)}")
            
            # 处理明天的变化数据
            if 'tomorrow' in status_data:
                tomorrow_data = status_data['tomorrow']
                
                print("\n=== 明日预计变化 ===")
                print(f"精力变化: {tomorrow_data.get('stamina_change', 0)}")
                print(f"健康变化: {tomorrow_data.get('health_change', 0)}")
                print(f"快乐变化: {tomorrow_data.get('happiness_change', 0)}")
                print(f"饥饿度变化: {tomorrow_data.get('starvation_change', 0)}")
            
            return status_data
        else:
            print(f"获取状态信息失败: {data.get('message', '未知错误')}")
            return None
    
    def get_skill(self):
        """获取技能信息"""
        print("\n获取技能信息...")
        response = self.session.get(f"{self.base_url}/get_skill/")
        data = response.json()
        
        # 检查响应状态
        if response.status_code == 200 and data.get('status') == 1:
            skill_data = data.get('data', {})
            
            # 创建技能列表
            if 'datalist' in skill_data and skill_data['datalist']:
                print("\n=== 技能列表 ===")
                if self.username:
                    print(f"用户名: {self.username}")
                
                for skill in skill_data['datalist']:
                    print(f"\n技能ID: {skill.get('id', '未知ID')}")
                    print(f"名称: {skill.get('name', '未知名称')}")
                    print(f"等级: {skill.get('level', '未知')}")
                    print(f"等级数: {skill.get('level_num', 0)}")
                    print(f"技能值: {skill.get('skill_num', 0):.2f}")
                    print(f"理解力: {skill.get('comprehension', 0):.2f}")
                    print(f"顿悟几率: {skill.get('eureka_chance', 0):.2f}")
                    
                    # 处理小技能
                    if 'skill_mini' in skill and skill['skill_mini']:
                        print("小技能:")
                        for mini in skill['skill_mini']:
                            print(f"  - {mini.get('small_skill', '未知')}: {mini.get('skill_num', 0):.2f}")
                    else:
                        print("小技能: 无")
            else:
                print("\n未获取到技能列表或列表为空")
            
            # 显示副职业次数信息
            if 'sideline_times' in skill_data:
                print(f"\n今日剩余副职业次数: {skill_data['sideline_times']}")
            
            return skill_data
        else:
            print(f"获取技能信息失败: {data.get('message', '未知错误')}")
            return None

def main():
    print("正在初始化API请求...")
    api = ApiStatusSkill()
    
    # 获取状态信息
    status_data = api.get_status()
    
    # 获取技能信息
    skill_data = api.get_skill()
    
    print("\n请求完成!")

if __name__ == "__main__":
    main()
