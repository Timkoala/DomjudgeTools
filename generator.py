"""
DOMjudge 账号生成器
根据输入的学号和姓名生成队伍文件(teams.tsv)和账号文件(accounts.tsv)
"""
import random
import os
try:
    import pandas as pd
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False


def generate_password():
    """生成8位纯数字不含零的密码"""
    digits = '123456789'
    return ''.join(random.choice(digits) for _ in range(8))


def generate_team_id(student_id):
    """根据学号生成队伍ID"""
    return f"GXU{student_id}"


def parse_excel_file(file_path):
    """解析 Excel 文件"""
    if not EXCEL_SUPPORT:
        raise ValueError("未安装 pandas 和 openpyxl，无法处理 Excel 文件。请运行: pip install pandas openpyxl")
    
    try:
        # 读取 Excel 文件，只读前两列
        df = pd.read_excel(file_path, usecols=[0, 1], header=None)
        students = []
        
        for index, row in df.iterrows():
            if pd.notna(row[0]) and pd.notna(row[1]):
                student_id = str(row[0]).strip()
                name = str(row[1]).strip()
                if student_id and name:
                    students.append((student_id, name))
        
        return students
    except Exception as e:
        raise ValueError(f"解析 Excel 文件失败: {str(e)}")


def parse_input_file(input_content):
    """解析输入文件内容"""
    students = []
    lines = input_content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) >= 2:
            student_id = parts[0].strip()
            name = parts[1].strip()
            students.append((student_id, name))
    
    return students


def generate_teams_tsv(students, category='3'):
    """
    生成队伍文件内容
    格式: 学号\t队伍ID\t类别\t姓名\t\t\t\t
    """
    lines = ['teams\t1']
    
    for student_id, name in students:
        team_id = generate_team_id(student_id)
        # 前四项: 学号、队伍ID、类别、姓名，后面保留4个tab
        line = f"{student_id}\t{team_id}\t{category}\t{name}\t\t\t\t"
        lines.append(line)
    
    return '\n'.join(lines)


def generate_accounts_tsv(students):
    """
    生成账号文件内容
    格式: team\t姓名\t学号\t密码
    """
    lines = ['accounts\t1\t\t']
    
    for student_id, name in students:
        password = generate_password()
        line = f"team\t{name}\t{student_id}\t{password}"
        lines.append(line)
    
    return '\n'.join(lines)


def process_file(input_path, output_dir=None):
    """
    处理输入文件，生成队伍和账号文件
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录，如果为None则使用输入文件所在目录
    
    Returns:
        tuple: (teams_path, accounts_path) 生成的文件路径
    """
    # 读取输入文件
    with open(input_path, 'r', encoding='utf-8') as f:
        input_content = f.read()
    
    # 解析学生信息
    students = parse_input_file(input_content)
    
    if not students:
        raise ValueError("输入文件中没有有效的学生信息")
    
    # 生成文件内容
    teams_content = generate_teams_tsv(students)
    accounts_content = generate_accounts_tsv(students)
    
    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(input_path)
        if not output_dir:  # 如果是当前目录
            output_dir = '.'
    
    if output_dir != '.':
        os.makedirs(output_dir, exist_ok=True)
    
    # 写入文件
    teams_path = os.path.join(output_dir, 'teams.tsv')
    accounts_path = os.path.join(output_dir, 'accounts.tsv')
    
    with open(teams_path, 'w', encoding='utf-8') as f:
        f.write(teams_content)
    
    with open(accounts_path, 'w', encoding='utf-8') as f:
        f.write(accounts_content)
    
    return teams_path, accounts_path


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python generator.py <input_file>")
        print("示例: python generator.py input.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"错误: 文件 {input_file} 不存在")
        sys.exit(1)
    
    try:
        teams_path, accounts_path = process_file(input_file)
        print(f"✓ 成功生成队伍文件: {teams_path}")
        print(f"✓ 成功生成账号文件: {accounts_path}")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
