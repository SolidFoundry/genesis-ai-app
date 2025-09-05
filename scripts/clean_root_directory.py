#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目根目录最终清理脚本
=====================

清理项目根目录下不需要提交到GitHub的文件
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

def clean_root_directory():
    """清理项目根目录"""
    
    # 项目根目录
    project_root = Path.cwd()
    
    print("项目根目录最终清理脚本")
    print("=" * 60)
    print(f"项目目录: {project_root}")
    print()
    
    # 要删除的文件和目录列表
    items_to_remove = [
        # 临时文件
        "=0.30.0",
        
        # 运行时文件
        "mcp_server.pid",
        "mcp_test.html", 
        "test_request.json",
        
        # 缓存目录
        "__pycache__",
        
        # 日志目录
        "logs",
        
        # 虚拟环境目录（应该被.gitignore，但可能意外创建）
        ".venv",
        
        # 环境变量文件（包含敏感信息）
        ".env",
    ]
    
    # 统计信息
    total_items = 0
    removed_items = 0
    missing_items = 0
    
    for item_path in items_to_remove:
        total_items += 1
        target_item = project_root / item_path
        
        if target_item.exists():
            try:
                if target_item.is_dir():
                    # 递归删除目录
                    shutil.rmtree(target_item)
                    print(f"[删除] 目录: {item_path}")
                else:
                    # 删除文件
                    target_item.unlink()
                    print(f"[删除] 文件: {item_path}")
                removed_items += 1
                
            except Exception as e:
                print(f"[失败] 删除失败: {item_path} - {e}")
                missing_items += 1
        else:
            print(f"[跳过] 不存在: {item_path}")
            missing_items += 1
    
    # 检查是否需要保留的文档文件
    doc_files = [
        "FASTMCP_CLIENT_HEADERS_GUIDE.md",
        "MCP_INTEGRATION_GUIDE.md",
    ]
    
    print("\n文档文件检查:")
    for doc_file in doc_files:
        target_file = project_root / doc_file
        if target_file.exists():
            print(f"[保留] 文档文件: {doc_file}")
        else:
            print(f"[不存在] 文档文件: {doc_file}")
    
    print("=" * 60)
    print("清理完成!")
    print(f"总项目数: {total_items}")
    print(f"成功删除: {removed_items}")
    print(f"缺失项目: {missing_items}")
    
    # 显示最终项目状态
    print("\n最终项目根目录文件:")
    root_items = [item for item in project_root.iterdir() 
                  if not item.name.startswith('.') and item.name not in ['__pycache__', '.venv', 'logs']]
    
    for item in sorted(root_items):
        if item.is_file():
            print(f"  [FILE] {item.name}")
        else:
            print(f"  [DIR] {item.name}/")
    
    return removed_items, missing_items

if __name__ == "__main__":
    removed, missing = clean_root_directory()
    print(f"\n最终清理完成! 删除了 {removed} 个项目，{missing} 个项目不存在。")
    print("项目已准备好提交到GitHub！")