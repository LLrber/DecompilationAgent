#!/usr/bin/env python3
"""
测试URL功能的脚本
"""

from src.tools.mcp_tools import chunk_code, search_code_tool, security_audit_tool, analyze_data_structures_tool
import json

def test_url_functionality():
    """测试URL功能"""
    
    # 测试文件路径（本地文件用于验证功能）
    test_file = "test_sample.c"
    
    # 您提供的Dify文件URL（已过期，仅作示例）
    test_url = "https://upload.dify.ai/files/3708d998-2edb-4109-b352-74a57df7833c/file-preview?timestamp=1750607843&nonce=25ecdc40137607a06e0e165511b9b136&sign=9lCYA5JqSPIP5_xoZYMNpV11x9MSbyYKivq_CziYTwk="
    
    print("🚀 开始测试URL功能...")
    print(f"测试文件: {test_file}")
    print(f"示例URL: {test_url[:100]}...")
    print("注意：将使用本地文件测试功能，URL功能已集成到代码中")
    print("=" * 80)
    
    # 测试1: 代码分块
    print("\n📦 测试1: 代码分块功能")
    try:
        result = chunk_code(file_path=test_file, max_chunk_size=600)
        if "error" in result:
            print(f"❌ 错误: {result['error']}")
        else:
            print(f"✅ 成功分块: {result['total_chunks']} 个块")
            print(f"   总函数数: {result['file_info']['total_functions']}")
            print(f"   总行数: {result['file_info']['total_lines']}")
            print(f"   是否为URL: {result['file_info']['is_url']}")
            if result['chunks']:
                print(f"   第一个块包含 {len(result['chunks'][0]['functions'])} 个函数")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
    
    # 测试2: 代码搜索
    print("\n🔍 测试2: 代码搜索功能 - 搜索'modbus'")
    try:
        result = search_code_tool(file_path=test_file, search_pattern="modbus", search_type="function")
        if "error" in result:
            print(f"❌ 错误: {result['error']}")
        else:
            print(f"✅ 搜索成功: 找到 {result['total_matches']} 个匹配")
            if result['results']:
                print(f"   前3个匹配:")
                for i, match in enumerate(result['results'][:3]):
                    print(f"     {i+1}. 行{match['line_number']}: {match['line_content'][:50]}...")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
    
    # 测试3: 安全审计
    print("\n🛡️ 测试3: 安全审计功能")
    try:
        result = security_audit_tool(file_path=test_file)
        if "error" in result:
            print(f"❌ 错误: {result['error']}")
        else:
            print(f"✅ 安全审计完成")
            print(f"   总问题数: {result['summary']['total_issues']}")
            print(f"   安全评分: {result['summary']['security_score']}/100")
            print(f"   风险评估: {result['risk_assessment']['overall_risk']}")
            if result['summary']['severity_distribution']:
                print(f"   严重性分布: {result['summary']['severity_distribution']}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
    
    # 测试4: 数据结构分析
    print("\n🏗️ 测试4: 数据结构分析功能")
    try:
        result = analyze_data_structures_tool(file_path=test_file)
        if "error" in result:
            print(f"❌ 错误: {result['error']}")
        else:
            print(f"✅ 数据结构分析完成")
            print(f"   结构体数量: {result['summary']['total_structures']}")
            print(f"   枚举数量: {result['summary']['total_enums']}")
            print(f"   类型定义数量: {result['summary']['total_typedefs']}")
            if result['structures']:
                print(f"   最复杂的结构体: {result['analysis']['most_complex_struct']['name'] if result['analysis']['most_complex_struct'] else '无'}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
    
    print("\n" + "=" * 80)
    print("🎉 URL功能测试完成！")

if __name__ == "__main__":
    test_url_functionality() 