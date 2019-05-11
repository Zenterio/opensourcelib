"""
Holds the different available reports.

Reporters write a summary and a full report of all the items
found during analysis.
"""

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ReportingError(Exception):

    def __init__(self, msg, original_exception=None):
        super().__init__(type(self))
        self.msg = msg
        self.original_exception = original_exception

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


class ItemSummary():

    def __init__(self, definition):
        self.count = 0
        self.definition = definition
        self.items = []


class ItemStats():

    def get_item_summaries(self, items):
        summaries = {}
        for item in items:
            definition_id = item.definition.definition_id
            summary = summaries.get(definition_id, ItemSummary(item.definition))
            summary.count += 1
            summary.items.append(item)
            summaries[definition_id] = summary

        result = (summaries[def_id] for def_id in sorted(summaries.keys()))
        return result


class TextReporter():

    def __init__(self, summary_output, report_output):
        self.summary_output = summary_output
        self.report_output = report_output
        logger.debug('TextReporter: created')

    def write_summary(self, items):
        try:
            self.summary_output.write("""SUMMARY:
--------
""")
            summary = None
            for summary in ItemStats().get_item_summaries(items):
                self.write_item_summary(summary, self.summary_output)
            if summary is None:
                self.summary_output.write('Nothing to report\n')
        except Exception as e:
            logger.error('TextReporter: write_summary (error={err}'.format(err=e))
            raise ReportingError('TextReporter: Unknown error while writing summary.', e)

    def write_report(self, items):
        try:
            self.report_output.write("""REPORT:
-------
""")
            summary = None
            for summary in ItemStats().get_item_summaries(items):
                self.write_definition(summary, self.report_output)
            if summary is None:
                pass
                self.report_output.write('Nothing to report\n')
        except Exception as e:
            logger.error('TextReporter: write_report (error={err}'.format(err=e))
            raise ReportingError('TextReporter: Unknown error while writing report.', e)

    def write_item_summary(self, item_summary, stream):
        stream.write(
            '{count} ({id}) {title}\n'.format(
                count=item_summary.count,
                id=item_summary.definition.id,
                title=item_summary.definition.title))

    def write_definition(self, item_summary, stream):
        definition = item_summary.definition
        items = item_summary.items
        header = '({id}) {title}'.format(id=definition.id, title=definition.title)
        desc = self.get_description(definition.description)
        stream.write(
            """
{header}
{line}
{desc}

""".format(header=header, line=self.get_headerline(header), desc=desc))
        for item in items:
            self.write_item(item, stream)

    def write_item(self, item, stream):
        for match in item.matches:
            self.write_match(match, stream)
        stream.write('\n')

    def write_match(self, logmatch, stream):
        entry = '  {index}: {content}'.format(
            index=logmatch.data.index, content=logmatch.data.content)
        match_text = logmatch.match.group() if logmatch.match else ''
        position = entry.find(match_text)
        entry_match = ''
        if position > 0:
            entry_match = (' ' * position) + ('-' * len(match_text))
        stream.write("""{entry}
{entry_match}
""".format(entry=entry, entry_match=entry_match))

    def get_headerline(self, header):
        return '-' * len(header)

    def get_description(self, desc):
        return desc.rstrip()


class WatchersReporter():

    def __init__(self, watchers, separator):
        self.watchers = watchers
        self.separator = separator

    def write_summary(self, items):
        pass

    def write_report(self, items):
        emails = self.find_emails(items)
        if emails:
            self.watchers.write(self.separator.join(emails))

    def find_emails(self, items):
        emails = set()
        for summary in ItemStats().get_item_summaries(items):
            for email in summary.definition.watchers:
                emails.add(email)
        return sorted(emails)
