"""
Mixin workbench behavior into XBlocks
"""
from glob import glob
import pkg_resources


def _read_file(file_path):
    """
    Read in a file's contents
    """
    with open(file_path) as file_input:
        file_contents = file_input.read()
    return file_contents


def _parse_title(file_path):
    """
    Parse a title from a file name
    """
    title = file_path
    title = title.split('/')[-1]
    title = '.'.join(title.split('.')[:-1])
    title = ' '.join(title.split('-'))
    title = ' '.join([
        word.capitalize()
        for word in title.split(' ')
    ])
    return title


def _read_files(files):
    """
    Read the contents of a list of files
    """
    file_contents = [
        (
            _parse_title(file_path),
            _read_file(file_path),
        )
        for file_path in files
    ]
    return file_contents


def _find_files(directory):
    """
    Find XML files in the directory
    """
    pattern = "{directory}/*.xml".format(
        directory=directory,
    )
    files = glob(pattern)
    return files


class XBlockWorkbenchMixin(object):
    """
    Provide a default test workbench for the XBlock
    """

    @classmethod
    def workbench_scenarios(cls):
        """
        Gather scenarios to be displayed in the workbench
        """
        module = cls.__module__
        module = module.split('.')[0]
        directory = pkg_resources.resource_filename(module, 'scenarios')
        files = _find_files(directory)
        scenarios = _read_files(files)
        return scenarios
