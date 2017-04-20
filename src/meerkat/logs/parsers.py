# -*- coding: utf-8 -*-

"""
Parsers for log files.

This module provides a generic parser that you can customize with regular
expressions to find the log files and to parse them.
"""

from __future__ import unicode_literals

import re
from os import walk
from os.path import join, relpath, sep


# FIXME: generic parser should give defaults to args, and use class
# variables to initialize them. Then, subparsers should overwrite only the
# class variables and not the init methods.

class GenericParser(object):
    """Generic parser. Customize it with regular expressions."""

    def __init__(self, file_path_regex, log_format_regex, top_dir):
        """
        Init method.

        Args:
            file_path_regex (str): the regex to find the log files.
            log_format_regex (str): the regex to parse the log files.
            top_dir (str): the path to the root directory containing the logs.
        """
        self.file_path_regex = file_path_regex
        self.log_format_regex = log_format_regex
        self.top_dir = top_dir
        self._content = None

    @property
    def content(self):
        """
        Return parsed data. Parse it if not already parsed.

        Returns:
            list: list of dictionaries (one for each parsed line).
        """
        if self._content is None:
            self._content = self.parse_files()
        return self._content

    # http://stackoverflow.com/questions/6798097#answer-6799409
    def matching_files(self):
        """
        Find files.

        Returns:
            list: the list of matching files.
        """
        matching = []
        matcher = self.file_path_regex
        pieces = self.file_path_regex.pattern.split(sep)
        partial_matchers = map(
            re.compile,
            (sep.join(pieces[:i + 1]) for i in range(len(pieces))))

        for root, dirs, files in walk(self.top_dir, topdown=True):
            for i in reversed(range(len(dirs))):
                dirname = relpath(
                    join(root, dirs[i]), self.top_dir)
                dirlevel = dirname.count(sep)
                if not partial_matchers[dirlevel].match(dirname):
                    del dirs[i]

            for filename in files:
                if matcher.match(filename):
                    matching.append(relpath(join(root, filename)))

        return matching

    def parse_files(self):
        """
        Find the files and parse them.

        Returns:
            list: list of dictionaries (one for each parsed line).
        """
        log_re = self.log_format_regex
        log_lines = []
        for log_file in self.matching_files():
            with open(log_file) as f:
                matches = re.finditer(log_re, f.read())
                for match in matches:
                    log_lines.append(match.groupdict())
        return log_lines

    def parse_string(self, string):
        """
        Parse just a string.

        Args:
            string (str): the log line to parse.

        Returns:
            dict: parsed information with regex groups as keys.
        """
        return re.match(self.log_format_regex, string).groupdict()


class NginXAccessLogParser(GenericParser):
    """Parser for NginX logs."""

    def __init__(self, file_path_regex=None,
                 log_format_regex=None, top_dir=None):
        """
        Init method.

        Args:
            file_path_regex (str): the regex to find the log files.
            log_format_regex (str): the regex to parse the log files.
            top_dir (str): the path to the root directory containing the logs.

        Defaults:
            file_path_regex: r'access.log'
            log_format_regex: see source code.
            top_dir: '/var/log/nginx'
        """
        if file_path_regex is None:
            file_path_regex = re.compile(r'access.log')
        # coderwall.com/p/snn1ag/regex-to-parse-your-default-nginx-access-logs
        if log_format_regex is None:
            log_format_regex = re.compile(
                r'(?P<ip_address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - '
                r'\[(?P<day>\d{2})/(?P<month>[a-z]{3})/(?P<year>\d{4})'
                r':(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}) '
                r'(?P<timezone>(\+|\-)\d{4})\] \"(?P<verb>(GET|POST)) '
                r'(?P<url>.+)(?P<protocol>HTTP/(1\.0|1\.1|2\.0)") '
                r'(?P<status_code>\d{3}) (?P<bytes_sent>\d+) '
                r'(["](?P<referrer>(\-)|(.+))["]) (["](?P<user_agent>.+)["])',
                re.IGNORECASE)
        if top_dir is None:
            top_dir = '/var/log/nginx'
        super(NginXAccessLogParser, self).__init__(
            file_path_regex, log_format_regex, top_dir)


class NginXErrorLogParser(GenericParser):
    """Parser for NginX error logs."""

    def __init__(self, file_path_regex=None,
                 log_format_regex=None, top_dir=None):
        """
        Init method.

        Args:
            file_path_regex (str): the regex to find the log files.
            log_format_regex (str): the regex to parse the log files.
            top_dir (str): the path to the root directory containing the logs.

        Defaults:
            file_path_regex: r'error.log'
            log_format_regex: see source code.
            top_dir: '/var/log/nginx'
        """
        if file_path_regex is None:
            file_path_regex = re.compile(r'error.log')
        if log_format_regex is None:
            log_format_regex = re.compile(
                # YYYY/MM/DD HH:MM:SS [LEVEL] PID#TID: *CID MESSAGE
                r'(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2}) '
                r'(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}) '
                r'\[(?P<level>[a-z]*)\] (?P<pid>\d+)#(?P<tid>\d+): '
                r'(\*(?P<cid>\d+) )?(?P<message>[^,]+)'
                r'(, client: (?P<ip_address>[^,]+))?'
                r'(, server: (?P<server>[^,]+))?'
                r'(, request: (?P<verb>(GET|POST)) (?P<url>[^ ]+) '
                r'(?P<protocol>HTTP/(1\.0|1\.1|2\.0)))?'
                r'(, upstream: (?P<upstream>[^,]+))?'
                r'(, host: (?P<host>[^,]+))?'
                r'(, referrer: (?P<referrer>[^,]+))?$',
                re.IGNORECASE)
        if top_dir is None:
            top_dir = 'var/log/nginx'
        super(NginXErrorLogParser, self).__init__(
            file_path_regex, log_format_regex, top_dir)


class ApacheAccessLogParser(GenericParser):
    """Parser for Apache logs. Not implemented."""


class ApacheErrorLogParser(GenericParser):
    """Parser for Apache error logs. Not implemented."""


class UWSGIAccessLogParser(GenericParser):
    """Parser for UWSGI logs. Not implemented."""


class UWSGIErrorLogParser(GenericParser):
    """Parser for UWSGI error logs. Not implemented."""


class GunicornAccessLogParser(GenericParser):
    """Parser for Gunicorn logs. Not implemented."""


class GunicornErrorLogParser(GenericParser):
    """Parser for Gunicorn error logs. Not implemented."""
