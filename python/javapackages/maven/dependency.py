#
# Copyright (c) 2014, Red Hat, Inc.
#
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
# 3. Neither the name of the Red Hat nor the names of its
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
# Authors:  Michal Srb <msrb@redhat.com>

from javapackages.maven.artifact import (AbstractArtifact,
                                         ArtifactFormatException)
from javapackages.maven.exclusion import Exclusion
import javapackages.maven.pomreader as POMReader
from lxml.etree import Element, SubElement


class Dependency(AbstractArtifact):

    def __init__(self, groupId, artifactId, extension="", classifier="",
                 version="", scope="", optional="", exclusions=set()):
        # groupId and artifactId are mandatory
        if groupId is not None:
            self.groupId = groupId.strip()
        if artifactId is not None:
            self.artifactId = artifactId.strip()

        if not self.groupId or not self.artifactId:
            raise ArtifactFormatException("\"{g}:{a}\" is not a valid artifact"
                                          .format(g=self.groupId,
                                                  a=self.artifactId))

        # default values
        self.extension = "jar"
        self.classifier = ""
        self.version = ""
        self.scope = "compile"
        self.optional = "false"
        self.exclusions = set()

        self._default_scope = True
        self._default_optional = True

        # raw values
        # TODO: probably not needed anymore
        self._raw_scope = scope
        self._raw_optional = optional

        if extension:
            self.extension = extension.strip()
        if classifier:
            self.classifier = classifier.strip()
        if version:
            self.version = version.strip()
        if scope is not None:
            self.scope = scope.strip()
            self._default_scope = False
        if optional is not None:
            self.optional = optional.strip()
            self._default_optional = False
        if exclusions:
            self.exclusions = exclusions

    def is_optional(self):
        if self.optional and self.optional.lower() == "true":
            return True
        return False

    def get_raw_optional(self):
        """Return original value for 'optional' element."""
        return self._raw_optional

    def get_raw_scope(self):
        """Return original value for 'scope' element."""
        return self._raw_scope

    def get_xml_element(self, root="dependency"):
        """Return XML Element node representation of this dependency."""
        root = AbstractArtifact.get_xml_element(self, root)

        if self._raw_scope:
            item = SubElement(root, "scope")
            item.text = self._raw_scope

        if self._raw_optional is not None:
            item = SubElement(root, "optional")
            item.text = self._raw_optional

        if self.exclusions:
            exc_root = Element("exclusions")
            for e in self.exclusions:
                exc_root.insert(len(exc_root), e.get_xml_element())
            root.insert(len(root), exc_root)

        return root

    @classmethod
    def from_xml_element(cls, xmlnode):
        """
        Create Dependency from xml.etree.ElementTree.Element as contained
        within pom.xml.
        """

        parts = {'groupId': '',
                 'artifactId': '',
                 'type': '',
                 'classifier': '',
                 'version': '',
                 'scope': '',
                 'optional': ''}

        parts = POMReader.find_raw_parts(xmlnode, parts)

        # exclusions
        excnodes = xmlnode.findall("{*}exclusions/{*}exclusion")

        exclusions = set()
        for e in [Exclusion.from_xml_element(x) for x in excnodes]:
            exclusions.add(e)

        return cls(parts['groupId'],
                   parts['artifactId'],
                   extension=parts['type'],
                   classifier=parts['classifier'],
                   version=parts['version'],
                   scope=parts['scope'],
                   optional=parts['optional'],
                   exclusions=exclusions)

    @classmethod
    def from_mvn_str(cls, mvnstr):
        """
        Create Dependency from Maven-style definition.

        The string should be in the format of:
           groupId:artifactId[:extension[:classifier]][:version]

        Where last part is always considered to be version unless empty.
        """
        p = cls.get_parts_from_mvn_str(mvnstr)
        return cls(p['groupId'],
                   p['artifactId'],
                   extension=p['extension'],
                   classifier=p['classifier'],
                   version=p['version'])
