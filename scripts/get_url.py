import subprocess
import yaml


def extract_url(notebook_name):
    cmd = [
        'oc',
        'get',
        'notebook',
        notebook_name,
        '-o',
        'yaml',
        '-n',
        'rhods-notebooks',
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Error getting YAML for notebook {notebook_name}:', result.stderr)
        return None
    data = yaml.safe_load(result.stdout)
    url = data.get('metadata', {}).get('annotations', {}).get('opendatahub.io/link')
    return url


notebook_name = input('Enter the notebook name: ')
url = extract_url(notebook_name)

if url:
    print(f'URL for notebook {notebook_name}: {url}')
else:
    print(f'No URL found for notebook {notebook_name}')
