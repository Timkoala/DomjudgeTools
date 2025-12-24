"""
DOMjudge 账号生成器 Web 应用
提供简单易用的 Web 界面来生成队伍和账号文件
"""
from flask import Flask, render_template, request, send_file, jsonify
import os
import tempfile
from generator import parse_input_file, parse_excel_file, generate_teams_tsv, generate_accounts_tsv
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


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
