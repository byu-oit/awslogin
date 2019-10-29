from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library

standard_library.install_aliases()
from builtins import object


class Colors(object):
    normal = "\033[39m"
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    magenta = "\033[35m"
    cyan = "\033[36m"
    lgrey = "\033[37m"
    lred = "\033[91m"
    lgreen = "\033[92m"
    lyellow = "\033[93m"
    lblue = "\033[94m"
    lmagenta = "\033[95m"
    lcyan = "\033[96m"
    white = "\033[97m"
