import distutils
from distutils import dir_util
from distutils import file_util

import sys

p = None

if len(sys.argv) > 1:
    print(sys.argv[1:])
    p = sys.argv[1]

name = "WoxTodoistInt"

if p is None:
    distutils.dir_util.copy_tree(f"C:\\Projects\\{name}", f"C:\\Users\\g\\AppData\\Roaming\\Wox\\Plugins\\{name}", preserve_mode=0)
else:
    distutils.file_util.copy_file(f"C:\\Projects\\{name}\\main.py", f"C:\\Users\\g\\AppData\\Roaming\\Wox\\Plugins\\{name}\\main.py", preserve_mode=0)