import json
from xml.dom.minidom import parseString

from dicttoxml import dicttoxml


def write_changelog(descriptions, start_tag, end_tag, json_file, txt_file, xml_file):
    """
    Write the changelog to each specified file.

    :param descriptions: The changelog data
    :param start_tag: The start tag the data was generated for
    :param end_tag: The end tag the data was generated for
    :param json_file: name of json output file
    :param txt_file: name of text output file
    :param xml_file: name of xml output file
    """
    if end_tag is not None:
        header = 'Changelog for {start}...{end}'.format(start=start_tag, end=end_tag)
    else:
        header = 'Changelog for {start}'.format(start=start_tag)

    output = {header: descriptions}
    if json_file:
        with open(json_file, 'w') as file:
            file.write(_format_json(output))
    if xml_file:
        with open(xml_file, 'w') as file:
            file.write(_format_xml(output))
    if txt_file:
        with open(txt_file, 'w') as file:
            file.write(_format_txt(output))


def _format_json(descriptions):
    r = json.dumps(descriptions, indent=4)
    return r


def _format_xml(descriptions):
    xml = dicttoxml(descriptions, custom_root='changelog', attr_type=False)
    dom = parseString(xml)
    return dom.toprettyxml()


def _format_txt(descriptions):
    output = """
    ================================================================================

    CHANGE LOG

    ================================================================================

    Latest changes ({header})
    ===========================

    {issues}
    """
    issue_list = []
    header_string = ''
    for header, issues in descriptions.items():
        header_string = header
        for issue in issues:
            issue_data = []
            for key, value in issue.items():
                issue_data.append(value)
            issue_string = ': '.join(issue_data)
            issue_list.append(issue_string)
    return output.format(header=header_string, issues='\n\n    '.join(issue_list))
