import os
import subprocess
import textwrap
import tempfile
import shutil
import re

import pytest

# This part of the test suite is in development, the aim is to find a way to easily test
# a script included in a Python package through pytest.


class TestEnvironment(object):
    def __init__(self, path):
        self.finalize = True
        self.path = path

    def ensure_file_is_present(self, filename, content=""):
        with open(os.path.join(self.path, filename), "w") as f:
            f.write(textwrap.dedent(content))

    def get_file_content(self, filename):
        with open(os.path.join(self.path, filename), "r") as f:
            return f.read()

    def call(self, cmdline, **kwds):
        return subprocess.check_call(cmdline, cwd=self.path, **kwds)

    def output(self, cmdline, **kwds):
        output = subprocess.check_output(cmdline, cwd=self.path, **kwds)
        return output.decode('utf8')

    def compare_output(self, expected_output, cmdline, **kwds):
        output = self.output(cmdline, **kwds)

        clean_expected_output = textwrap.dedent(expected_output)

        for line in clean_expected_output.split(os.linesep):
            reline = re.compile(line)
            l = reline.findall(output)
            assert len(l) > 0


def punch_root():

    return os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir)


def fix_os_path():
    old = os.environ.get("PATH", "")
    scripts_path = os.path.join(punch_root(), "scripts")
    if scripts_path not in old:
        os.environ["PATH"] = ":".join([scripts_path, old])


@pytest.fixture
def test_environment(request):
    tempdir = tempfile.mkdtemp()

    fix_os_path()

    te = TestEnvironment(tempdir)

    def fin():
        if te.finalize:
            shutil.rmtree(tempdir, ignore_errors=True)

    request.addfinalizer(fin)
    return te

