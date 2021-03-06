"""
Contains functional tests of the Bazaar class.
"""

import os

import pytest

from pip._internal.vcs.bazaar import Bazaar
from tests.lib import (
    _test_path_to_file_url, _vcs_add, create_file, is_bzr_installed, need_bzr,
)


@pytest.mark.skipif(
    'TRAVIS' not in os.environ,
    reason='Bazaar is only required under Travis')
def test_ensure_bzr_available():
    """Make sure that bzr is available when running in Travis."""
    assert is_bzr_installed()


@need_bzr
def test_export(script, tmpdir):
    """Test that a Bazaar branch can be exported."""
    source_dir = tmpdir / 'test-source'
    source_dir.mkdir()

    create_file(source_dir / 'test_file', 'something')

    _vcs_add(script, str(source_dir), vcs='bazaar')

    bzr = Bazaar('bzr+' + _test_path_to_file_url(source_dir))
    export_dir = str(tmpdir / 'export')
    bzr.export(export_dir)

    assert os.listdir(export_dir) == ['test_file']


@need_bzr
def test_export_rev(script, tmpdir):
    """Test that a Bazaar branch can be exported, specifying a rev."""
    source_dir = tmpdir / 'test-source'
    source_dir.mkdir()

    # Create a single file that is changed by two revisions.
    create_file(source_dir / 'test_file', 'something initial')
    _vcs_add(script, str(source_dir), vcs='bazaar')

    create_file(source_dir / 'test_file', 'something new')
    script.run(
        'bzr', 'commit', '-q',
        '--author', 'pip <pypa-dev@googlegroups.com>',
        '-m', 'change test file', cwd=source_dir,
    )

    bzr = Bazaar('bzr+' + _test_path_to_file_url(source_dir) + '@1')
    export_dir = tmpdir / 'export'
    bzr.export(str(export_dir))

    with open(export_dir / 'test_file', 'r') as f:
        assert f.read() == 'something initial'
