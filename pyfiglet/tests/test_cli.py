import os

import pytest
import subprocess32


@pytest.fixture
def test_font_dir():
    swd = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(swd, '..', '..', 'test-fonts'))


def test_strip():
    command = "pyfiglet -f doh -s 0"
    expected = '''\
     000000000     
   00:::::::::00   
 00:::::::::::::00 
0:::::::000:::::::0
0::::::0   0::::::0
0:::::0     0:::::0
0:::::0     0:::::0
0:::::0 000 0:::::0
0:::::0 000 0:::::0
0:::::0     0:::::0
0:::::0     0:::::0
0::::::0   0::::::0
0:::::::000:::::::0
 00:::::::::::::00 
   00:::::::::00   
     000000000
'''
    result = subprocess32.run(command, shell=True, stdout=subprocess32.PIPE)
    assert result.stdout.decode() == expected
    assert result.returncode == 0


def test_strip_strange_font(test_font_dir):
    install_command = "pyfiglet -L %s/TEST_ONLY.flf " % test_font_dir
    subprocess32.run(install_command, shell=True, check=True)

    command = "pyfiglet -f TEST_ONLY -s 0"
    expected = '''\
0000000000  
            
000    000  
            
000    000  
            
000    000  
            
0000000000
'''
    result = subprocess32.run(command, shell=True, stdout=subprocess32.PIPE)
    assert result.stdout.decode() == expected
    assert result.returncode == 0


# normalize is just strip with padding
def test_normalize():
    command = "pyfiglet -f doh -n 0"
    expected = '''\

     000000000     
   00:::::::::00   
 00:::::::::::::00 
0:::::::000:::::::0
0::::::0   0::::::0
0:::::0     0:::::0
0:::::0     0:::::0
0:::::0 000 0:::::0
0:::::0 000 0:::::0
0:::::0     0:::::0
0:::::0     0:::::0
0::::::0   0::::::0
0:::::::000:::::::0
 00:::::::::::::00 
   00:::::::::00   
     000000000

'''
    result = subprocess32.run(command, shell=True, stdout=subprocess32.PIPE)
    assert result.stdout.decode() == expected
    assert result.returncode == 0
