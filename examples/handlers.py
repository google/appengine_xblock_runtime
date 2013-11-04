# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The HTTP handlers for the example server."""

__author__ = 'John Orr (jorr@google.com)'

from cStringIO import StringIO
import json
import os
import urllib
import appengine_xblock_runtime.runtime
import django.template.loader
import jinja2
import webapp2
from workbench.runtime import _BlockSet
from xblock.fragment import Fragment
from google.appengine.api import users


class WorkbenchRuntime(appengine_xblock_runtime.runtime.Runtime):
    """A XBlock runtime which uses the App Engine datastore."""

    def render_template(self, template_name, **kwargs):
        """Loads the django template for `template_name."""
        template = django.template.loader.get_template(template_name)
        return template.render(django.template.Context(kwargs))

    def wrap_child(self, block, view, frag, context):  # pylint: disable=W0613
        wrapped = Fragment()
        wrapped.add_javascript_url('/static/js/vendor/jquery.min.js')
        wrapped.add_javascript_url('/static/js/vendor/jquery.cookie.js')

        data = {}
        if frag.js_init_fn:
            wrapped.add_javascript_url(
                '/static/js/runtime/%s.js' % frag.js_init_version)
            data['init'] = frag.js_init_fn
            data['runtime-version'] = frag.js_init_version
            data['usage'] = block.scope_ids.usage_id
            data['block-type'] = block.scope_ids.block_type

        if block.name:
            data['name'] = block.name

        html = u'<div class="xblock"%s>%s</div>' % (
            ''.join(' data-%s="%s"' % item for item in data.items()),
            frag.body_html(),
        )
        wrapped.add_content(html)
        wrapped.add_frag_resources(frag)
        return wrapped

    def query(self, block):
        return _BlockSet(self, [block])

    def resources_url(self, resource):
        return '/static/%s' % resource


class XBlockEndpointHandler(webapp2.RequestHandler):
    """Router for all callbacks from XBlocks."""

    def post(self, usage_id, handler_name):
        student_id = self.request.get('student')  # From XBlock code
        assert student_id == users.get_current_user().user_id()

        def fix_ajax_request_body(body):
            # The ajax clients are sending JSON strings in the POST body, but
            # appengine is trying to read it as name=value pairs in url-encoded
            # strings. Maybe this is because the wrong mime type is being set?
            return urllib.unquote(body[:-1])

        rt = WorkbenchRuntime(student_id=student_id)
        block = rt.get_block(usage_id)
        self.request.body = fix_ajax_request_body(self.request.body)
        response = block.runtime.handle(block, handler_name, self.request)
        self.response.body = response.body
        self.response.headers.update(response.headers)


class BasePageHandler(webapp2.RequestHandler):
    """Base class for pages which use Jinja templates."""

    def __init__(self, *args, **kwargs):
        super(BasePageHandler, self).__init__(*args, **kwargs)
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=['jinja2.ext.autoescape'],
            autoescape=True)


class DefaultPageHandler(BasePageHandler):
    """Display the default landing page."""

    def get(self):
        template_values = {
            'email': users.get_current_user().nickname(),
            'logout_url': users.create_logout_url('/')}
        template = self.template_env.get_template('default.html')
        self.response.write(template.render(template_values))


class DisplayXblockPageHandler(BasePageHandler):
    """Display the XBlock with usage id passed in the query parameter."""

    def get(self):
        usage_id = self.request.get('usage_id')
        student_id = users.get_current_user().user_id()

        rt = WorkbenchRuntime(student_id=student_id)
        block = rt.get_block(usage_id)
        fragment = rt.render(block, 'student_view')

        template_values = {
            'fragment': fragment,
            'student_id': student_id}
        template = self.template_env.get_template('display_xblock.html')
        self.response.write(template.render(template_values))


class XblockRestHandler(webapp2.RequestHandler):
    """A REST handler to store and retrieve XBlock XML definitions."""

    def get(self, usage_id):
        student_id = users.get_current_user().user_id()

        rt = WorkbenchRuntime(student_id=student_id)
        block = rt.get_block(usage_id)
        xml_buffer = StringIO()
        rt.export_to_xml(block, xml_buffer)

        self.response.headers['Content-Type'] = 'text/xml'
        self.response.write(xml_buffer.getvalue())

    def post(self):
        assert self.request.headers['Content-Type'] == 'text/xml'

        self.response.headers['Content-Type'] = 'application/json'
        try:
            rt = WorkbenchRuntime()
            usage_id = rt.parse_xml_string(self.request.body)

            self.response.write(json.dumps({
                'status': 'OK',
                'usage_id': str(usage_id)}))
        except Exception as e:
            self.response.write(json.dumps({
                'status': 'ERROR',
                'message': str(e)}))
