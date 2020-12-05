#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the end-to-end tests script files writer."""

from __future__ import unicode_literals

import unittest

from l2tdevtools import dependencies
from l2tdevtools.dependency_writers import jenkins_scripts
from l2tdevtools.helpers import project
from tests import test_lib


class LinuxRunEndToEndTestsScriptWriterTest(test_lib.BaseTestCase):
  """Tests the Linux run end-to-end test script file writer."""

  def testInitialize(self):
    """Tests the __init__ function."""
    l2tdevtools_path = '/fake/l2tdevtools/'
    project_definition = project.ProjectHelper(l2tdevtools_path)
    dependencies_file = self._GetTestFilePath(['dependencies.ini'])
    test_dependencies_file = self._GetTestFilePath(['test_dependencies.ini'])
    dependency_helper = dependencies.DependencyHelper(
        dependencies_file=dependencies_file,
        test_dependencies_file=test_dependencies_file)

    writer = jenkins_scripts.LinuxRunEndToEndTestsScriptWriter(
        l2tdevtools_path, project_definition, dependency_helper)
    self.assertIsNotNone(writer)

  # TODO: Add test for the Write method.


class RunPython3EndToEndTestsScriptWriterTest(test_lib.BaseTestCase):
  """Tests the run end-to-end test script file writer."""

  def testInitialize(self):
    """Tests the __init__ function."""
    l2tdevtools_path = '/fake/l2tdevtools/'
    project_definition = project.ProjectHelper(l2tdevtools_path)
    dependencies_file = self._GetTestFilePath(['dependencies.ini'])
    test_dependencies_file = self._GetTestFilePath(['test_dependencies.ini'])
    dependency_helper = dependencies.DependencyHelper(
        dependencies_file=dependencies_file,
        test_dependencies_file=test_dependencies_file)

    writer = jenkins_scripts.RunPython3EndToEndTestsScriptWriter(
        l2tdevtools_path, project_definition, dependency_helper)
    self.assertIsNotNone(writer)

  # TODO: Add test for the Write method.


if __name__ == '__main__':
  unittest.main()
