import os
import subprocess

import pytest

import pyfiglet


@pytest.fixture
def test_font_dir():
    swd = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(swd, '..', '..', 'test-fonts'))


def test_strip():
    command = "pyfiglet -f slant -s 0"
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


def test_strip_strange_font(test_font_dir):
    install_command = "pyfiglet -L %s/TEST_ONLY.flf " % test_font_dir
    subprocess.run(install_command, shell=True, check=True)

    command = "pyfiglet -f TEST_ONLY -s 0"
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


def test_font_directories_are_searched(test_font_dir, monkeypatch):
    monkeypatch.setattr(pyfiglet, "FONT_DIRECTORIES", (test_font_dir,))

    assert "TEST_ONLY" in pyfiglet.FigletFont.getFonts()
    rendered = pyfiglet.Figlet(font="TEST_ONLY").renderText("0")
    assert "0000000000" in rendered


# normalize is just strip with padding
def test_normalize():
    command = "pyfiglet -f slant -n 0"
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
