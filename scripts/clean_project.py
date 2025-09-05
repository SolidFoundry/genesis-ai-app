#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目清理脚本
==========

安全删除临时文件和脚本
"""

import os
import shutil
import sys
from pathlib import Path

def clean_project():
    """清理项目中的临时文件"""
    
    # 项目根目录
    project_root = Path.cwd()
    
    print("项目清理脚本")
    print("=" * 60)
    print(f"项目目录: {project_root}")
    print()
    
    # 要删除的文件列表
    files_to_delete = [
        # 日志文件
        "app.log",
        "server.log", 
        "mcp_server.log",
        
        # 数据库相关脚本
        "check_db_structure.py",
        "check_session_data.py",
        "clean_all_sessions.py",
        "clean_database.py",
        "clean_database_auto.py",
        "clear_and_test.py",
        "debug_tool_issue.py",
        "verify_db_save.py",
        
        # MCP相关测试脚本
        "fastmcp_client_headers_example.py",
        "fastmcp_client_test.py",
        "fixed_mcp_test_server.py",
        "mcp_client_diagnostic.py",
        "mcp_client_test.py",
        "mcp_server_simple.py",
        "simple_mcp_router_test.py",
        "simple_mcp_test.py",
        "simple_mcp_test_server.py",
        
        # API测试脚本
        "test_api_simple.py",
        "test_different_sessions.py",
        "test_mcp_router.py",
        "test_memory_final.py",
        "test_message_formatting.py",
        "test_original_curl.py",
        "test_original_query.py",
        "test_original_session.py",
        "test_session_accumulation.py",
        "test_tool_calling.py",
        "test_tool_execution.py",
        "test_tool_fix.py",
        "test_tool_schemas.py",
        
        # Scripts目录下的临时文件
        "scripts/mcp_start_improved.py",
        "scripts/mcp_start_simple.bat",
        "scripts/test_mcp_server.py",
        "scripts/test_mcp_service.py",
        "scripts/mcp_quick_test.bat",
        "scripts/mcp_test_dir.bat",
        "scripts/mcp_test_simple.bat",
        "scripts/mcp_test_auto.bat",
        "scripts/mcp_fastmcp.bat",
        "scripts/test_config.py",
        "scripts/test_genesis_permissions.py",
        "scripts/test_new_database.py",
        "scripts/test_postgres.py",
        "scripts/test_simple.bat",
    ]
    
    # 统计信息
    total_files = 0
    deleted_files = 0
    missing_files = 0
    
    for file_path in files_to_delete:
        total_files += 1
        target_file = project_root / file_path
        
        if target_file.exists():
            try:
                # 删除文件
                target_file.unlink()
                print(f"[删除] {file_path}")
                deleted_files += 1
                
            except Exception as e:
                print(f"[失败] 删除失败: {file_path} - {e}")
                missing_files += 1
        else:
            print(f"[跳过] 文件不存在: {file_path}")
            missing_files += 1
    
    # 清理空目录
    directories_to_check = [
        "scripts/__pycache__",
    ]
    
    print("\n清理空目录...")
    for dir_path in directories_to_check:
        target_dir = project_root / dir_path
        if target_dir.exists() and target_dir.is_dir():
            try:
                # 检查目录是否为空
                if not any(target_dir.iterdir()):
                    target_dir.rmdir()
                    print(f"[删除] 空目录: {dir_path}")
                else:
                    print(f"[保留] 目录不为空: {dir_path}")
            except Exception as e:
                print(f"[失败] 删除目录失败: {dir_path} - {e}")
    
    print("=" * 60)
    print("清理完成!")
    print(f"总文件数: {total_files}")
    print(f"成功删除: {deleted_files}")
    print(f"缺失文件: {missing_files}")
    
    # 显示当前项目状态
    print("\n当前项目根目录文件:")
    root_files = [f for f in project_root.iterdir() if f.is_file()]
    for f in sorted(root_files):
        print(f"  - {f.name}")
    
    print(f"\n当前scripts目录文件:")
    scripts_dir = project_root / "scripts"
    if scripts_dir.exists():
        script_files = [f for f in scripts_dir.iterdir() if f.is_file()]
        for f in sorted(script_files):
            print(f"  - {f.name}")
    
    return deleted_files, missing_files

if __name__ == "__main__":
    deleted, missing = clean_project()
    print(f"\n清理完成! 删除了 {deleted} 个文件，{missing} 个文件不存在。")
    print("如果需要恢复，请从备份目录复制文件。")