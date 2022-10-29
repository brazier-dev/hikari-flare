import os
import platform
import sys

import hikari

import flare

# Support color on Windows
if sys.platform == "win32":
    import colorama

    colorama.init()


BLUE = "\x1b[34m"
WHITE = "\x1b[37m"

uname = platform.uname()
system_details = f"{uname.system} {uname.machine} ({uname.node}) - {uname.release}"
python_details = f"{platform.python_implementation()} {platform.python_version()} ({platform.python_compiler()})"

sys.stderr.write(
    f"""{BLUE}hikari-flare - package information
{WHITE}----------------------------------
{BLUE}Flare version: {WHITE}{flare.__version__}
{BLUE}Install path: {WHITE}{os.path.abspath(os.path.dirname(__file__))}
{BLUE}Hikari version: {WHITE}{hikari.__version__}
{BLUE}Install path: {WHITE}{os.path.abspath(os.path.dirname(hikari.__file__))}
{BLUE}Python: {WHITE}{python_details}
{BLUE}System: {WHITE}{system_details}\n\n"""
)

# MIT License
#
# Copyright (c) 2022-present HyperGH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
