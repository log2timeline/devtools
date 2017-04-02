# -*- coding: utf-8 -*-
"""RPM spec file generator."""

import datetime
import logging
import os
import subprocess
import sys


class RPMSpecFileGenerator(object):
  """Class that helps in generating RPM spec files."""

  _EMAIL_ADDRESS = (
      u'log2timeline development team <log2timeline-dev@googlegroups.com>')

  _DOC_FILENAMES = [
      u'CHANGES', u'CHANGES.txt', u'CHANGES.TXT',
      u'README', u'README.txt', u'README.TXT']

  _LICENSE_FILENAMES = [
      u'LICENSE', u'LICENSE.txt', u'LICENSE.TXT']

  def _GetBuildDefinition(self, python2_only):
    """Retrieves the build definition.

    Args:
      python2_only (bool): True if the spec file should build Python 2
          packages only.

    Returns:
      str: build definition.
    """
    lines = [b'python2 setup.py build']
    if not python2_only:
      lines.append(b'python3 setup.py build')

    return b'\n'.join(lines)

  def _GetDocumentationFilesDefinition(self, source_directory):
    """Retrieves the documentation files definition.

    Args:
      source_directory (str): path of the source directory.

    Returns:
      str: documentation files definition.
    """
    doc_files = []
    for doc_file in self._DOC_FILENAMES:
      doc_file_path = os.path.join(source_directory, doc_file)
      if os.path.exists(doc_file_path):
        doc_files.append(doc_file)

    doc_file_definition = b''
    if doc_files:
      doc_file_definition = b'%doc {0:s}\n'.format(b' '.join(doc_files))

    return doc_file_definition

  def _GetInstallDefinition(self, python2_only):
    """Retrieves the install definition.

    Args:
      python2_only (bool): True if the spec file should build Python 2
          packages only.

    Returns:
      str: install definition.
    """
    lines = [b'python2 setup.py install -O1 --root=%{buildroot}']
    if not python2_only:
      lines.append(b'python3 setup.py install -O1 --root=%{buildroot}')

    lines.append(b'rm -rf %{buildroot}/usr/share/doc/%{name}/')
    lines.append(b'')
    return b'\n'.join(lines)

  def _GetLicenseFileDefinition(self, source_directory):
    """Retrieves the license file definition.

    Args:
      source_directory (str): path of the source directory.

    Returns:
      str: license file definition.
    """
    license_file_definition = b''
    for license_file in self._LICENSE_FILENAMES:
      license_file_path = os.path.join(source_directory, license_file)
      if os.path.exists(license_file_path):
        license_file_definition = b'%license {0:s}\n'.format(license_file)
        break

    return license_file_definition

  def _WriteChangeLog(self, output_file_object, version):
    """Writes the change log.

    Args:
      output_file_object (file): output file-like object to write to.
      version (str): version.
    """
    date_time = datetime.datetime.now()
    date_time_string = date_time.strftime(u'%a %b %e %Y')

    output_file_object.write((
        b'\n'
        b'%changelog\n'
        b'* {0:s} {1:s} {2:s}-1\n'
        b'- Auto-generated\n').format(
            date_time_string, self._EMAIL_ADDRESS, version))

  def _WritePythonPackageDefinition(
      self, output_file_object, summary, requires, description):
    """Writes the Python package definition.

    Args:
      output_file_object (file): output file-like object to write to.
      summary (str): package summary.
      requires (str): package requires definition.
      description (str): package description.
    """
    output_file_object.write((
        b'%package -n python-%{{name}}\n'
        b'{0:s}'
        b'{1:s}'
        b'\n'
        b'%description -n python-%{{name}}\n'
        b'{2:s}').format(summary, requires, description))

  def _WritePythonPackageFiles(
      self, output_file_object, license_line, doc_line, lib_dir):
    """Writes the Python package files.

    Args:
      output_file_object (file): output file-like object to write to.
      license_line (str): line containing the license file definition.
      doc_line (str): line containing the document files definition.
      lib_dir (str): path of the library directory.
    """
    output_file_object.write((
        b'%files -n python-%{{name}}\n'
        b'{0:s}'
        b'{1:s}'
        b'{2:s}/python2*/*\n').format(
            license_line, doc_line, lib_dir))

  def _WritePython3PackageDefinition(
      self, output_file_object, summary, requires, description):
    """Writes the Python 3 package definition.

    Args:
      output_file_object (file): output file-like object to write to.
      summary (str): package summary.
      requires (str): package requires definition.
      description (str): package description.
    """
    output_file_object.write((
        b'%package -n python3-%{{name}}\n'
        b'{0:s}'
        b'{1:s}'
        b'\n'
        b'%description -n python3-%{{name}}\n'
        b'{2:s}').format(summary, requires, description))

  def _WritePython3PackageFiles(
      self, output_file_object, license_line, doc_line, lib_dir):
    """Writes the Python 3 package files.

    Args:
      output_file_object (file): output file-like object to write to.
      license_line (str): line containing the license file definition.
      doc_line (str): line containing the document files definition.
      lib_dir (str): path of the library directory.
    """
    output_file_object.write((
        b'\n'
        b'%files -n python3-%{{name}}\n'
        b'{0:s}'
        b'{1:s}'
        b'{2:s}/python3*/*\n').format(
            license_line, doc_line, lib_dir))

  def GenerateWithSetupPy(self, source_directory, build_log_file):
    """Generates the RPM spec file with setup.py.

    Args:
      source_directory (str): path of the source directory.
      build_log_file (str): path of the build log file.

    Returns:
      bool: True if successful, False otherwise.
    """
    command = u'{0:s} setup.py bdist_rpm --spec-only >> {1:s} 2>&1'.format(
        sys.executable, build_log_file)
    exit_code = subprocess.call(u'(cd {0:s} && {1:s})'.format(
        source_directory, command), shell=True)
    if exit_code != 0:
      logging.error(u'Running: "{0:s}" failed.'.format(command))
      return False

    return True

  def _RewriteSetupPyGeneratedFile(
      self, project_definition, source_directory, source_filename,
      project_name, rpm_build_dependencies, input_file, output_file_object):
    """Rewrites the RPM spec file generated with setup.py.

    Args:
      project_definition (ProjectDefinition): project definition.
      source_directory (str): path of the source directory.
      source_filename (str): name of the source package.
      project_name (str): name of the project.
      rpm_build_dependencies (list[str]): RPM build dependencies.
      input_file (str): path of the input RPM spec file.
      output_file_object (file): output file-like object to write to.

    Returns:
      bool: True if successful, False otherwise.
    """
    description = b''
    requires = b''
    summary = b''
    version = b''

    in_description = False
    has_build_requires = False
    has_python_package = False
    has_python3_package = False

    python2_only = project_definition.IsPython2Only()

    with open(input_file, 'r+b') as input_file_object:
      for line in input_file_object.readlines():
        if line.startswith(b'%') and in_description:
          in_description = False

          if project_definition.description_long:
            description = u'{0:s}\n\n'.format(
                project_definition.description_long)

          output_file_object.write(description)

        if line.startswith(b'%define name '):
          # Need to override the project name for projects that prefix
          # their name with "python-" in setup.py but do not use it
          # for their source package name.
          line = b'%define name {0:s}\n'.format(project_name)

        elif line.startswith(b'%define version '):
          version = line[16:-1]
          if version.startswith(u'1!'):
            version = version[2:]

          if project_name == u'efilter':
            line = u'%define version {0:s}\n'.format(version)

        elif line.startswith(b'%define unmangled_version '):
          if project_name == u'efilter':
            line = u'%define unmangled_version {0:s}\n'.format(version)

        elif not summary and line.startswith(b'Summary: '):
          summary = line

        elif line.startswith(b'Source0: '):
          if source_filename.endswith(u'.zip'):
            line = u'Source0: %{name}-%{unmangled_version}.zip\n'

        elif line.startswith(b'BuildRoot: '):
          if project_name == u'efilter':
            line = (
                u'BuildRoot: %{_tmppath}/'
                u'dotty-%{version}-%{release}-buildroot\n')

          elif project_name == u'psutil':
            line = (
                u'BuildRoot: %{_tmppath}/'
                u'%{name}-release-%{version}-%{release}-buildroot\n')

        elif (not description and not requires and
              line.startswith(b'Requires: ')):
          requires = line
          continue

        elif line.startswith(b'BuildArch: noarch'):
          if project_definition.architecture_dependent:
            continue

        elif line.startswith(b'BuildRequires: '):
          has_build_requires = True
          line = b'BuildRequires: {0:s}\n'.format(b', '.join(
              rpm_build_dependencies))

        elif line == b'\n' and summary and not has_build_requires:
          has_build_requires = True
          line = b'BuildRequires: {0:s}\n'.format(b', '.join(
              rpm_build_dependencies))

        elif line.startswith(b'%description') and not description:
          in_description = True

        elif line.startswith(b'%package -n python-'):
          has_python_package = True

        elif line.startswith(b'%package -n python3-'):
          has_python3_package = True

        elif line.startswith(b'%prep'):
          if not has_python_package:
            self._WritePythonPackageDefinition(
                output_file_object, summary, requires, description)

          if not python2_only and not has_python3_package:
            # TODO: convert python 2 package names to python 3
            self._WritePython3PackageDefinition(
                output_file_object, summary, requires, description)

          if project_name == u'PyYAML':
            output_file_object.write(
                b'%global debug_package %{nil}\n'
                b'\n')

        elif line.startswith(b'%setup -n %{name}-%{unmangled_version}'):
          if project_name == u'efilter':
            line = b'%autosetup -n dotty-%{unmangled_version}\n'
          elif project_name == u'psutil':
            line = b'%autosetup -n %{name}-release-%{unmangled_version}\n'
          else:
            line = b'%autosetup -n %{name}-%{unmangled_version}\n'

        elif line.startswith(b'python setup.py build'):
          line = self._GetBuildDefinition(python2_only)

        elif line.startswith(b'python setup.py install'):
          line = self._GetInstallDefinition(python2_only)

        elif line == b'rm -rf $RPM_BUILD_ROOT\n':
          line = b'rm -rf %{buildroot}\n'

        elif line.startswith(b'%files'):
          break

        elif in_description:
          # Ignore leading white lines in the description.
          if not description and line == b'\n':
            continue

          description = b''.join([description, line])
          continue

        output_file_object.write(line)

    license_line = self._GetLicenseFileDefinition(source_directory)

    doc_line = self._GetDocumentationFilesDefinition(source_directory)

    if not project_definition.architecture_dependent:
      lib_dir = '%{_exec_prefix}/lib'
    else:
      lib_dir = '%{_libdir}'

    self._WritePythonPackageFiles(
        output_file_object, license_line, doc_line, lib_dir)

    if not python2_only:
      self._WritePython3PackageFiles(
          output_file_object, license_line, doc_line, lib_dir)

    # TODO: add bindir support.
    output_file_object.write((
        b'\n'
        b'%exclude %{_bindir}/*\n'))

    # TODO: add shared data support.

    self._WriteChangeLog(output_file_object, version)

    return True

  def RewriteSetupPyGeneratedFile(
      self, project_definition, source_directory, source_filename,
      project_name, input_file, output_file):
    """Rewrites the RPM spec file generated with setup.py.

    Args:
      project_definition (ProjectDefinition): project definition.
      source_directory (str): path of the source directory.
      source_filename (str): name of the source package.
      project_name (str): name of the project.
      input_file (str): path of the input RPM spec file.
      output_file (str): path of the output RPM spec file.

    Returns:
      bool: True if successful, False otherwise.
    """
    python2_only = project_definition.IsPython2Only()

    rpm_build_dependencies = [u'python2-setuptools']
    if project_definition.architecture_dependent:
      rpm_build_dependencies.append(u'python-devel')

    if not python2_only:
      rpm_build_dependencies.append(u'python3-setuptools')
      if project_definition.architecture_dependent:
        rpm_build_dependencies.append(u'python3-devel')

    if project_definition.rpm_build_dependencies:
      rpm_build_dependencies.extend(
          project_definition.rpm_build_dependencies)

    # TODO: check if already prefixed with python-

    output_file_object = open(output_file, 'wb')

    result = self._RewriteSetupPyGeneratedFile(
        project_definition, source_directory, source_filename, project_name,
        rpm_build_dependencies, input_file, output_file_object)

    output_file_object.close()

    return result

  def RewriteSetupPyGeneratedFileForOSC(
      self, project_definition, source_directory, source_filename,
      project_name, input_file, output_file):
    """Rewrites the RPM spec file generated with setup.py for OSC.

    Args:
      project_definition (ProjectDefinition): project definition.
      source_directory (str): path of the source directory.
      source_filename (str): name of the source package.
      project_name (str): name of the project.
      input_file (str): path of the input RPM spec file.
      output_file (str): path of the output RPM spec file.

    Returns:
      bool: True if successful, False otherwise.
    """
    python2_only = project_definition.IsPython2Only()

    rpm_build_dependencies = [u'python-devel', u'python-setuptools']

    if not python2_only:
      rpm_build_dependencies.append(u'python3-devel')
      rpm_build_dependencies.append(u'python3-setuptools')

    if project_definition.rpm_build_dependencies:
      rpm_build_dependencies.extend(
          project_definition.rpm_build_dependencies)

    # TODO: check if already prefixed with python-

    output_file_object = open(output_file, 'wb')

    result = self._RewriteSetupPyGeneratedFile(
        project_definition, source_directory, source_filename, project_name,
        rpm_build_dependencies, input_file, output_file_object)

    output_file_object.close()

    return result
