import subprocess
import json

OUTPUT_FILE = rf""

def get_installed_packages():
    # 执行pip list命令并获取输出
    pip_list_output = subprocess.check_output(['pip', 'list', '--format=json']).decode('utf-8')
    # 解析json格式的输出
    package_info = [line for line in pip_list_output.splitlines() if line]
    packages = [json.loads(package) for package in package_info][0]
    # 提取包名和版本
    package_dict = {package['name']: package['version'] for package in packages}
    return package_dict

# # 使用函数
output_content = []
packages = get_installed_packages()
for package, version in packages.items():
    print(f"{package}: {version}")
    output_content.append(f"{package}=={version}\n")

with open(OUTPUT_FILE, mode='w+') as f:
    f.writelines(output_content)