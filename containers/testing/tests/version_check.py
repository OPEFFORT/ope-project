import re
import sys

if len(sys.argv) <= 2:
    print("Invalid number of arguments")
    sys.exit(1)

pip_list_output_file = sys.argv[1]
pip_list_text_file = sys.argv[2]

def extract_package_versions(text):
    package_versions = {}
    for line in text.split('\n'):
        match = re.search(r'([a-zA-Z0-9-_.]+)\s+(\d+\.\d+(\.\d+)?)', line)
        if match:
            package = match.group(1)
            version = match.group(2)
            package_versions[package] = version
    return package_versions

# Read the pip list output from the first file
with open(pip_list_output_file, 'r') as file:
    file_content = file.read()

# Read the versions from the second file
with open(pip_list_text_file, 'r') as file:
    pip_list_text = file.read()

versions1 = extract_package_versions(file_content)
versions2 = extract_package_versions(pip_list_text)

# Compare versions
mismatched_versions = []
for package, version in versions1.items():
    if package in versions2:
        if versions2[package] != version:
            mismatched_versions.append((package, version, versions2[package]))

if not mismatched_versions:
    print("All versions are matching.")
else:
    print("Versions not matching:")
    for package, version1, version2 in mismatched_versions:
        print(f"{package}: {version1} != {version2}")
