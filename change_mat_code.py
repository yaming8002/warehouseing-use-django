import os

def replace_in_files(directory, replacements):
    modified_files = []

    # 遍歷目標資料夾
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") or file.endswith(".html"):
                file_path = os.path.join(root, file)

                try:
                    # 讀取文件內容
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    print(f"Error reading {file_path}, skipping.")
                    continue

                # 替換內容
                original_content = content
                for key, value in replacements.items():
                    content = content.replace(key, value)

                # 如果有修改，寫回文件並記錄
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    modified_files.append(file_path)

    return modified_files

# 例子: 對照字典
replacements = {
      'm_102':'m_102',
      'm_170':'m_170',
      'm_18':'m_18',
      'm_19':'m_19',
      'm_193':'m_193',
      'm_1931':'m_265',
      'm_295':'m_295',
      'm_424':'m_424',
      'm_400':'m_424',
      'm_352':'m_352',
      'm_358':'m_358',
      'm_367':'m_367'
    # 可以添加更多鍵值對
}

# 設定目標資料夾
directory = "F:/Django/kuokuang/warehousing_server"

# 執行替換並獲取修改的文件列表
modified_files = replace_in_files(directory, replacements)

# 列出所有修改的文件
if modified_files:
    print("以下文件已修改：")
    for file in modified_files:
        print(file)
else:
    print("未找到需要修改的文件。")
