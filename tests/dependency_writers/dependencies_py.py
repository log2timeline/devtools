#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the dependencies.py writer."""

import unittest

from l2tdevtools import dependencies
from l2tdevtools.dependency_writers import dependencies_py
from l2tdevtools.helpers import project
from tests import test_lib


class DependenciesPyWriterTest(test_lib.BaseTestCase):
  """Tests the dependencies.py writer."""

  def testInitialize(self):
    """Tests that the writer can be initialized."""

    l2tdevtools_path = '/fake/l2tdevtools/'
    project_definition = project.ProjectHelper(l2tdevtools_path)
    dependencies_file = self._GetTestFilePath(['dependencies.ini'])
    test_dependencies_file = self._GetTestFilePath(['test_dependencies.ini'])
    dependency_helper = dependencies.DependencyHelper(
        dependencies_file=dependencies_file,
        test_dependencies_file=test_dependencies_file)

    writer = dependencies_py.DependenciesPyWriter(
        l2tdevtools_path, project_definition, dependency_helper)
    self.assertIsNotNone(writer)

  # TODO: Add test for the Write method.


if __name__ == '__main__':
  unittest.main()
