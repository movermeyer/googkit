import logging
import os
import re
import googkit.compat.urllib.request
from googkit.commands.command import Command


class ApplyConfigCommand(Command):
    CONFIG_TARGET_EXT = ('.html', '.xhtml', '.js', '.css')

    @classmethod
    def needs_project_config(cls):
        return True

    @classmethod
    def line_indent(cls, line):
        indent = ''
        m = re.search(r'^(\s*)', line)
        if len(m.groups()) >= 1:
            indent = m.group(1)

        return indent

    def update_base_js(self, line, dirpath):
        path = self.config.base_js()
        relpath = os.path.relpath(path, dirpath)
        href = googkit.compat.urllib.request.pathname2url(relpath)

        return '<script src="{href}"></script>'.format(href=href)

    def update_deps_js(self, line, dirpath):
        path = self.config.deps_js()
        relpath = os.path.relpath(path, dirpath)
        src = googkit.compat.urllib.request.pathname2url(relpath)

        return '<script src="{src}"></script>'.format(src=src)

    def update_multitestrunner_css(self, line, dirpath):
        path = self.config.multitestrunner_css()
        relpath = os.path.relpath(path, dirpath)
        href = googkit.compat.urllib.request.pathname2url(relpath)

        return '<link rel="stylesheet" href="{href}">'.format(href=href)

    def apply_config(self, path):
        lines = []
        updaters = {
            '<!--@base_js@-->': self.update_base_js,
            '<!--@deps_js@-->': self.update_deps_js,
            '<!--@multitestrunner_css@-->': self.update_multitestrunner_css}
        markers = updaters.keys()
        dirpath = os.path.dirname(path)

        with open(path) as fp:
            for line in fp:
                for marker in markers:
                    if line.find(marker) >= 0:
                        format_dict = {'marker': marker, 'path': path}
                        msg = 'Line marked by {marker} was replaced on {path}'.format(**format_dict)
                        logging.debug(msg)

                        line = '{indent}{content}{marker}\n'.format(
                            indent=ApplyConfigCommand.line_indent(line),
                            content=updaters[marker](line, dirpath),
                            marker=marker)

                lines.append(line)

        with open(path, 'w') as fp:
            for line in lines:
                fp.write(line)

    def apply_config_all(self):
        devel_dir = self.config.development_dir()

        # If library_root is in development_dir, we should avoid to walk into the library_root.
        ignores = (
            self.config.library_root(),
            self.config.compiler_root())

        for root, dirs, files in os.walk(devel_dir):
            for filename in files:
                (base, ext) = os.path.splitext(filename)
                if ext not in ApplyConfigCommand.CONFIG_TARGET_EXT:
                    continue

                filepath = os.path.join(root, filename)
                self.apply_config(filepath)

            # Avoid to walk into ignores
            for dirname in dirs:
                if os.path.join(root, dirname) in ignores:
                    dirs.remove(dirname)

    def run_internal(self):
        self.apply_config_all()