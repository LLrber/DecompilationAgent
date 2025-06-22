#!/usr/bin/env python3
"""
简单的URL功能测试
"""

from src.tools.mcp_tools import chunk_code
import json

def test_simple_url():
    """测试简单的URL功能"""
    
    # 使用一个公开的示例C代码URL
    test_url = "https://raw.githubusercontent.com/torvalds/linux/master/kernel/fork.c"
    
    print("🚀 测试URL功能...")
    print(f"测试URL: {test_url}")
    print("=" * 80)
    
    try:
        result = chunk_code(file_path=test_url, max_chunk_size=100)
        if "error" in result:
            print(f"❌ 错误: {result['error']}")
        else:
            print(f"✅ 成功从URL获取代码并分块:")
            print(f"   总块数: {result['total_chunks']}")
            print(f"   总函数数: {result['file_info']['total_functions']}")
            print(f"   总行数: {result['file_info']['total_lines']}")
            print(f"   是否为URL: {result['file_info']['is_url']}")
            print(f"   显示路径: {result['file_info']['path']}")
            
            if result['chunks']:
                print(f"   第一个块包含 {len(result['chunks'][0]['functions'])} 个函数")
                if result['chunks'][0]['functions']:
                    print(f"   第一个函数: {result['chunks'][0]['functions'][0]['name']}")
                    
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
    
    print("\n" + "=" * 80)
    print("🎉 URL功能测试完成！")

if __name__ == "__main__":
    test_simple_url() 