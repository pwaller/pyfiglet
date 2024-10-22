import os
import subprocess

import pytest


pyfiglet = 'python -m textual_pyfiglet.pyfiglet'
# NOTE: wherever there is {pyfiglet} will get replaced with the above line
# Original test simply called 'pyfiglet'. That is a global install, and we
# want to avoid that.


@pytest.fixture
def test_font_dir():
    swd = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(swd, '..', '..', 'test-fonts'))


def test_strip():
    command = f"{pyfiglet} -f slant -s 0"
    
    expected = '''\
   ____ 
  / __ \\
 / / / /
/ /_/ / 
\\____/
'''

    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    assert result.stdout.decode() == expected
    assert result.returncode == 0


def test_strip_strange_font(test_font_dir):
    install_command = f"{pyfiglet} -L %s/TEST_ONLY.flf " % test_font_dir
    subprocess.run(install_command, shell=True, check=True)

    command = f"{pyfiglet} -f TEST_ONLY -s 0"
    expected = '''\
0000000000  
            
000    000  
            
000    000  
            
000    000  
            
0000000000
'''
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    assert result.stdout.decode() == expected
    assert result.returncode == 0


# normalize is just strip with padding
def test_normalize():
    command = f"{pyfiglet} -f slant -n 0"
    expected = '''\

   ____ 
  / __ \\
 / / / /
/ /_/ / 
\\____/

'''
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    assert result.stdout.decode() == expected
    assert result.returncode == 0
