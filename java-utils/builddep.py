#
# Copyright (c) 2014, Red Hat, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of Red Hat nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors:  Stanislav Ochotnicky <sochotnicky@redhat.com>

import optparse
import sys

from javapackages.maven.artifact import (Artifact, ArtifactFormatException,
                                         ArtifactValidationException)
from javapackages.common.util import args_to_unicode
from javapackages.common.exception import JavaPackagesToolsException

from lxml import etree


class SaneParser(optparse.OptionParser):
    def format_epilog(self, formatter):
        return self.epilog

usage = "usage: %prog [options] <builddep file>"
epilog = """
%prog generates RPM requires from builddep file generated by XMvn during package build
"""

if __name__ == "__main__":
    parser = SaneParser(usage=usage,
                        epilog=epilog)
    sys.argv = args_to_unicode(sys.argv)

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Exactly 1 argument is required")

    try:
        et = etree.parse(args[0]).getroot()
        deps = et.findall('./dependency')
        for dep in deps:
            art = Artifact.from_xml_element(dep)
            print(art.get_rpm_str(art.version))
    except (ArtifactValidationException, ArtifactFormatException) as e:
        parser.error("{e}: Provided artifact strings were invalid. "
                     "Please see help  and check your arguments".format(e=e))
        sys.exit(1)
    except JavaPackagesToolsException as e:
        sys.exit(e)
