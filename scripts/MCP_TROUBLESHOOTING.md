# MCP服务器启动故障排除指南

## 问题：mcp_start.bat 运行闪退

### 可能的原因和解决方案

#### 1. Python环境问题
**症状**: 脚本运行时立即闪退，没有任何错误信息

**解决方案**:
1. 打开命令提示符，手动运行：
   ```cmd
   cd D:\GitHub_Projects\genesis-ai-app
   python --version
   ```

2. 如果Python不可用，确保：
   - Python已正确安装
   - Python已添加到系统PATH环境变量
   - 使用项目虚拟环境：`.venv\Scripts\activate`

#### 2. 依赖缺失问题
**症状**: 启动时出现模块导入错误

**解决方案**:
1. 激活虚拟环境并安装依赖：
   ```cmd
   .venv\Scripts\activate
   pip install fastmcp
   ```

2. 或者使用Poetry：
   ```cmd
   poetry install
   ```

#### 3. 端口冲突
**症状**: 启动时提示端口被占用

**解决方案**:
1. 检查端口占用：
   ```cmd
   netstat -ano | findstr :8001
   ```

2. 终止占用端口的进程：
   ```cmd
   taskkill /F /PID <进程ID>
   ```

#### 4. 配置文件问题
**症状**: 配置读取错误

**解决方案**:
1. 确保 `.env` 文件存在并包含MCP配置：
   ```env
   MCP__SERVER__HOST=0.0.0.0
   MCP__SERVER__PORT=8001
   MCP__SERVER__DEBUG=true
   ```

### 调试步骤

#### 步骤1: 使用调试脚本
运行调试脚本获取详细信息：
```cmd
scripts\mcp_start_debug.bat
```

#### 步骤2: 手动测试
在命令提示符中逐步测试：
```cmd
cd D:\GitHub_Projects\genesis-ai-app
python -c "import apps.mcp_server.main; print('导入成功')"
python -m apps.mcp_server.main
```

#### 步骤3: 检查日志
查看是否有日志文件生成：
```cmd
dir logs\
type logs\mcp_server.log
```

### 常用命令

```cmd
# 检查Python环境
python --version

# 检查模块导入
python -c "import apps.mcp_server.main"

# 检查端口占用
netstat -ano | findstr :8001

# 使用Poetry启动
poetry run python -m apps.mcp_server.main

# 使用虚拟环境启动
.venv\Scripts\python -m apps.mcp_server.main
```

### 如果问题仍然存在

1. 确保在正确的目录中运行脚本
2. 检查所有依赖是否正确安装
3. 尝试使用Make命令：`make mcp-start`
4. 查看项目文档或联系技术支持