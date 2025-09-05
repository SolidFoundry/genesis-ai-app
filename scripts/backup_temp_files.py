#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目文件备份脚本
==============

安全备份要删除的临时文件和脚本
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

def backup_files():
    """备份要删除的文件"""
    
    # 项目根目录
    project_root = Path.cwd()
    
    # 备份目录
    backup_dir = Path("D:/GitHub_Projects/backup/genesis-ai-app-temp-files_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"备份目录: {backup_dir}")
    print("=" * 60)
    
    # 要备份的文件列表
    files_to_backup = [
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
    backed_up_files = 0
    missing_files = 0
    
    for file_path in files_to_backup:
        total_files += 1
        source_file = project_root / file_path
        
        if source_file.exists():
            try:
                # 创建目标目录
                target_file = backup_dir / file_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(source_file, target_file)
                print(f"[成功] 已备份: {file_path}")
                backed_up_files += 1
                
            except Exception as e:
                print(f"[失败] 备份失败: {file_path} - {e}")
                missing_files += 1
        else:
            print(f"[警告] 文件不存在: {file_path}")
            missing_files += 1
    
    # 创建备份清单
    manifest_file = backup_dir / "backup_manifest.txt"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write(f"Genesis AI App 备份清单\n")
        f.write(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"项目目录: {project_root}\n")
        f.write(f"备份目录: {backup_dir}\n")
        f.write("=" * 60 + "\n")
        f.write(f"统计信息:\n")
        f.write(f"  总文件数: {total_files}\n")
        f.write(f"  成功备份: {backed_up_files}\n")
        f.write(f"  缺失文件: {missing_files}\n")
        f.write("=" * 60 + "\n")
        f.write("备份文件列表:\n")
        
        for file_path in files_to_backup:
            source_file = project_root / file_path
            status = "[OK]" if source_file.exists() else "[MISS]"
            f.write(f"  {status} {file_path}\n")
    
    print("=" * 60)
    print("备份完成!")
    print(f"总文件数: {total_files}")
    print(f"成功备份: {backed_up_files}")
    print(f"缺失文件: {missing_files}")
    print(f"备份目录: {backup_dir}")
    print(f"备份清单: {manifest_file}")
    
    return backup_dir

if __name__ == "__main__":
    backup_dir = backup_files()
    print(f"\n备份完成，可以安全进行清理操作。")
    print(f"如果清理后出现问题，可以从备份目录恢复文件。")