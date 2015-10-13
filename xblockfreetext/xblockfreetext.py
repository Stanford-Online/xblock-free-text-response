"""
This is the core logic for the FreeText XBlock
"""
import os

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope
from xblock.fields import String
from xblock.fragment import Fragment


class XblockFreetext(XBlock):
    """
    Enables instructors to create questions with free-text responses.
    """

    @staticmethod
    def workbench_scenarios():
        """
        Gather scenarios to be displayed in the workbench
        """
        return [
            ('FreeText XBlock',
             """<sequence_demo>
                    <xblockfreetext />
                    <xblockfreetext name="My First XBlock" />
                </sequence_demo>
             """),
        ]

    name = String(
        default='FreeText XBlock',
        scope=Scope.settings,
        help="This is the XBlock's name",
    )

    def student_view(self, context=None):
        """
        Build the fragment for the default student view
        """
        fragment = self.build_fragment(
            path_html='view.html',
            paths_css=[
                'view.less.min.css',
            ],
            paths_js=[
                'view.js.min.js',
            ],
            fragment_js='XblockFreetextView',
        )
        return fragment

    def studio_view(self, context=None):
        """
        Build the fragment for the edit/studio view

        Implementation is optional.
        """
        fragment = self.build_fragment(
            path_html='edit.html',
            paths_css=[
                'edit.less.min.css',
            ],
            paths_js=[
                'edit.js.min.js',
            ],
            fragment_js='XblockFreetextEdit',
        )
        return fragment

    @XBlock.json_handler
    def studio_view_save(self, data, suffix=''):
        """
        Save XBlock fields

        Returns: the new field values
        """

        # TODO: Add an entry here for each field.
        self.name = data['name']
        return {
            'name': self.name,
        }

    def get_resource_string(self, path):
        """
        Retrieve string contents for the file path
        """
        path = os.path.join('public', path)
        resource_string = pkg_resources.resource_string(__name__, path)
        return resource_string.decode('utf8')

    def get_resource_url(self, path):
        """
        Retrieve a public URL for the file path
        """
        path = os.path.join('public', path)
        resource_url = self.runtime.local_resource_url(self, path)
        return resource_url

    def build_fragment(self,
        path_html='',
        paths_css=[],
        paths_js=[],
        urls_css=[],
        urls_js=[],
        fragment_js=None,
    ):
        """
        Assemble the HTML, JS, and CSS for an XBlock fragment
        """
        html_source = self.get_resource_string(path_html)
        html_source = html_source.format(
            self=self,
        )
        fragment = Fragment(html_source)
        for url in urls_css:
            fragment.add_css_url(url)
        for path in paths_css:
            url = self.get_resource_url(path)
            fragment.add_css_url(url)
        for url in urls_js:
            fragment.add_javascript_url(url)
        for path in paths_js:
            url = self.get_resource_url(path)
            fragment.add_javascript_url(url)
        if fragment_js:
            fragment.initialize_js(fragment_js)
        return fragment
