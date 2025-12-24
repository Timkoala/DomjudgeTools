"""
DOMjudge 工具集 Web 应用
提供简单易用的 Web 界面来生成队伍和账号文件，以及DomJudge题目包
"""
from flask import Flask, render_template, request, send_file, jsonify
import os
import tempfile
from generator import parse_input_file, parse_excel_file, generate_teams_tsv, generate_accounts_tsv
from problem_generator import ProblemGenerator, validate_problem_info
import io
import zipfile

app = Flask(__name__)


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """处理文件生成请求"""
    try:
        # 获取上传的文件或文本内容
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = file.filename.lower()
            
            # 检查是否为 Excel 文件
            if filename.endswith(('.xlsx', '.xls')):
                # 保存临时文件
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1])
                file.save(temp_file.name)
                temp_file.close()
                
                try:
                    students = parse_excel_file(temp_file.name)
                finally:
                    os.unlink(temp_file.name)  # 删除临时文件
            else:
                # 处理文本文件
                input_content = file.read().decode('utf-8')
                students = parse_input_file(input_content)
                
        elif 'text_input' in request.form and request.form['text_input'].strip():
            input_content = request.form['text_input']
            students = parse_input_file(input_content)
        else:
            return jsonify({'error': '请上传文件或输入文本'}), 400
        
        if not students:
            return jsonify({'error': '没有找到有效的学生信息'}), 400
        
        # 生成文件内容
        teams_content = generate_teams_tsv(students)
        accounts_content = generate_accounts_tsv(students)
        
        # 创建 ZIP 文件
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('teams.tsv', teams_content)
            zip_file.writestr('accounts.tsv', accounts_content)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='domjudge_files.zip'
        )
    
    except Exception as e:
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


@app.route('/preview', methods=['POST'])
def preview():
    """预览生成的内容"""
    try:
        # 获取上传的文件或文本内容
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = file.filename.lower()
            
            # 检查是否为 Excel 文件
            if filename.endswith(('.xlsx', '.xls')):
                # 保存临时文件
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1])
                file.save(temp_file.name)
                temp_file.close()
                
                try:
                    students = parse_excel_file(temp_file.name)
                finally:
                    os.unlink(temp_file.name)  # 删除临时文件
            else:
                # 处理文本文件
                input_content = file.read().decode('utf-8')
                students = parse_input_file(input_content)
                
        elif 'text_input' in request.form and request.form['text_input'].strip():
            input_content = request.form['text_input']
            students = parse_input_file(input_content)
        else:
            return jsonify({'error': '请上传文件或输入文本'}), 400
        
        if not students:
            return jsonify({'error': '没有找到有效的学生信息'}), 400
        
        # 生成文件内容
        teams_content = generate_teams_tsv(students)
        accounts_content = generate_accounts_tsv(students)
        
        return jsonify({
            'success': True,
            'student_count': len(students),
            'teams_preview': '\n'.join(teams_content.split('\n')[:6]),  # 显示前5条
            'accounts_preview': '\n'.join(accounts_content.split('\n')[:6]),
            'teams_full': teams_content,
            'accounts_full': accounts_content
        })
    
    except Exception as e:
        return jsonify({'error': f'预览失败: {str(e)}'}), 500


@app.route('/problem')
def problem():
    """题目包生成页面"""
    return render_template('problem.html')


@app.route('/problem/preview', methods=['POST'])
def problem_preview():
    """预览题目包信息"""
    try:
        generator = ProblemGenerator()
        
        # 获取题面PDF
        if 'problem_pdf' not in request.files:
            return jsonify({'error': '请上传题面PDF文件'}), 400
        
        pdf_file = request.files['problem_pdf']
        if not pdf_file.filename or not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': '请上传有效的PDF文件'}), 400
        
        pdf_content = pdf_file.read()
        
        # 从PDF中提取信息
        extracted_info = generator.extract_info_from_pdf(pdf_content)
        
        # 获取用户输入的信息
        problem_info = {
            'name': request.form.get('problem_name') or extracted_info.get('name'),
            'timelimit': None,
            'memory': None,
            'color': request.form.get('balloon_color', '')
        }
        
        # 处理时间限制
        if request.form.get('time_limit'):
            try:
                problem_info['timelimit'] = float(request.form.get('time_limit')) / 1000.0  # 转换为秒
            except ValueError:
                problem_info['timelimit'] = extracted_info.get('timelimit')
        else:
            problem_info['timelimit'] = extracted_info.get('timelimit')
        
        # 处理内存限制
        if request.form.get('memory_limit'):
            try:
                problem_info['memory'] = int(request.form.get('memory_limit'))
            except ValueError:
                problem_info['memory'] = extracted_info.get('memory')
        else:
            problem_info['memory'] = extracted_info.get('memory')
        
        # 设置默认值
        if problem_info['timelimit'] is None:
            problem_info['timelimit'] = generator.default_timelimit
        if problem_info['memory'] is None:
            problem_info['memory'] = generator.default_memory
        
        # 处理测试数据
        test_files = []
        if 'test_files' in request.files:
            for file in request.files.getlist('test_files'):
                if file.filename:
                    test_files.append((file.filename, file.read()))
        
        test_data = generator.parse_test_data(test_files)
        
        return jsonify({
            'success': True,
            'problem_info': problem_info,
            'extracted_info': extracted_info,
            'test_data_summary': {
                'secret_count': len(test_data['secret']) // 2,  # 输入输出成对
                'sample_count': len(test_data['sample']) // 2,
                'secret_files': [f[0] for f in test_data['secret']],
                'sample_files': [f[0] for f in test_data['sample']]
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'预览失败: {str(e)}'}), 500


@app.route('/problem/generate', methods=['POST'])
def problem_generate():
    """生成题目包"""
    try:
        generator = ProblemGenerator()
        
        # 获取题面PDF
        if 'problem_pdf' not in request.files:
            return jsonify({'error': '请上传题面PDF文件'}), 400
        
        pdf_file = request.files['problem_pdf']
        if not pdf_file.filename or not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': '请上传有效的PDF文件'}), 400
        
        pdf_content = pdf_file.read()
        
        # 从PDF中提取信息
        extracted_info = generator.extract_info_from_pdf(pdf_content)
        
        # 获取用户输入的信息
        problem_info = {
            'name': request.form.get('problem_name') or extracted_info.get('name'),
            'timelimit': None,
            'memory': None,
            'color': request.form.get('balloon_color', '')
        }
        
        # 处理时间限制
        if request.form.get('time_limit'):
            try:
                problem_info['timelimit'] = float(request.form.get('time_limit')) / 1000.0  # 转换为秒
            except ValueError:
                problem_info['timelimit'] = extracted_info.get('timelimit')
        else:
            problem_info['timelimit'] = extracted_info.get('timelimit')
        
        # 处理内存限制
        if request.form.get('memory_limit'):
            try:
                problem_info['memory'] = int(request.form.get('memory_limit'))
            except ValueError:
                problem_info['memory'] = extracted_info.get('memory')
        else:
            problem_info['memory'] = extracted_info.get('memory')
        
        # 设置默认值
        if problem_info['timelimit'] is None:
            problem_info['timelimit'] = generator.default_timelimit
        if problem_info['memory'] is None:
            problem_info['memory'] = generator.default_memory
        
        # 验证题目信息
        errors = validate_problem_info(problem_info)
        if errors:
            return jsonify({'error': '题目信息不完整: ' + '; '.join(errors)}), 400
        
        # 处理测试数据
        test_files = []
        if 'test_files' in request.files:
            for file in request.files.getlist('test_files'):
                if file.filename:
                    test_files.append((file.filename, file.read()))
        
        if not test_files:
            return jsonify({'error': '请上传测试数据文件'}), 400
        
        test_data = generator.parse_test_data(test_files)
        
        if not test_data['secret']:
            return jsonify({'error': '至少需要一组正式测试数据'}), 400
        
        # 生成题目包
        package_content = generator.create_problem_package(
            problem_info, pdf_content, test_data
        )
        
        # 生成文件名
        safe_name = problem_info['name'].replace(' ', '_').replace('/', '_')
        filename = f"{safe_name}_problem.zip"
        
        return send_file(
            io.BytesIO(package_content),
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
