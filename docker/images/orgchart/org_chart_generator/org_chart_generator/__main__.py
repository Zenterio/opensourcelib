import os
import time

import click

from org_chart_generator.orgchart import generate_data_and_write_output

_DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__name__)), 'org_chart_generator', 'data')


@click.command()
@click.option(
    '--template',
    default=os.path.join(_DATA_DIR, 'template.html.in'),
    type=str,
    help='Input template file')
@click.option('--output', default='index.html', type=str, help='Output file')
@click.option(
    '--update-interval',
    type=int,
    default=0,
    help='Regenerate the output file with this frequency, 0 to only write once')
@click.argument('PATH')
def main(template, output, update_interval, path):
    generate_data_and_write_output(template, output, update_interval, path)

    while update_interval != 0:
        try:
            generate_data_and_write_output(template, output, update_interval, path)
        except Exception as e:
            print(str(e))
        time.sleep(update_interval)


if __name__ == '__main__':
    main()
