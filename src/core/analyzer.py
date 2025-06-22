"""
代码分析器

负责解析和分析C代码的核心引擎。
"""

import re
from typing import List
from dataclasses import asdict

from ..models.data_models import FunctionInfo


class CodeAnalyzer:
    """代码分析核心类"""
    
    def __init__(self):
        self.call_pattern = re.compile(r'\b(\w+)\s*\(')
        self.function_pattern = re.compile(
            r'^\s*(?:(static|extern|inline)\s+)?' +
            r'(?:(const|volatile)\s+)?' +
            r'(\w+(?:\s*\*)*)\s+' +
            r'(?:__cdecl\s+|__stdcall\s+|__fastcall\s+)?' +
            r'(\w+)\s*' +
            r'\(([^)]*)\)\s*$'
        )
        
    def extract_functions(self, code: str) -> List[FunctionInfo]:
        """提取函数信息"""
        functions = []
        lines = code.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('//') or line.startswith('/*') or line.startswith('#'):
                i += 1
                continue
            
            # 匹配函数声明
            func_match = self.function_pattern.match(line)
            if not func_match:
                simple_match = re.match(r'^\s*(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*$', line)
                if simple_match and i + 1 < len(lines) and lines[i + 1].strip() == '{':
                    func_name = simple_match.group(1)
                else:
                    i += 1
                    continue
            else:
                func_name = func_match.group(4)
            
            if i + 1 < len(lines) and lines[i + 1].strip() == '{':
                start_line = i + 1
                
                # 找到函数结束
                brace_count = 0
                j = i + 1
                while j < len(lines):
                    for char in lines[j]:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_line = j + 1
                                break
                    if brace_count == 0:
                        break
                    j += 1
                
                if brace_count == 0:
                    func_code = '\n'.join(lines[i:end_line])
                    calls = self._extract_function_calls(func_code)
                    complexity = self._calculate_complexity(func_code)
                    
                    functions.append(FunctionInfo(
                        name=func_name,
                        signature=line,
                        start_line=start_line,
                        end_line=end_line,
                        code=func_code,
                        calls=calls,
                        complexity=complexity
                    ))
                    
                    i = end_line
                else:
                    i += 1
            else:
                i += 1
                
        return functions
    
    def _extract_function_calls(self, code: str) -> List[str]:
        """提取函数调用"""
        calls = []
        matches = self.call_pattern.findall(code)
        excluded = {'if', 'while', 'for', 'switch', 'sizeof', 'return', 'printf'}
        
        for match in matches:
            if match not in excluded and not match.isdigit() and len(match) > 1:
                calls.append(match)
                
        return list(set(calls))
    
    def _calculate_complexity(self, code: str) -> int:
        """计算复杂度"""
        complexity = 1
        control_keywords = ['if', 'else', 'while', 'for', 'switch', 'case', 'do']
        for keyword in control_keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', code))
        
        # 额外复杂度因子
        complexity += len(re.findall(r'goto', code)) * 2
        complexity += len(re.findall(r'&&|\|\|', code))
        
        return complexity 