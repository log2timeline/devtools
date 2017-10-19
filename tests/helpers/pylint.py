#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the pylint helper."""

from __future__ import unicode_literals

import unittest

import l2tdevtools.helpers.pylint as pylint_helper


class PylintHelperTest(unittest.TestCase):
  """Tests the pylint helper"""

  def testInitialize(self):
    """Tests that the helper can be initialized."""
    helper = pylint_helper.PylintHelper()
    self.assertIsNotNone(helper)


if __name__ == '__main__':
  unittest.main()
