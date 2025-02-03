import re

input_file = r"C:\CORE FOLDERS\FIPLY2\strip.txt"
output_file = r"C:\CORE FOLDERS\FIPLY2\strip_cleaned.txt"

# Read file content
with open(input_file, "r", encoding="utf-8") as file:
    content = file.read()

# Step 1: Remove triple backticks (```), print confirmation
content = content.replace("```", "")
print("Triple backticks removed.")

# Step 2: Remove all triple-quoted docstrings (""" and ''')
content = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\')', '', content, flags=re.DOTALL)

# Step 3: Remove all single-line comments (lines that start with `#`)
content = re.sub(r'^\s*#.*$', '', content, flags=re.MULTILINE)

# Step 4: Remove extra blank lines left after comment removal
content = re.sub(r'\n\s*\n', '\n', content)

# Write cleaned content to a new file
with open(output_file, "w", encoding="utf-8") as file:
    file.write(content)

print(f"All comments removed. Cleaned file saved as: {output_file}")
