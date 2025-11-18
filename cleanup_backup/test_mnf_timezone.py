import sys
sys.path.append('utils')
from timezone_utils import convert_to_ast
from datetime import datetime

mnf_time = datetime(2025, 10, 20, 20, 15)
ast_time = convert_to_ast(mnf_time)
print(f'MNF ET: {mnf_time.strftime("%A %I:%M %p")}')
print(f'MNF AST: {ast_time.strftime("%A %I:%M %p")}')
print('SUCCESS!' if ast_time.strftime('%A') == 'Monday' else 'FAILED')