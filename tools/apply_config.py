#!/usr/bin/env python


import glob
import os
import re
import toolsconfig


CONFIG = os.path.join('tools', 'tools.cfg')


def line_indent(line):
    indent = ''
    m = re.search(r'^(\s*)', line)
    if len(m.groups()) >= 1:
        indent = m.group(1)

    return indent


def html_path(path):
    return '/'.join(path.split(os.path.sep))


def update_base_js(line, dirpath, config):
    path = config.base_js()
    relpath = os.path.relpath(path, dirpath)

    return '<script type="text/javascript" src="%s"></script>' % html_path(relpath)


def update_deps_js(line, dirpath, config):
    path = config.deps_js()
    relpath = os.path.relpath(path, dirpath)

    return '<script type="text/javascript" src="%s"></script>' % html_path(relpath)


def update_require_main(line, dirpath, config):
    namespace = config.main_namespace()
    return '<script type="text/javascript"> goog.require(\'%s\'); </script>' % namespace


def update_exec_main(line, dirpath, config):
    namespace = config.main_namespace()
    return '%s();' % namespace


def update_provide_main(line, dirpath, config):
    namespace = config.main_namespace()
    return 'goog.provide(\'%s\');' % namespace


def update_main_fn(line, dirpath, config):
    namespace = config.main_namespace()
    return '%s = function() {' % namespace


def update_multitestrunner_css(line, dirpath, config):
    path = config.multitestrunner_css()
    relpath = os.path.relpath(path, dirpath)

    return '<link rel="stylesheet" type="text/css" href="%s">' % html_path(relpath)


def apply_config(path, config):
    lines = []
    updaters = {
            '<!--@base_js@-->': update_base_js,
            '<!--@deps_js@-->': update_deps_js,
            '/*@exec_main@*/': update_exec_main,
            '/*@main_fn@*/': update_main_fn,
            '/*@provide_main@*/': update_provide_main,
            '<!--@require_main@-->': update_require_main,
            '<!--@multitestrunner_css@-->': update_multitestrunner_css}
    markers = updaters.keys()
    dirpath = os.path.dirname(path)

    for line in open(path):
        for marker in markers:
            if line.find(marker) >= 0:
                updater = updaters[marker]
                line = line_indent(line) + updater(line, dirpath, config) + marker + '\n'
        lines.append(line)

    with open(path, 'w') as f:
        for line in lines:
            f.write(line)


def apply_config_all(config):
    dev_dir = config.development_dir()

    for root, dirs, files in os.walk(dev_dir):
        for file in files:
            path = os.path.join(root, file)
            apply_config(path, config)


if __name__ == '__main__':
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(basedir)

    config = toolsconfig.ToolsConfig()
    config.load(CONFIG)

    apply_config_all(config)
