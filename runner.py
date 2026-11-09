import subprocess
import sys
import os

# 1. 幕僚长（Chief of Staff）定义的扩充任务队列（包含文档生成内容）
PROJECT_TASKS = [
    {
        "id": 1, 
        "name": "新增阶乘函数 factorial(n)", 
        "domain": "math_feature",
        "coder_task": "在 calc.py 中新增 factorial(n) 函数，计算 n 的阶乘，并包含规范的 Docstring",
        "qa_task": "在 test_calc.py 中新增 test_factorial() 测试用例，测试 0、正整数等边界条件",
        "doc_content": "### 1. 阶乘函数 factorial(n)\n- **功能**：计算给定非负整数 $n$ 的阶乘。\n- **参数**：$n$ (int) - 非负整数。\n- **返回值**：(int) 阶乘计算结果。\n\n"
    },
    {
        "id": 2, 
        "name": "新增平方根函数 sqrt(n)", 
        "domain": "math_feature",
        "coder_task": "在 calc.py 中新增 sqrt(n) 函数，计算 n 的平方根，并包含规范的 Docstring",
        "qa_task": "在 test_calc.py 中新增 test_sqrt() 测试用例，测试正常正数、0 以及负数异常边界",
        "doc_content": "### 2. 平方根函数 sqrt(n)\n- **功能**：计算给定数值 $n$ 的平方根。\n- **参数**：$n$ (int/float) - 目标数值。\n- **返回值**：(float) 平方根结果，负数时应抛出 ValueError 异常。\n\n"
    },
    {
        "id": 3, 
        "name": "新增乘方函数 power(base, exp)", 
        "domain": "math_feature",
        "coder_task": "In calc.py 中新增 power(base, exp) 函数，并包含规范的 Docstring",
        "qa_task": "在 test_calc.py 中新增 test_power() 测试用例，覆盖正整、零次方及负数次方",
        "doc_content": "### 3. 乘方函数 power(base, exp)\n- **功能**：计算底数的指定幂次方。\n- **参数**：\n  - `base` (int/float) - 底数。\n  - `exp` (int/float) - 指数。\n- **返回值**：(int/float) 幂运算结果。\n\n"
    }
]

def run_tests():
    """【Tester 执行助手】强验证守门员"""
    result = subprocess.run([sys.executable, "test_calc.py"], capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr

def doc_assistant_generate(task):
    """【Doc 执行助手】由 Python 脚本全自动沉淀 API_DOCS.md"""
    doc_filename = "API_DOCS.md"
    print(f"  📚 [Doc 助手] 正在全自动将 {task['name']} 写入 {doc_filename}...")
    
    # 如果文件不存在，先写入 Markdown 标题头部
    if not os.path.exists(doc_filename):
        with open(doc_filename, "w", encoding="utf-8") as f:
            f.write("# 📐 数学计算库 API 自动生成文档\n\n> 本文档由 1-3-3 AI 矩阵的 **Doc 助手** 在测试通过后自动沉淀。\n\n---\n\n")
    
    # 追加当前任务的文档内容
    with open(doc_filename, "a", encoding="utf-8") as f:
        f.write(task["doc_content"])
    
    print(f"  ✅ {doc_filename} 文档已全自动更新成功！")

def chief_of_staff_dispatch(task):
    """幕僚长全局调度逻辑"""
    print(f"\n========================================")
    print(f"🏛️ [幕僚长] 正在调度任务 [{task['id']}/{len(PROJECT_TASKS)}]: {task['name']}")
    print(f"========================================")
    
    # --- 1. 开发经理派发 Coder 助手 ---
    print(f"\n  👨‍💻 [开发经理] 指挥 【Coder 助手】 执行:")
    print(f"     👉 指令: \"{task['coder_task']}\"")
    input("  请在 Cursor Agent 中发送该指令修改 calc.py，完成后按 Enter 键继续...")
    
    # --- 2. QA 经理派发 Tester 助手 ---
    print(f"\n  🕵️ [QA 经理] 指挥 【Tester 助手】 执行:")
    print(f"     👉 指令: \"{task['qa_task']}\"")
    input("  请在 Cursor Agent 中发送该指令补充 test_calc.py，完成后按 Enter 键继续...")
    
    # --- 3. 规约经理触发强验证 ---
    print(f"\n  🔍 [规约经理] 启动全自动化质量守门强验证...")
    passed, output = run_tests()
    
    if not passed:
        print(f"  ❌ 任务 #{task['id']} 强验证失败，流水线拦截:\n{output.strip()}")
        return False
    
    print(f"  ✅ 任务 #{task['id']} 强验证通过！")
    
    # --- 4. 运维/文档经理派发 Doc 助手（全自动写入，无需手动按回车） ---
    doc_assistant_generate(task)
    
    return True

def main():
    print("=== 1-3-3 AI 智能体【全自动文档沉淀流水线】启动 ===")
    success_count = 0
    
    for task in PROJECT_TASKS:
        success = chief_of_staff_dispatch(task)
        if not success:
            print(f"\n⚠️ 流水线在任务 #{task['id']} 处中断，停止后续任务。")
            break
        success_count += 1

    print(f"\n=== 流水线处理完成：成功通关并全自动沉淀文档 {success_count}/{len(PROJECT_TASKS)} 个任务 ===")

if __name__ == "__main__":
    main()