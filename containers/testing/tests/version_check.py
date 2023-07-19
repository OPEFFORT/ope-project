import re
import sys

if len(sys.argv) <= 2:
    print("Invalid number of arguments")
    sys.exit(1)

pip_list_output_file= sys.argv[1]
pip_list_text= sys.argv[2]

versions = set()

# Extract versions from the pip list output
for line in pip_list_text.split('\n'):
    match = re.search(r'\d+\.\d+(\.\d+)?', line)
    if match:
        versions.add(match.group())

# Read the pip list output file
with open(pip_list_output_file, 'r') as file:
    file_content = file.read()

# Compare versions
mismatched_versions = []
for version in versions:
    if version not in file_content:
        mismatched_versions.append(version)

if not mismatched_versions:
    result = "All versions are matching."
else:
    result = "Versions not matching:"
    for version in mismatched_versions:
        result += f"\n{version}"

print(result)

