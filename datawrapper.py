import codecs
import datetime as dt
from datetime import timedelta
import logging
import time

from serverdensity.wrapper import Device
from serverdensity.wrapper import Tag
from serverdensity.wrapper import Metrics
from serverdensity.wrapper import ApiClient

logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
# summing lists map(sum, izip(a,b)) vector style.


class DataWrapper(object):

    def __init__(self, token, conf):
        self.token = token
        self.conf = conf
        self.historic_data = None
        client = ApiClient(self.token, timeout=(3.05, 18))
        self.device = Device(self.token)
        self.tag = Tag(self.token)
        self.metrics = Metrics(client)

        self._validation()

    def _validation(self):
        """Check the following
        - metric for every piece in infrastructure
        - That the configuration contains everything necessary.
        - check that there are no none values in any lists.
        """

    def _get_devices(self, infra_conf):
        """Takes the configuration part for each infrastructure"""
        raw_devices = self.device.list()

        if infra_conf.get('tag'):
            tags = self.tag.list()
            tag_id =[tag['_id'] for tag in tags if tag['name'] == infra_conf['tag']]
            if not tag_id:
                available_tags = '\n'.join(list(set([tag['name'] for tag in tags])))
                message = 'There is no tag with the name "{}". Try one of these: \n{}'.format(infra_conf['tag'], available_tags)
                raise Exception(message)
            else:
                tag_id = tag_id[0]
            devices = [device for device in raw_devices if tag_id in device.get('tags', [])]
            if not devices:
                available_tags = '\n'.join(list(set([tag['name'] for tag in tags])))
                raise Exception('There is no device with this tag name. Try one of these: \n{}'.format(available_tags))
        elif infra_conf.get('group'):
            group = infra_conf.get('group')
            devices = [device for device in raw_devices if group == device.get('group')]
            if not devices:
                groups = set([device['group'] for device in raw_devices
                             if not device['group'] is None])
                groups = '\n'.join(list(groups))
                raise Exception('There is no device with this group name. The following groups are available:\n {}'.format(groups))
        else:
            raise Exception('You have to provide either group or tag for each part of your infrastructure.')
        return devices

    def _merge_loadbalanced_data(self, data_points, points):
        max_length = len(data_points)
        for i, point in enumerate(points):
            if i < max_length:
                data_points[i] = data_points[i] + point
        return data_points

    def _get_metrics(self, metric, devices):
        """For all devices associated with the group or device"""
        metric = metric.split('.')
        metric_filter = self.metric_filter(metric)
        end = dt.datetime.now()
        start = end - timedelta(hours=self.conf['general'].get('timeframe', 24))
        data_entries = []
        for device in devices:
            data = self.metrics.get(device['_id'], start, end, metric_filter)
            data = self._data_node(data)
            time.sleep(0.3)
            if data['data']:
                data_entries.append(data)

        if not data_entries:
            metric = '.'.join(metric)
            # Append zero data to avoid zerodivison error
            data_entries.append({'data': [{'x': 0, 'y': 0}]})
            logging.warning('No server in this group has any data on {}'.format(metric))
        return data_entries

    def _data_node(self, data, names=None):
        """Inputs the data from the metrics endpoints and returns
        the node that has contains the data + names of the metrics."""

        if not names:
            names = []
        for d in data:
            if d.get('data') or d.get('data') == []:
                names.append(d.get('name'))
                d['full_name'] = names
                return d
            else:
                names.append(d.get('name'))
                return self._data_node(d.get('tree'), names)

    def _get_data_points(self, cumulative, data_entries, multiplier):
        """Extract the singular points into a list and return a list of those points"""
        data_points = []
        for data in data_entries:
            points = [point['y'] * multiplier for point in data['data']]
            if cumulative and len(data_points) > 0:
                self._merge_loadbalanced_data(data_points, points)
            else:
                data_points.extend(points)
        return data_points

    def _round(self, number):
        rounding = self.conf['general'].get('round', 2)
        if rounding > 0:
            return round(number, rounding)
        else:
            return int(round(number, 0))

    def calc_average(self, data_points):
        return self._round(sum(data_points) / len(data_points))

    def calc_max(self, data_points):
        return self._round(max(data_points))

    def calc_min(self, data_points):
        return self._round(min(data_points))

    def calc_median(self, data_points):
        data_points.sort()
        start = len(data_points) // 2.0
        if len(data_points) % 2 > 0:
            result = (data_points[start] + data_points[start + 1]) / 2.0
        else:
            result = self._round(data_points[start] // 2.0)
        return result

    def calc_sum(self, data_points):
        return self._round(sum(data_points))

    def gather_data(self):
        """The main function that gathers all data and returns an updated
        configuration file that the index template can read"""

        infrastructure = self.conf['infrastructure']
        for infra_conf in infrastructure:
            logging.info('Gather data from {}...'.format(infra_conf['title']))
            devices = self._get_devices(infra_conf)
            for metric_conf in infra_conf['metrics']:
                metric = metric_conf.get('metrickey')
                cumulative = metric_conf.get('cumulative', True)
                # giving the option to show case static information in boxes
                if metric:
                    multiplier = metric_conf.get('multiplier', 1)
                    data_entries = self._get_metrics(metric, devices)
                    for method in metric_conf['calculation']:
                        data_points = self._get_data_points(cumulative, data_entries, multiplier)
                        result = getattr(self, 'calc_{}'.format(method))(data_points)
                        metric_conf['{}_stat'.format(method)] = result
        return self.conf

    def metric_filter(self, metrics, filter=None):
        """from a list of metrics ie ['cpuStats', 'CPUs', 'usr'] it constructs
        a dictionary that can be sent to the metrics endpoint for consumption"""

        metrics = list(metrics)
        if not filter:
            filter = {}
            filter[metrics.pop()] = 'all'
            return self.metric_filter(metrics, filter)
        else:
            try:
                metric = metrics.pop()
                dic = {metric: filter}
                return self.metric_filter(metrics, dic)
            except IndexError:
                return filter

    def available(self):
        """Assumes that all metrics are the same for a group or a tag"""
        infrastructure = self.conf['infrastructure']
        md = '# Available metrics for all your groups\n\n'

        for infra_conf in infrastructure:
            if infra_conf.get('group'):
                category = infra_conf['group']
            elif infra_conf.get('tag'):
                category = infra_conf['tags']
            else:
                raise Exception('You need to provide either a group or tag')
            logging.info('Gathering metrics from {}...'.format(category))
            devices = self._get_devices(infra_conf)
            device = devices[0]
            end = dt.datetime.now()
            start = end - timedelta(hours=2)
            available = self.metrics.available(device['_id'], start, end)
            metrics = self.flatten(available)
            try:
                md += '## {}\n'.format(infra_conf['title'])
            except KeyError:
                raise KeyError('Each section need a title, go on fill one in and try again.')
            for metric in metrics:
                title = ' '.join([tup[0] for tup in metric])
                metric = '.'.join([tup[1] for tup in metric])
                entry = '##### {}\nmetrickey: {}\n\n'.format(title, metric)
                md += entry
        with codecs.open('available.md', 'w') as f:
            f.write(md)

    def flatten(self, lst):
        """Get all the keys when calling available"""
        for dct in lst:
            key = dct['key']
            name = dct['name']
            if 'tree' not in dct:
                yield [(name, key)]  # base case
            else:
                for result in self.flatten(dct["tree"]):  # recursive case
                    yield [(name, key)] + result

