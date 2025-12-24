"""
DOMjudge 题目压缩包生成器
根据用户上传的题面和测试数据生成符合DOMjudge格式的题目压缩包
"""

import os
import re
import tempfile
import zipfile
import io
from typing import Dict, List, Tuple, Optional
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


class ProblemGenerator:
    """DOMjudge 题目压缩包生成器"""
    
    def __init__(self):
        self.default_timelimit = 1.0  # 1000ms = 1.0s
        self.default_memory = 128     # 128MB
    
    def extract_info_from_pdf(self, pdf_content: bytes) -> Dict[str, Optional[str]]:
        """
        从PDF中提取题目信息
        
        Args:
            pdf_content: PDF文件的二进制内容
            
        Returns:
            包含题目名称、时间限制、空间限制的字典
        """
        if not PDF_SUPPORT:
            return {
                'name': None,
                'timelimit': None,
                'memory': None
            }
        
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # 提取所有页面的文本
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text()
            
            # 解析题目信息
            info = self._parse_problem_info(full_text)
            return info
            
        except Exception as e:
            print(f"PDF解析失败: {e}")
            return {
                'name': None,
                'timelimit': None,
                'memory': None
            }
    
    def _parse_problem_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        解析题目文本信息
        
        Args:
            text: PDF提取的文本内容
            
        Returns:
            解析出的题目信息
        """
        info = {
            'name': None,
            'timelimit': None,
            'memory': None
        }
        
        # 清理文本
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 尝试提取题目名称 (通常在开头或标题位置)
        name_patterns = [
            r'(?:题目|问题|Problem|Title)(?:名称|标题)?[：:]\s*([^\n\r]+)',
            r'^([A-Z][^.!?]*(?:[.!?]|$))',  # 首行可能是标题
            r'(\b[A-Z][a-zA-Z\s]*Problem\b)',  # 包含Problem的标题
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if len(name) > 3 and len(name) < 100:  # 合理的标题长度
                    info['name'] = name
                    break
        
        # 提取时间限制
        time_patterns = [
            r'时间限制[：:]?\s*(\d+)\s*(?:ms|毫秒|秒)',
            r'Time\s+Limit[：:]?\s*(\d+)\s*(?:ms|second|sec)',
            r'时间[：:]?\s*(\d+)\s*(?:ms|毫秒)',
            r'限时[：:]?\s*(\d+)\s*(?:ms|毫秒|秒)',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                time_val = int(match.group(1))
                # 转换为秒
                if time_val > 100:  # 假设大于100的是毫秒
                    info['timelimit'] = time_val / 1000.0
                else:
                    info['timelimit'] = float(time_val)
                break
        
        # 提取内存限制
        memory_patterns = [
            r'内存限制[：:]?\s*(\d+)\s*(?:MB|mb|兆)',
            r'Memory\s+Limit[：:]?\s*(\d+)\s*(?:MB|mb)',
            r'内存[：:]?\s*(\d+)\s*(?:MB|mb|兆)',
            r'空间限制[：:]?\s*(\d+)\s*(?:MB|mb|兆)',
        ]
        
        for pattern in memory_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['memory'] = int(match.group(1))
                break
        
        return info
    
    def parse_test_data(self, uploaded_files: List[Tuple[str, bytes]]) -> Dict[str, List[Tuple[str, bytes]]]:
        """
        解析上传的测试数据文件
        
        Args:
            uploaded_files: 上传文件列表，格式为 [(filename, content), ...]
            
        Returns:
            分类后的测试数据：{'secret': [...], 'sample': [...]}
        """
        data = {
            'secret': [],
            'sample': []
        }
        
        # 按文件名分类
        for filename, content in uploaded_files:
            filename_lower = filename.lower()
            
            if 'sample' in filename_lower or 'example' in filename_lower:
                data['sample'].append((filename, content))
            else:
                data['secret'].append((filename, content))
        
        # 对文件进行配对处理 (.in 和 .ans/.out)
        data['secret'] = self._pair_test_files(data['secret'])
        data['sample'] = self._pair_test_files(data['sample'])
        
        return data
    
    def _pair_test_files(self, files: List[Tuple[str, bytes]]) -> List[Tuple[str, bytes]]:
        """
        将测试数据文件进行配对处理
        
        Args:
            files: 文件列表
            
        Returns:
            配对后的文件列表
        """
        input_files = {}
        output_files = {}
        
        for filename, content in files:
            base_name = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in ['.in', '.input']:
                input_files[base_name] = content
            elif ext in ['.ans', '.out', '.output']:
                output_files[base_name] = content
        
        # 配对文件
        paired_files = []
        for base_name in sorted(input_files.keys()):
            if base_name in output_files:
                paired_files.append((f"{base_name}.in", input_files[base_name]))
                paired_files.append((f"{base_name}.ans", output_files[base_name]))
        
        return paired_files
    
    def generate_config_files(self, problem_info: Dict) -> Dict[str, str]:
        """
        生成配置文件内容
        
        Args:
            problem_info: 题目信息
            
        Returns:
            配置文件内容字典
        """
        # domjudge-problem.ini
        timelimit = problem_info.get('timelimit', self.default_timelimit)
        color = problem_info.get('color', '')
        
        ini_content = f"""[problem]
timelimit = {timelimit}"""
        
        if color:
            ini_content += f"\ncolor = '{color}'"
        
        # problem.yaml
        name = problem_info.get('name', 'Untitled Problem')
        memory = problem_info.get('memory', self.default_memory)
        
        yaml_content = f"""name: '{name}'
limits:
  memory: {memory}"""
        
        return {
            'domjudge-problem.ini': ini_content,
            'problem.yaml': yaml_content
        }
    
    def create_problem_package(self, problem_info: Dict, pdf_content: bytes, 
                             test_data: Dict[str, List[Tuple[str, bytes]]]) -> bytes:
        """
        创建题目压缩包
        
        Args:
            problem_info: 题目信息
            pdf_content: PDF文件内容
            test_data: 测试数据
            
        Returns:
            压缩包的二进制内容
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 添加PDF文件
            zip_file.writestr('problem.pdf', pdf_content)
            
            # 添加配置文件
            config_files = self.generate_config_files(problem_info)
            for filename, content in config_files.items():
                zip_file.writestr(filename, content)
            
            # 添加测试数据
            # 正式测试数据
            if test_data['secret']:
                for i, (filename, content) in enumerate(test_data['secret']):
                    # 重新编号
                    if filename.endswith('.in'):
                        new_filename = f"data/secret/{(i//2)+1}.in"
                    elif filename.endswith('.ans'):
                        new_filename = f"data/secret/{(i//2)+1}.ans"
                    else:
                        new_filename = f"data/secret/{filename}"
                    
                    zip_file.writestr(new_filename, content)
            
            # 样例数据
            if test_data['sample']:
                for filename, content in test_data['sample']:
                    zip_file.writestr(f"data/sample/{filename}", content)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()


def validate_problem_info(problem_info: Dict) -> List[str]:
    """
    验证题目信息的完整性
    
    Args:
        problem_info: 题目信息字典
        
    Returns:
        错误信息列表
    """
    errors = []
    
    if not problem_info.get('name'):
        errors.append("题目名称不能为空")
    
    timelimit = problem_info.get('timelimit')
    if timelimit is None:
        errors.append("时间限制未设置")
    elif not isinstance(timelimit, (int, float)) or timelimit <= 0:
        errors.append("时间限制必须是大于0的数字")
    
    memory = problem_info.get('memory')
    if memory is None:
        errors.append("内存限制未设置")
    elif not isinstance(memory, int) or memory <= 0:
        errors.append("内存限制必须是大于0的整数")
    
    return errors


if __name__ == '__main__':
    # 测试代码
    generator = ProblemGenerator()
    
    # 测试PDF解析
    test_text = """
    A + B Problem
    时间限制: 1000ms
    内存限制: 256MB
    给定两个整数A和B，求A+B的值。
    """
    
    info = generator._parse_problem_info(test_text)
    print("解析结果:", info)
