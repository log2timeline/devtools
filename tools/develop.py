#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tool to build, run and manage dockerized development environments."""

from __future__ import unicode_literals
from __future__ import print_function

import argparse
import json
import os
import platform
import sys
import tarfile
import tempfile

try:
  import docker
except ImportError:
  print('Please install docker and try again')
  sys.exit(1)

UTF8 = 'utf-8'
docker_base_url = (
    'npipe:////./pipe/docker_engine' if platform.system() == 'Windows'
    else 'unix://var/run/docker.sock')
docker_build_client = docker.APIClient(base_url=docker_base_url)
docker_client = docker.from_env()
docker_image_name = 'plaso-dev-environment'


def BuildDevelopmentImage(plaso_src, verbose=False, nocache=False):
  """Builds a docker image to be used for Plaso development.

  Args:
    plaso_src (str): absolute location of the plaso source directory.
    verbose (bool): print all output of docker build steps.
    nocache (bool): don't use cached layers from a previous build.
  """
  print('Building docker image...')

  root_repo_location = os.path.dirname(os.path.dirname(
      os.path.abspath(__file__)))
  root_repo_location = str(root_repo_location)
  dockerfile_location = os.path.join(
      root_repo_location, 'config', 'docker', 'plaso_dev_dockerfile')
  ppa_installer_location = os.path.join(
      plaso_src, 'config', 'linux', 'gift_ppa_install.sh')

  # Add the installer file and dockerfile to the same build context
  context_tarball_location = tempfile.NamedTemporaryFile(
      delete=False, suffix='.tar').name
  tar = tarfile.open(context_tarball_location, 'w')
  tar.add(ppa_installer_location, arcname='gift_ppa_install.sh')
  tar.add(dockerfile_location, arcname='Dockerfile')
  tar.close()

  with open(context_tarball_location, 'rb') as tarball:
    for line in docker_build_client.build(
        fileobj=tarball,
        tag=docker_image_name,
        nocache=nocache,
        custom_context=True):
      parts = line.decode(UTF8).split('\r\n')
      for part in parts:
        if part == '':
          continue
        part_json = json.loads(part)
        if 'stream' in part_json:
          stream = part_json['stream']
        elif 'aux' in part_json:
          sha_id = part_json['aux']['ID']
          print('Built image with SHA: {0:s}'.format(sha_id))
          continue
        elif 'status' in part_json and 'id' in part_json:
          stream = '{0:s}:{1:s}'.format(part_json['status'], part_json['id'])
        else:
          continue
        if 'Step' in stream and not verbose:
          print(stream)
        elif verbose:
          print(stream.strip())


def RunCommand(image_name, command, plaso_source):
  """Runs a command inside a Plaso development container, prints the output.

  Args:
    image_name (str): name of the docker image to start the container with.
    command (str): command to run inside the docker container.
    plaso_source (string): absolute location of the plaso source directory.
  """
  print('Running command: {0:s}'.format(command))

  container = docker_client.containers.run(
      image_name, command, detach=True,
      volumes={plaso_source: {'bind': '/root/plaso', 'mode': 'rw'}})

  for line in container.logs(stdout=True, stderr=True, stream=True):
    print(line.decode(UTF8), end='')


def StartContainer(image_name, plaso_src):
  """Starts a Plaso development container.

  Args:
    image_name (str): name of the docker image to start the container with.
    plaso_src (string): absolute path to the plaso source directory.

  Returns:
    docker.containers.Container: a container object.
  """
  print('Starting container with image {0:s}'.format(image_name))
  # This method is only called for python >= 3.0 but linter complains that
  # os.get_terminal_size doesn't exist (in 2.7), disable no-member for now
  columns, rows = os.get_terminal_size(0)  # pylint: disable=no-member
  container = docker_client.containers.run(
      image_name, detach=True, tty=True,
      # Setting COLUMNS and ROWS avoids an issue where the container's terminal
      # prematurely wraps long commands due to not having a tty upon creation
      environment=['COLUMNS={0:d}'.format(columns), 'ROWS={0:d}'.format(rows)],
      volumes={plaso_src: {'bind': '/root/plaso', 'mode': 'rw'}})
  return container


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """

  argument_parser = argparse.ArgumentParser(description=(
      'Enables the building, running and management of a dockerized plaso '
      'development environment'))

  argument_parser.add_argument(
      'action', action='store', metavar='ACTION',
      choices=['build', 'check_dependencies', 'test', 'start'], help=(
          'the command to run'))

  argument_parser.add_argument(
      '--verbose', '-v', action='store_true', default=False, help=(
          'show all docker output'))

  argument_parser.add_argument(
      '--nocache', action='store_true', default=False, help=(
          'don\'t use cached build steps'))

  if 'PLASO_SRC' in os.environ:
    plaso_src = os.environ['PLASO_SRC']
  else:
    print(
        'Please set the PLASO_SRC environment variable to the absolute path '
        'to your Plaso source tree')
    return False

  options = argument_parser.parse_args()
  command = options.action

  # Check to ensure that docker is installed & working
  try:
    docker_client.info()
  except docker.errors.APIError:
    print('Please ensure Docker is installed and running')
    return 1

  if command == 'build':
    BuildDevelopmentImage(
        plaso_src,
        verbose=options.verbose,
        nocache=options.nocache)
  elif command == 'check_dependencies':
    RunCommand(
        '{0:s}:latest'.format(docker_image_name),
        'python utils/check_dependencies.py',
        plaso_src)
  elif command == 'test':
    RunCommand(
        '{0:s}:latest'.format(docker_image_name),
        'python run_tests.py',
        plaso_src)
  elif command == 'start':
    if sys.version_info > (3, 0):
      container = StartContainer(
          '{0:s}:latest'.format(docker_image_name), plaso_src)

      print(
          """To enter the development environment, attach to container {0:s}
          e.g. 'docker exec -it {0:s} /bin/bash'""".format(
              container.name))
    else:
      print(
          """To start the development environment, run:
          docker run -v {0:s}:/root/plaso -it {1:s} /bin/bash
          """.format(plaso_src, docker_image_name))
  else:
    print('Command {0:s} not supported'.format(command))
    return False

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
