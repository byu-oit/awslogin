import subprocess
import os

os.environ['TESTING'] = 'it worked!'
print(os.environ['PS1'])
os.environ['PS1'] = '(hello) ' + os.environ['PS1']

subprocess.call(['/bin/bash', '--norc'])
#proc = subprocess.Popen('/bin/bash', stdout=subprocess.PIPE, env={'BLASTDB': '/path/to/directory'})
