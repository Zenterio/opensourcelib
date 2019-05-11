import logging
import os

from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import FrameworkExtension, get_logger_name

from ..messages import collect_metrics
from .reporter import AbstractMetricsReportExtension

logger = logging.getLogger(get_logger_name('k2', 'metrics', 'graph'))
logger.addHandler(logging.NullHandler())

GRAPH_REPORTER_ID = ConfigOptionId(
    name='ids',
    description='Names a graph metrics reporter instance',
    multiple=True,
    entity=True,
    namespace='metrics.graph',
)

GRAPH_DIRECTORY = ConfigOptionId(
    name='dir',
    description='Directory to write the graphs to',
    default='${output.dir}/metrics/graphs',
    at=GRAPH_REPORTER_ID,
)

GRAPH_FILENAME = ConfigOptionId(
    name='filename',
    description=(
        'Name of the graph file to write, '
        'the format to write is determined by the file ending'),
    at=GRAPH_REPORTER_ID,
)

GRAPH_NAMESPACE = ConfigOptionId(
    name='namespace',
    description='Metrics namespace to add to the plot',
    at=GRAPH_REPORTER_ID,
    multiple=True,
)

GRAPH_TITLE = ConfigOptionId(
    name='title',
    description='Title of the graph',
    default=None,
    at=GRAPH_REPORTER_ID,
)

GRAPH_YLABEL = ConfigOptionId(
    name='ylabel',
    description='Label of the Y label',
    default=None,
    at=GRAPH_REPORTER_ID,
)

GRAPH_YMIN = ConfigOptionId(
    name='ymin',
    description='Minimum value on Y axis',
    default=None,
    at=GRAPH_REPORTER_ID,
    option_type=float)

GRAPH_YMAX = ConfigOptionId(
    name='ymax',
    description='Maximum value on Y axis',
    default=None,
    at=GRAPH_REPORTER_ID,
    option_type=float)

GRAPH_WIDTH = ConfigOptionId(
    name='width',
    description='Output a graph of this width in pixels',
    default=1280,
    option_type=int,
    at=GRAPH_REPORTER_ID)

GRAPH_HEIGHT = ConfigOptionId(
    name='height',
    description='Output a graph of this height in pixels',
    default=720,
    option_type=int,
    at=GRAPH_REPORTER_ID)


@FrameworkExtension(
    name='metrics',
    config_options=[
        ConfigOption(GRAPH_REPORTER_ID, required=False, instantiate_on=True),
        ConfigOption(GRAPH_DIRECTORY, required=True),
        ConfigOption(GRAPH_FILENAME, required=True),
        ConfigOption(GRAPH_NAMESPACE, required=True),
        ConfigOption(GRAPH_TITLE, required=False),
        ConfigOption(GRAPH_YLABEL, required=False),
        ConfigOption(GRAPH_YMIN, required=False),
        ConfigOption(GRAPH_YMAX, required=False),
        ConfigOption(GRAPH_WIDTH, required=False),
        ConfigOption(GRAPH_HEIGHT, required=False),
    ],
    groups=['metrics'],
)
class MetricsGraphReporter(AbstractMetricsReportExtension):
    """Metrics reporter that generates an image containing a plot of a series measurement."""

    def __init__(self, config, instances):
        super().__init__(config, instances)
        self.namespaces = config.get(GRAPH_NAMESPACE)
        self.directory = config.get(GRAPH_DIRECTORY)
        self.filename = config.get(GRAPH_FILENAME)
        self.title = config.get(GRAPH_TITLE)
        self.ylabel = config.get(GRAPH_YLABEL)
        self.ymin = config.get(GRAPH_YMIN)
        self.ymax = config.get(GRAPH_YMAX)
        self.width = config.get(GRAPH_WIDTH)
        self.height = config.get(GRAPH_HEIGHT)

    def __str__(self):
        return 'MetricsGraphReporter({namespaces}) -> {filename}'.format(
            namespaces=', '.join(self.namespaces), filename=self.filename)

    def handle_generate_metrics_report(self, message):
        logger.debug('Importing matplotlib')
        import matplotlib
        logger.debug('Done importing matplotlib')
        matplotlib.use('Agg')
        logger.debug('Importing matplotlib.pyplot')
        import matplotlib.pyplot
        logger.debug('Done importing matplotlib.pyplot')

        self.bbox_extra_artists = []
        self.figure, self.axes = matplotlib.pyplot.subplots()
        for data_frame in self._get_data_frames():
            self._plot_from_data_frame(data_frame)
        self._resize_to_desired_resolution()
        self._adjust_axes()
        self._add_timestamp_formatting()
        self._add_grid()
        logger.debug('Writing plots to disk')
        self._write_to_disk()
        logger.debug('Done writing plots to disk')

    def _resize_to_desired_resolution(self):
        # matplotlib measures everything in inches and dots per inches.
        dots_per_inches = self.figure.get_dpi()
        self.figure.set_size_inches(self.width / dots_per_inches, self.height / dots_per_inches)

    def _adjust_axes(self):
        if self.ymin or self.ymax:
            self.axes.set_ylim([self.ymin, self.ymax])

    def _add_timestamp_formatting(self):
        import matplotlib
        import matplotlib.dates
        import matplotlib.pyplot

        class Formatter(matplotlib.dates.DateFormatter):

            def __call__(self, x, pos=0):
                return super().__call__(matplotlib.dates.epoch2num(x))

        self.axes.xaxis.set_major_formatter(Formatter('%Y-%m-%d %H:%M:%S'))
        self.figure.autofmt_xdate(bottom=0.3, rotation=30)

    def _add_grid(self):
        self.axes.grid()

    def _write_to_disk(self):
        os.makedirs(self.directory, exist_ok=True)

        self.figure.tight_layout()
        self.figure.savefig(
            os.path.join(self.directory, self.filename),
            bbox_extra_artists=self.bbox_extra_artists,
            bbox_inches='tight')

    def _plot_from_data_frame(self, data_frame):
        plot = data_frame.plot.line(
            ax=self.axes,
            x=data_frame.columns[0],
            y=data_frame.columns[1],
            title=self.title,
            legend=True)
        plot.set_ylabel(self.ylabel)
        plot.set_xlabel('')
        legend = plot.legend(loc='upper left', bbox_to_anchor=(1.0, 0.5))
        self.bbox_extra_artists.append(legend)

    def _get_data_frames(self):
        import pandas
        data_frames = []
        namespaces = self._get_namespaces()

        # The namespaces are sorted so that the labels retain the same order
        # and coloring each time they are generated.
        for namespace in sorted(namespaces):
            metrics = namespaces[namespace].get_data()
            if not metrics:
                continue
            data_frame = pandas.DataFrame(metrics, columns=['timestamp', 'data'])
            data_frame.columns = ['timestamp', namespace]
            data_frames.append(data_frame)

        return data_frames

    def _get_namespaces(self):

        def flatten(namespace, metric):
            if metric.is_leaf:
                return {namespace: metric}
            result = {}
            for child in metric.children:
                result.update(flatten('.'.join([namespace, child.name]), child))
            return result

        result = {}
        for namespace in self.namespaces:
            result.update(flatten(namespace, collect_metrics(self.messagebus, namespace)))
        return result
