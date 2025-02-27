// 全局变量
let userData = {};
let lastUpdatedTime = null;

// DOM元素
const parametersTable = document.getElementById('parameters-table');
const tableBody = document.getElementById('table-body');
const lastUpdatedElement = document.getElementById('last-updated');
const refreshBtn = document.getElementById('refresh-btn');
const userSearchInput = document.getElementById('user-search');
const totalUsersElement = document.getElementById('total-users');
const statusRecordsElement = document.getElementById('status-records');
const skillRecordsElement = document.getElementById('skill-records');
const userdetailRecordsElement = document.getElementById('userdetail-records');
const historyRecordsElement = document.getElementById('history-records');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    fetchData();
    
    // 设置事件监听器
    refreshBtn.addEventListener('click', fetchData);
    userSearchInput.addEventListener('input', filterUsers);
});

/**
 * 从服务器获取数据
 */
async function fetchData() {
    try {
        const response = await fetch('/api/data');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.status === 1) {
            userData = data.data;
            lastUpdatedTime = new Date();
            updateUI();
            fetchStats();
        } else {
            showError('获取数据失败: ' + data.message);
        }
    } catch (error) {
        showError('获取数据时出错: ' + error.message);
    }
}

/**
 * 获取统计数据
 */
async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.status === 1) {
            updateStats(data.data);
        }
    } catch (error) {
        console.error('获取统计数据时出错:', error);
    }
}

/**
 * 更新统计信息
 */
function updateStats(stats) {
    totalUsersElement.textContent = stats.total_users || 0;
    statusRecordsElement.textContent = stats.status_records || 0;
    skillRecordsElement.textContent = stats.skill_records || 0;
    userdetailRecordsElement.textContent = stats.userdetail_records || 0;
    historyRecordsElement.textContent = stats.history_records || 0;
}

/**
 * 更新UI
 */
function updateUI() {
    updateLastUpdated();
    renderParametersTable();
}

/**
 * 更新最后更新时间
 */
function updateLastUpdated() {
    if (lastUpdatedTime) {
        lastUpdatedElement.textContent = formatDate(lastUpdatedTime);
    }
}

/**
 * 渲染参数表格 - 每个用户一行，参数为列
 */
function renderParametersTable() {
    // 清空表格头和表格体
    const tableHead = parametersTable.querySelector('thead tr');
    tableBody.innerHTML = '';
    
    // 只保留第一列（用户名）
    while (tableHead.children.length > 1) {
        tableHead.removeChild(tableHead.lastChild);
    }
    
    // 从userData获取用户列表
    let usernames = [];
    
    // 检查status和skills对象中的用户
    if (userData.status) {
        usernames = usernames.concat(Object.keys(userData.status));
    }
    
    if (userData.skills) {
        usernames = usernames.concat(Object.keys(userData.skills));
    }
    
    if (userData.userdetail) {
        usernames = usernames.concat(Object.keys(userData.userdetail));
    }
    
    // 去重
    usernames = [...new Set(usernames)];
    
    if (usernames.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="2" class="empty-message">暂无用户数据</td></tr>';
        return;
    }
    
    // 定义表格列 - 用户详细信息
    const userDetailParams = [
        { key: 'level', label: '等级' },
        { key: 'now_exp', label: '当前经验' },
        { key: 'need_exp', label: '升级经验' },
        { key: 'work_at', label: '工作地点', isArray: true, index: 1 },
        { key: 'location', label: '州府', isArray: true, index: 1 },
        { key: 'location_county', label: '郡县', isArray: true, index: 1 },
        { key: 'native_place', label: '籍贯', isArray: true, index: 1 },
        { key: 'stay_at', label: '住所', isArray: true, index: 1 },
        { key: 'depository', label: '仓库', isArray: true, index: 1 }
    ];
    
    // 定义表格列 - 状态参数
    const statusParams = [
        { key: 'health', label: '健康' },
        { key: 'happiness', label: '愉悦度' },
        { key: 'stamina', label: '体力' },
        { key: 'starvation', label: '饱食度' },
        { key: 'strength', label: '力量' },
        { key: 'intelligence', label: '智力' }
    ];
    
    // 定义表格列 - 明天变化
    const changeParams = [
        { key: 'stamina_change', label: '体力变化' },
        { key: 'health_change', label: '健康变化' },
        { key: 'happiness_change', label: '愉悦度变化' },
        { key: 'starvation_change', label: '饱食度变化' }
    ];
    
    // 收集所有用户的技能名称
    const allSkills = new Set();
    usernames.forEach(username => {
        if (!userData.skills || !userData.skills[username]) return;
        
        const skillsData = userData.skills[username];
        if (skillsData.data && skillsData.data.datalist) {
            skillsData.data.datalist.forEach(skill => {
                if (skill && skill.name) {
                    allSkills.add(skill.name);
                }
            });
        }
    });
    
    // 创建表头 - 添加所有参数列
    const usernameHeader = document.createElement('th');
    usernameHeader.textContent = '用户名';
    tableHead.appendChild(usernameHeader);
    
    // 添加用户详细信息组标题
    const userDetailHeaderGroup = document.createElement('th');
    userDetailHeaderGroup.textContent = '用户信息';
    userDetailHeaderGroup.colSpan = userDetailParams.length;
    userDetailHeaderGroup.style.backgroundColor = '#e0f7fa';
    tableHead.appendChild(userDetailHeaderGroup);
    
    // 添加状态参数组标题
    const statusHeaderGroup = document.createElement('th');
    statusHeaderGroup.textContent = '状态参数';
    statusHeaderGroup.colSpan = statusParams.length;
    statusHeaderGroup.style.backgroundColor = '#e1e4e8';
    tableHead.appendChild(statusHeaderGroup);
    
    // 添加明天变化组标题
    const changeHeaderGroup = document.createElement('th');
    changeHeaderGroup.textContent = '明天预计变化';
    changeHeaderGroup.colSpan = changeParams.length;
    changeHeaderGroup.style.backgroundColor = '#e1e4e8';
    tableHead.appendChild(changeHeaderGroup);
    
    // 添加技能组标题
    const skillsHeaderGroup = document.createElement('th');
    skillsHeaderGroup.textContent = '技能';
    skillsHeaderGroup.colSpan = allSkills.size;
    skillsHeaderGroup.style.backgroundColor = '#e1e4e8';
    tableHead.appendChild(skillsHeaderGroup);
    
    // 添加最后更新列
    const lastUpdatedHeader = document.createElement('th');
    lastUpdatedHeader.textContent = '最后更新';
    tableHead.appendChild(lastUpdatedHeader);
    
    // 添加参数名称行
    const paramsRow = document.createElement('tr');
    
    // 添加一个空单元格来对应用户名列
    const emptyCell = document.createElement('th');
    paramsRow.appendChild(emptyCell);
    
    // 添加用户详细信息参数名称
    userDetailParams.forEach(param => {
        const paramHeader = document.createElement('th');
        paramHeader.textContent = param.label;
        paramsRow.appendChild(paramHeader);
    });
    
    // 添加状态参数名称
    statusParams.forEach(param => {
        const paramHeader = document.createElement('th');
        paramHeader.textContent = param.label;
        paramsRow.appendChild(paramHeader);
    });
    
    // 添加变化参数名称
    changeParams.forEach(param => {
        const paramHeader = document.createElement('th');
        paramHeader.textContent = param.label;
        paramsRow.appendChild(paramHeader);
    });
    
    // 添加技能名称
    Array.from(allSkills).sort().forEach(skillName => {
        const skillHeader = document.createElement('th');
        skillHeader.textContent = skillName;
        skillHeader.style.fontSize = '12px';
        paramsRow.appendChild(skillHeader);
    });
    
    // 添加一个空单元格来对应最后更新列
    const emptyLastUpdatedCell = document.createElement('th');
    paramsRow.appendChild(emptyLastUpdatedCell);
    
    tableBody.appendChild(paramsRow);
    
    // 为每个用户创建一行数据
    usernames.sort().forEach(username => {
        const userRow = document.createElement('tr');
        userRow.setAttribute('data-username', username);
        
        // 添加用户名单元格
        const usernameCell = document.createElement('td');
        usernameCell.textContent = username;
        usernameCell.style.fontWeight = 'bold';
        userRow.appendChild(usernameCell);
        
        // 添加用户详细信息
        userDetailParams.forEach(param => {
            const cell = document.createElement('td');
            
            // 检查是否有userdetail数据
            let userDetailValue = '';
            if (userData.userdetail && userData.userdetail[username]) {
                const userDetailData = userData.userdetail[username].data;
                if (userDetailData && userDetailData.data) {
                    if (param.isArray && Array.isArray(userDetailData.data[param.key])) {
                        userDetailValue = userDetailData.data[param.key][param.index] || '';
                    } else {
                        userDetailValue = userDetailData.data[param.key] || '';
                    }
                }
            }
            
            cell.textContent = userDetailValue;
            userRow.appendChild(cell);
        });
        
        // 添加状态参数值
        statusParams.forEach(param => {
            const valueCell = document.createElement('td');
            const statusData = userData.status[username] || {};
            
            // 处理嵌套数据结构
            let value = '—';
            if (statusData.data && statusData.data.today && statusData.data.today[param.key] !== undefined) {
                value = statusData.data.today[param.key];
            } else if (statusData[param.key] !== undefined) {
                value = statusData[param.key];
            }
            
            valueCell.textContent = value;
            
            // 为某些状态值添加颜色
            if (param.key === 'health' || param.key === 'happiness' || param.key === 'stamina' || param.key === 'starvation') {
                if (value >= 80) {
                    valueCell.className = 'status-high';
                } else if (value >= 50) {
                    valueCell.className = 'status-medium';
                } else if (value !== '—') {
                    valueCell.className = 'status-low';
                }
            }
            
            userRow.appendChild(valueCell);
        });
        
        // 添加变化参数值
        changeParams.forEach(param => {
            const valueCell = document.createElement('td');
            const statusData = userData.status[username] || {};
            
            // 处理嵌套数据结构
            let value = '—';
            if (statusData.data && statusData.data.tomorrow && statusData.data.tomorrow[param.key] !== undefined) {
                value = statusData.data.tomorrow[param.key].toFixed(1);
                
                // 添加变化指示符号
                if (value > 0) {
                    valueCell.className = 'status-high';
                    value = '+' + value;
                } else if (value < 0) {
                    valueCell.className = 'status-low';
                }
            }
            
            valueCell.textContent = value;
            userRow.appendChild(valueCell);
        });
        
        // 添加技能等级
        Array.from(allSkills).sort().forEach(skillName => {
            const valueCell = document.createElement('td');
            
            if (!userData.skills || !userData.skills[username]) {
                valueCell.textContent = '—';
                userRow.appendChild(valueCell);
                return;
            }
            
            const skillsData = userData.skills[username];
            
            let skillLevel = '—';
            let skillLevelNum = 0;
            
            // 从用户的技能列表中查找此技能
            if (skillsData.data && skillsData.data.datalist) {
                const skill = skillsData.data.datalist.find(s => s.name === skillName);
                if (skill) {
                    skillLevel = skill.level;
                    skillLevelNum = skill.level_num || 0;
                    if (skillLevelNum > 0) {
                        skillLevel += ` (${skillLevelNum})`;
                    }
                }
            }
            
            valueCell.textContent = skillLevel;
            
            // 根据技能等级添加样式
            if (skillLevelNum >= 3) {
                valueCell.className = 'status-high';
            } else if (skillLevelNum >= 1) {
                valueCell.className = 'status-medium';
            }
            
            userRow.appendChild(valueCell);
        });
        
        // 添加最后更新时间
        const timeCell = document.createElement('td');
        
        let latestTime = null;
        if (userData.status && userData.status[username] && userData.status[username].timestamp) {
            latestTime = new Date(userData.status[username].timestamp);
        }
        
        if (userData.skills && userData.skills[username] && userData.skills[username].timestamp) {
            const skillsTime = new Date(userData.skills[username].timestamp);
            if (!latestTime || skillsTime > latestTime) {
                latestTime = skillsTime;
            }
        }
        
        if (userData.userdetail && userData.userdetail[username] && userData.userdetail[username].timestamp) {
            const userDetailTime = new Date(userData.userdetail[username].timestamp);
            if (!latestTime || userDetailTime > latestTime) {
                latestTime = userDetailTime;
            }
        }
        
        timeCell.textContent = latestTime ? formatDate(latestTime) : '—';
        timeCell.style.fontSize = '12px';
        timeCell.style.color = '#586069';
        
        userRow.appendChild(timeCell);
        
        tableBody.appendChild(userRow);
    });
}

/**
 * 过滤用户表格
 */
function filterUsers() {
    const searchTerm = userSearchInput.value.toLowerCase().trim();
    const userRows = tableBody.querySelectorAll('tr[data-username]');
    
    userRows.forEach(row => {
        const username = row.getAttribute('data-username');
        if (username && username.toLowerCase().includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * 显示错误消息
 */
function showError(message) {
    console.error(message);
    tableBody.innerHTML = `<tr><td colspan="2" class="error-message">错误: ${message}</td></tr>`;
}

/**
 * 格式化日期
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    }).format(date);
}
