// ==UserScript==
// @name         Civitas Status and Skill Monitor
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  获取并显示角色的状态和技能信息，并自动发送到后端服务器
// @author       Civitas2 Player
// @match        https://civitas2.top/*
// @grant        GM_xmlhttpRequest
// @connect      api.civitas2.top
// @connect      localhost
// @connect      127.0.0.1
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';
    
    // 配置变量
    const BASE_URL = "https://api.civitas2.top";
    const SERVER_URL = "http://localhost:5000"; // 后端服务器地址
    let username = null;
    
    // 初始化
    console.log("Civitas Status and Skill Monitor 初始化中...");
    
    // 主函数
    async function main() {
        try {
            // 获取用户名
            await getUserName();
            
            // 获取用户详细信息
            const userDetailData = await getUserDetail();
            
            // 获取状态信息
            const statusData = await getStatus();
            
            // 获取技能信息
            const skillData = await getSkill();
            
            // 将数据发送到后端服务器
            if (userDetailData) {
                sendDataToServer('userdetail', userDetailData);
            }
            
            if (statusData) {
                sendDataToServer('status', statusData);
            }
            
            if (skillData) {
                sendDataToServer('skill', skillData);
            }
            
            console.log("Civitas Status and Skill Monitor 数据获取完成!");
        } catch (error) {
            console.error("Civitas Monitor 发生错误:", error);
        }
    }
    
    // 获取用户名
    async function getUserName() {
        console.log("\n获取用户信息...");
        try {
            const response = await fetchAPI(`${BASE_URL}/get_user_estate_list/`);
            
            if (response.status === 1) {
                const userData = response.data;
                if (userData && userData.username) {
                    username = userData.username;
                    console.log(`用户名: ${username}`);
                } else {
                    console.log("未能获取用户名");
                }
            } else {
                console.log(`获取用户信息失败: ${response.message || "未知错误"}`);
            }
            return response.data;
        } catch (error) {
            console.error("获取用户名时发生错误:", error);
            return null;
        }
    }
    
    // 获取状态信息
    async function getStatus() {
        console.log("\n获取状态信息...");
        try {
            const response = await fetchAPI(`${BASE_URL}/get_status/`);
            
            if (response.status === 1) {
                const statusData = response.data;
                
                // 处理今天的状态数据
                if (statusData.today) {
                    const todayData = statusData.today;
                    
                    console.group("=== 今日状态 ===");
                    if (username) {
                        console.log(`用户名: ${username}`);
                    }
                    
                    console.log(`精力: ${todayData.stamina || 0}`);
                    console.log(`健康: ${todayData.health || 0}`);
                    console.log(`快乐: ${todayData.happiness || 0}`);
                    console.log(`饥饿度: ${todayData.starvation || 0}`);
                    console.groupEnd();
                }
                
                // 处理明天的变化数据
                if (statusData.tomorrow) {
                    const tomorrowData = statusData.tomorrow;
                    
                    console.group("=== 明日预计变化 ===");
                    console.log(`精力变化: ${tomorrowData.stamina_change || 0}`);
                    console.log(`健康变化: ${tomorrowData.health_change || 0}`);
                    console.log(`快乐变化: ${tomorrowData.happiness_change || 0}`);
                    console.log(`饥饿度变化: ${tomorrowData.starvation_change || 0}`);
                    console.groupEnd();
                }
                
                return {
                    username: username,
                    timestamp: new Date().toISOString(),
                    data: statusData
                };
            } else {
                console.log(`获取状态信息失败: ${response.message || "未知错误"}`);
                return null;
            }
        } catch (error) {
            console.error("获取状态信息时发生错误:", error);
            return null;
        }
    }
    
    // 获取技能信息
    async function getSkill() {
        console.log("\n获取技能信息...");
        try {
            const response = await fetchAPI(`${BASE_URL}/get_skill/`);
            
            if (response.status === 1) {
                const skillData = response.data;
                
                // 创建技能列表
                if (skillData.datalist && skillData.datalist.length > 0) {
                    console.group("=== 技能列表 ===");
                    if (username) {
                        console.log(`用户名: ${username}`);
                    }
                    
                    skillData.datalist.forEach(skill => {
                        console.group(`技能: ${skill.name || "未知名称"} (ID: ${skill.id || "未知ID"})`);
                        console.log(`等级: ${skill.level || "未知"}`);
                        console.log(`等级数: ${skill.level_num || 0}`);
                        console.log(`技能值: ${skill.skill_num ? skill.skill_num.toFixed(2) : 0}`);
                        console.log(`理解力: ${skill.comprehension ? skill.comprehension.toFixed(2) : 0}`);
                        console.log(`顿悟几率: ${skill.eureka_chance ? skill.eureka_chance.toFixed(2) : 0}`);
                        
                        // 处理小技能
                        if (skill.skill_mini && skill.skill_mini.length > 0) {
                            console.group("小技能:");
                            skill.skill_mini.forEach(mini => {
                                console.log(`${mini.small_skill || "未知"}: ${mini.skill_num ? mini.skill_num.toFixed(2) : 0}`);
                            });
                            console.groupEnd();
                        } else {
                            console.log("小技能: 无");
                        }
                        console.groupEnd();
                    });
                    
                    console.groupEnd();
                } else {
                    console.log("\n未获取到技能列表或列表为空");
                }
                
                // 显示副职业次数信息
                if ('sideline_times' in skillData) {
                    console.log(`\n今日剩余副职业次数: ${skillData.sideline_times}`);
                }
                
                return {
                    username: username,
                    timestamp: new Date().toISOString(),
                    data: skillData
                };
            } else {
                console.log(`获取技能信息失败: ${response.message || "未知错误"}`);
                return null;
            }
        } catch (error) {
            console.error("获取技能信息时发生错误:", error);
            return null;
        }
    }
    
    // 获取用户详细信息
    async function getUserDetail() {
        console.log("\n获取用户详细信息...");
        try {
            const response = await fetchAPI(`${BASE_URL}/get_userdetail/`);
            
            if (response.status === 1) {
                const userDetailData = response.data;
                
                console.group("=== 用户详细信息 ===");
                console.log(`用户名: ${userDetailData.username || "未知"}`);
                console.log(`头像: ${userDetailData.avatar || "未知"}`);
                console.log(`等级: ${userDetailData.level || 0}`);
                console.log(`当前经验: ${userDetailData.now_exp || 0}`);
                console.log(`升级需要经验: ${userDetailData.need_exp || 0}`);
                
                if (userDetailData.work_at) {
                    console.log(`工作地点: ${userDetailData.work_at[1] || "未知"}`);
                }
                
                if (userDetailData.location) {
                    console.log(`所在州府: ${userDetailData.location[1] || "未知"}`);
                }
                
                if (userDetailData.location_county) {
                    console.log(`所在郡县: ${userDetailData.location_county[1] || "未知"}`);
                }
                
                if (userDetailData.native_place) {
                    console.log(`籍贯: ${userDetailData.native_place[1] || "未知"}`);
                }
                
                if (userDetailData.stay_at) {
                    console.log(`住所: ${userDetailData.stay_at[1] || "未知"}`);
                }
                
                if (userDetailData.depository) {
                    console.log(`仓库: ${userDetailData.depository[1] || "未知"}`);
                }
                
                console.log(`UID: ${userDetailData.uid || "未知"}`);
                console.groupEnd();
                
                return {
                    username: username,
                    timestamp: new Date().toISOString(),
                    data: userDetailData
                };
            } else {
                console.log(`获取用户详细信息失败: ${response.message || "未知错误"}`);
                return null;
            }
        } catch (error) {
            console.error("获取用户详细信息时发生错误:", error);
            return null;
        }
    }
    
    // 发送数据到后端服务器
    function sendDataToServer(type, data) {
        let url;
        let typeName;
        
        switch(type) {
            case 'status':
                url = `${SERVER_URL}/api/record_status`;
                typeName = '状态';
                break;
            case 'skill':
                url = `${SERVER_URL}/api/record_skill`;
                typeName = '技能';
                break;
            case 'userdetail':
                url = `${SERVER_URL}/api/record_userdetail`;
                typeName = '用户详细信息';
                break;
            default:
                console.error('未知的数据类型');
                return;
        }
        
        console.log(`正在发送${typeName}数据到服务器...`);
        
        // 使用GM_xmlhttpRequest进行跨域请求
        GM_xmlhttpRequest({
            method: 'POST',
            url: url,
            data: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json'
            },
            onload: function(response) {
                try {
                    const result = JSON.parse(response.responseText);
                    if (result.status === 1) {
                        console.log(`${typeName}数据已成功发送到服务器`);
                    } else {
                        console.error(`发送${typeName}数据失败:`, result.message);
                    }
                } catch (e) {
                    console.error(`解析服务器响应时出错:`, e);
                }
            },
            onerror: function(error) {
                console.error(`发送${typeName}数据时出错:`, error);
            }
        });
    }
    
    // 封装API请求函数
    function fetchAPI(url) {
        return new Promise((resolve, reject) => {
            fetch(url, {
                method: 'GET',
                credentials: 'include', // 包含cookies
                headers: {
                    'Accept': '*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': 'https://civitas2.top/',
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => resolve(data))
            .catch(error => reject(error));
        });
    }
    
    // 自动执行主函数
    console.log("页面加载完成，自动执行数据收集...");
    main();
    
})();
