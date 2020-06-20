# -*- coding: utf-8 -*-
"""Writers for Travis-CI script files."""

from __future__ import unicode_literals

import io
import os

from l2tdevtools.dependency_writers import interface


class TravisInstallScriptWriter(interface.DependencyFileWriter):
  """Travis-CI install.sh file writer."""

  PATH = os.path.join('config', 'travis', 'install.sh')

  # Maps source directory names to project names.
  _SOURCE_DIRECTORY_MAPPINGS = {
      'esedbrc': 'esedb-kb',
      'winevtrc': 'winevt-kb',
      'winregrc': 'winreg-kb',
  }

  _TEMPLATE_FILE = os.path.join('data', 'templates', 'install.sh')

  _URL_L2TDEVTOOLS = 'https://github.com/log2timeline/l2tdevtools.git'

  def Write(self):
    """Writes an install.sh file."""
    dpkg_build_dependencies = ['build-essential']

    dpkg_python3_dependencies = self._GetDPKGPythonDependencies(
        python_version=3)

    dpkg_python3_test_dependencies = self._GetDPKGTestDependencies(
        dpkg_python3_dependencies, python_version=3)

    rpm_python3_dependencies = self._GetRPMPythonDependencies(python_version=3)

    rpm_python3_test_dependencies = self._GetRPMTestDependencies(
        rpm_python3_dependencies, python_version=3)

    source_directory = self._SOURCE_DIRECTORY_MAPPINGS.get(
        self._project_definition.name, self._project_definition.name)

    template_mappings = {
        'dpkg_build_dependencies': ' '.join(dpkg_build_dependencies),
        'dpkg_python3_dependencies': ' '.join(dpkg_python3_dependencies),
        'dpkg_python3_test_dependencies': ' '.join(
            dpkg_python3_test_dependencies),
        'rpm_python3_dependencies': ' '.join(rpm_python3_dependencies),
        'rpm_python3_test_dependencies': ' '.join(
            rpm_python3_test_dependencies),
        'source_directory': source_directory}

    template_file = os.path.join(self._l2tdevtools_path, self._TEMPLATE_FILE)
    file_content = self._GenerateFromTemplate(template_file, template_mappings)

    with io.open(self.PATH, 'w', encoding='utf-8') as file_object:
      file_object.write(file_content)


class TravisRunPython3ScriptWriter(interface.DependencyFileWriter):
  """Travis-CI run_python3.sh file writer."""

  _TEMPLATE_FILE = os.path.join('data', 'templates', 'run_python3.sh')

  PATH = os.path.join('config', 'travis', 'run_python3.sh')

  def Write(self):
    """Writes a run_python3.sh file."""
    template_mappings = {}

    template_file = os.path.join(self._l2tdevtools_path, self._TEMPLATE_FILE)
    file_content = self._GenerateFromTemplate(template_file, template_mappings)

    with io.open(self.PATH, 'w', encoding='utf-8') as file_object:
      file_object.write(file_content)


class TravisRunTestsScriptWriter(interface.DependencyFileWriter):
  """Travis-CI runtests.sh file writer."""

  PATH = os.path.join('config', 'travis', 'runtests.sh')

  # Maps source directory names to project names.
  _SOURCE_DIRECTORY_MAPPINGS = {
      'esedbrc': 'esedb-kb',
      'winevtrc': 'winevt-kb',
      'winregrc': 'winreg-kb',
  }

  _TEMPLATE_FILE = os.path.join('data', 'templates', 'runtests.sh')

  def Write(self):
    """Writes a runtests.sh file."""
    source_directory = self._SOURCE_DIRECTORY_MAPPINGS.get(
        self._project_definition.name, self._project_definition.name)

    template_mappings = {'source_directory': source_directory}

    template_file = os.path.join(self._l2tdevtools_path, self._TEMPLATE_FILE)
    file_content = self._GenerateFromTemplate(template_file, template_mappings)

    with io.open(self.PATH, 'w', encoding='utf-8') as file_object:
      file_object.write(file_content)


class TravisRunWithTimeoutScriptWriter(interface.DependencyFileWriter):
  """Travis-CI run_with_timeout.sh file writer."""

  _TEMPLATE_FILE = os.path.join('data', 'templates', 'run_with_timeout.sh')

  PATH = os.path.join('config', 'travis', 'run_with_timeout.sh')

  def Write(self):
    """Writes a run_with_timeout.sh file."""
    template_mappings = {}

    template_file = os.path.join(self._l2tdevtools_path, self._TEMPLATE_FILE)
    file_content = self._GenerateFromTemplate(template_file, template_mappings)

    with io.open(self.PATH, 'w', encoding='utf-8') as file_object:
      file_object.write(file_content)
