"""
代码分析器单元测试
"""

import unittest
from src.core.analyzer import CodeAnalyzer


class TestCodeAnalyzer(unittest.TestCase):
    """代码分析器测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.analyzer = CodeAnalyzer()
    
    def test_extract_functions_simple(self):
        """测试简单函数提取"""
        code = """
int add(int a, int b)
{
    return a + b;
}
"""
        functions = self.analyzer.extract_functions(code)
        self.assertEqual(len(functions), 1)
        self.assertEqual(functions[0].name, "add")
    
    def test_calculate_complexity(self):
        """测试复杂度计算"""
        code = """
if (condition) {
    for (int i = 0; i < 10; i++) {
        if (i % 2 == 0) {
            continue;
        }
    }
}
"""
        complexity = self.analyzer._calculate_complexity(code)
        self.assertGreater(complexity, 1)
    
    def test_extract_function_calls(self):
        """测试函数调用提取"""
        code = """
int result = function_a(x);
function_b(y, z);
"""
        calls = self.analyzer._extract_function_calls(code)
        self.assertIn("function_a", calls)
        self.assertIn("function_b", calls)


if __name__ == '__main__':
    unittest.main() 