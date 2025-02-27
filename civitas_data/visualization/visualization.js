// 全局变量
let userData = null;
let statusChart = null;
let skillChart = null;
let selectedUser = null;

// DOM 元素
const refreshBtn = document.getElementById('refresh-btn');
const userList = document.getElementById('user-list');
const userSearch = document.getElementById('user-search');
const selectedUserElement = document.getElementById('selected-user');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');

// 统计数据元素
const totalUsersElement = document.getElementById('total-users');
const statusRecordsElement = document.getElementById('status-records');
const skillRecordsElement = document.getElementById('skill-records');
const historyRecordsElement = document.getElementById('history-records');
const lastUpdatedElement = document.getElementById('last-updated');

// 状态和技能元素
const statusGrid = document.getElementById('status-grid');
const skillsList = document.getElementById('skills-list');
const skillSelect = document.getElementById('skill-select');

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    fetchData();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    // 刷新按钮
    refreshBtn.addEventListener('click', fetchData);
    
    // 用户搜索
    userSearch.addEventListener('input', filterUserList);
    
    // 标签页切换
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
    
    // 技能选择
    skillSelect.addEventListener('change', updateSkillChart);
}

// 获取数据
async function fetchData() {
    try {
        const response = await fetch('/api/data');
        const result = await response.json();
        
        if (result.status === 1) {
            userData = result.data;
            updateStats();
            populateUserList();
            
            // 如果已经选择了用户，刷新用户数据
            if (selectedUser) {
                displayUserData(selectedUser);
            }
        } else {
            showError('获取数据失败');
        }
    } catch (error) {
        console.error('获取数据出错:', error);
        showError('获取数据出错: ' + error.message);
    }
}

// 更新统计数据
function updateStats() {
    const statusUsers = Object.keys(userData.status);
    const skillUsers = Object.keys(userData.skills);
    const allUsers = [...new Set([...statusUsers, ...skillUsers])];
    
    totalUsersElement.textContent = allUsers.length;
    statusRecordsElement.textContent = statusUsers.length;
    skillRecordsElement.textContent = skillUsers.length;
    historyRecordsElement.textContent = userData.history.length;
    
    // 格式化日期
    const lastUpdated = new Date(userData.last_updated);
    lastUpdatedElement.textContent = formatDate(lastUpdated);
}

// 填充用户列表
function populateUserList() {
    userList.innerHTML = '';
    
    const statusUsers = Object.keys(userData.status);
    const skillUsers = Object.keys(userData.skills);
    const allUsers = [...new Set([...statusUsers, ...skillUsers])];
    
    if (allUsers.length === 0) {
        const emptyItem = document.createElement('li');
        emptyItem.textContent = '暂无用户数据';
        emptyItem.classList.add('loading');
        userList.appendChild(emptyItem);
        return;
    }
    
    // 按用户名排序
    allUsers.sort();
    
    allUsers.forEach(username => {
        const listItem = document.createElement('li');
        listItem.textContent = username;
        listItem.addEventListener('click', () => {
            // 移除之前的选中状态
            const activeItems = userList.querySelectorAll('.active');
            activeItems.forEach(item => item.classList.remove('active'));
            
            // 添加新的选中状态
            listItem.classList.add('active');
            
            // 显示选中用户的数据
            selectedUser = username;
            displayUserData(username);
        });
        
        // 如果是当前选中的用户，添加active类
        if (username === selectedUser) {
            listItem.classList.add('active');
        }
        
        userList.appendChild(listItem);
    });
}

// 过滤用户列表
function filterUserList() {
    const searchTerm = userSearch.value.toLowerCase();
    const listItems = userList.querySelectorAll('li:not(.loading)');
    
    listItems.forEach(item => {
        const username = item.textContent.toLowerCase();
        if (username.includes(searchTerm)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// 切换标签页
function switchTab(tabId) {
    // 更新按钮状态
    tabButtons.forEach(button => {
        if (button.getAttribute('data-tab') === tabId) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
    
    // 更新标签页显示
    tabPanes.forEach(pane => {
        if (pane.id === tabId + '-tab') {
            pane.classList.add('active');
            
            // 如果切换到图表标签页，重新渲染图表
            if (tabId === 'charts' && selectedUser) {
                renderCharts(selectedUser);
            }
        } else {
            pane.classList.remove('active');
        }
    });
}

// 显示用户数据
function displayUserData(username) {
    selectedUserElement.textContent = username;
    
    // 显示状态数据
    displayStatusData(username);
    
    // 显示技能数据
    displaySkillsData(username);
    
    // 渲染图表
    if (document.getElementById('charts-tab').classList.contains('active')) {
        renderCharts(username);
    }
}

// 显示状态数据
function displayStatusData(username) {
    const statusData = userData.status[username];
    
    if (!statusData || !statusData.data || !statusData.data.today) {
        statusGrid.innerHTML = '<div class="empty-message">该用户没有状态数据</div>';
        return;
    }
    
    const today = statusData.data.today;
    const tomorrow = statusData.data.tomorrow || {};
    
    statusGrid.innerHTML = `
        <div class="status-item">
            <div class="status-label">精力</div>
            <div class="status-value">${today.stamina || 0}</div>
            <div class="status-change">${formatChange(tomorrow.stamina_change)}</div>
        </div>
        <div class="status-item">
            <div class="status-label">健康</div>
            <div class="status-value">${today.health || 0}</div>
            <div class="status-change">${formatChange(tomorrow.health_change)}</div>
        </div>
        <div class="status-item">
            <div class="status-label">快乐</div>
            <div class="status-value">${today.happiness || 0}</div>
            <div class="status-change">${formatChange(tomorrow.happiness_change)}</div>
        </div>
        <div class="status-item">
            <div class="status-label">饥饿度</div>
            <div class="status-value">${today.starvation || 0}</div>
            <div class="status-change">${formatChange(tomorrow.starvation_change)}</div>
        </div>
        <div class="status-item" style="grid-column: span 2;">
            <div class="status-label">数据更新时间</div>
            <div class="status-value" style="font-size: 16px;">${formatDate(new Date(statusData.timestamp))}</div>
        </div>
    `;
}

// 显示技能数据
function displaySkillsData(username) {
    const skillsData = userData.skills[username];
    
    if (!skillsData || !skillsData.data || !skillsData.data.datalist) {
        skillsList.innerHTML = '<div class="empty-message">该用户没有技能数据</div>';
        return;
    }
    
    const skills = skillsData.data.datalist;
    const sidelineTimes = skillsData.data.sideline_times;
    
    skillsList.innerHTML = '';
    
    // 添加副职业次数
    const sidelineItem = document.createElement('div');
    sidelineItem.classList.add('skill-card');
    sidelineItem.style.gridColumn = 'span 2';
    sidelineItem.innerHTML = `
        <div class="skill-header">
            <span class="skill-name">今日剩余副职业次数</span>
            <span class="skill-level">${sidelineTimes || 0}</span>
        </div>
        <div class="skill-details">
            <div class="skill-detail">
                <span>数据更新时间</span>
                <span>${formatDate(new Date(skillsData.timestamp))}</span>
            </div>
        </div>
    `;
    skillsList.appendChild(sidelineItem);
    
    // 更新技能选择下拉菜单
    skillSelect.innerHTML = '<option value="">选择技能...</option>';
    
    // 添加每个技能
    skills.forEach(skill => {
        // 创建技能卡片
        const skillCard = document.createElement('div');
        skillCard.classList.add('skill-card');
        
        // 小技能HTML
        let miniSkillsHtml = '';
        if (skill.skill_mini && skill.skill_mini.length > 0) {
            miniSkillsHtml = `
                <div class="skill-mini-header">小技能:</div>
                <div class="skill-mini-list">
                    ${skill.skill_mini.map(mini => `
                        <div class="skill-mini-item">
                            <span>${mini.small_skill || "未知"}</span>
                            <span>${mini.skill_num ? mini.skill_num.toFixed(2) : 0}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            miniSkillsHtml = `
                <div class="skill-mini-header">小技能:</div>
                <div class="skill-mini-list">无</div>
            `;
        }
        
        skillCard.innerHTML = `
            <div class="skill-header">
                <span class="skill-name">${skill.name || "未知名称"}</span>
                <span class="skill-level">${skill.level || "未知"} (Lv.${skill.level_num || 0})</span>
            </div>
            <div class="skill-details">
                <div class="skill-detail">
                    <span>技能值</span>
                    <span>${skill.skill_num ? skill.skill_num.toFixed(2) : 0}</span>
                </div>
                <div class="skill-detail">
                    <span>理解力</span>
                    <span>${skill.comprehension ? skill.comprehension.toFixed(2) : 0}</span>
                </div>
                <div class="skill-detail">
                    <span>顿悟几率</span>
                    <span>${skill.eureka_chance ? skill.eureka_chance.toFixed(2) : 0}</span>
                </div>
            </div>
            ${miniSkillsHtml}
        `;
        
        skillsList.appendChild(skillCard);
        
        // 添加到技能选择下拉菜单
        const option = document.createElement('option');
        option.value = skill.id;
        option.textContent = skill.name;
        skillSelect.appendChild(option);
    });
}

// 渲染图表
function renderCharts(username) {
    // 渲染状态图表
    renderStatusChart(username);
    
    // 初始化技能图表（但不渲染，等待用户选择）
    initSkillChart();
}

// 渲染状态图表
function renderStatusChart(username) {
    const statusData = userData.status[username];
    
    if (!statusData || !statusData.data || !statusData.data.today) {
        return;
    }
    
    const today = statusData.data.today;
    
    const ctx = document.getElementById('status-chart').getContext('2d');
    
    // 如果已有图表，销毁它
    if (statusChart) {
        statusChart.destroy();
    }
    
    // 创建新图表
    statusChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['精力', '健康', '快乐', '饥饿度'],
            datasets: [{
                label: '当前值',
                data: [
                    today.stamina || 0,
                    today.health || 0,
                    today.happiness || 0,
                    today.starvation || 0
                ],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(255, 99, 132, 0.6)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// 初始化技能图表
function initSkillChart() {
    const ctx = document.getElementById('skill-chart').getContext('2d');
    
    // 如果已有图表，销毁它
    if (skillChart) {
        skillChart.destroy();
        skillChart = null;
    }
    
    // 创建空图表
    skillChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [],
            datasets: [{
                label: '技能数据',
                data: [],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 更新技能图表
function updateSkillChart() {
    const skillId = skillSelect.value;
    
    if (!skillId || !selectedUser) {
        return;
    }
    
    const skillsData = userData.skills[selectedUser];
    
    if (!skillsData || !skillsData.data || !skillsData.data.datalist) {
        return;
    }
    
    const skill = skillsData.data.datalist.find(s => s.id == skillId);
    
    if (!skill) {
        return;
    }
    
    const ctx = document.getElementById('skill-chart').getContext('2d');
    
    // 如果已有图表，销毁它
    if (skillChart) {
        skillChart.destroy();
    }
    
    // 准备数据
    const labels = ['技能值', '等级', '理解力', '顿悟几率'];
    const data = [
        skill.skill_num || 0,
        skill.level_num || 0,
        skill.comprehension || 0,
        skill.eureka_chance || 0
    ];
    
    // 添加小技能
    if (skill.skill_mini && skill.skill_mini.length > 0) {
        skill.skill_mini.forEach(mini => {
            labels.push(mini.small_skill || '未知小技能');
            data.push(mini.skill_num || 0);
        });
    }
    
    // 创建新图表
    skillChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: skill.name,
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    beginAtZero: true
                }
            }
        }
    });
}

// 辅助函数：格式化变化值
function formatChange(value) {
    if (!value) return '';
    
    const formattedValue = Math.abs(value).toFixed(2);
    
    if (value > 0) {
        return `<span style="color: green;">+${formattedValue}</span>`;
    } else if (value < 0) {
        return `<span style="color: red;">${-formattedValue}</span>`;
    } else {
        return `<span>0</span>`;
    }
}

// 辅助函数：格式化日期时间
function formatDate(date) {
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric'
    });
}

// 显示错误信息
function showError(message) {
    console.error(message);
    alert('错误: ' + message);
}
