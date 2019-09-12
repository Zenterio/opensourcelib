import json
import logging

import click
import flask

import zit.cisco_ios

app = flask.Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')

logging.basicConfig()
logging.getLogger('paramiko').setLevel(logging.INFO)

networks = [
    {
        'network': '5',
        'vlan': '710',
        'description': 'McDonalds WiFi'
    }
]


@app.route('/api/networks', methods=['GET'])
def get_networks():
    return flask.Response(
        response=json.dumps({
            'networks': networks
        }, indent=2) + '\n',
        content_type='application/json')


@app.route('/api/ports', methods=['GET'])
def get_ports():
    portlist = zit.cisco_ios.get_ports()
    for portinfo in portlist:
        portinfo['network'] = [n['network'] for n in networks if n['vlan'] == portinfo['vlan']][0]
    return flask.Response(
        response=json.dumps({
            'ports': portlist
        }, indent=2) + '\n',
        content_type='application/json')


@app.route('/api/port/<path:port>', methods=['GET'])
def get_port(port):
    portinfo = zit.cisco_ios.get_port(port)
    portinfo['network'] = [n['network'] for n in networks if n['vlan'] == portinfo['vlan']][0]
    return flask.Response(
        response=json.dumps(portinfo, indent=2) + '\n', content_type='application/json')


@app.route('/api/port/<path:port>', methods=['POST'])
def post_port(port):
    print(str(port))
    network = flask.request.json['network']
    print(str(network))
    zit.cisco_ios.set_vlan_for_port(
        port, [n['vlan'] for n in networks if n['network'] == network][0])
    return ''


@app.route('/', methods=['GET'])
def get_root():
    return flask.send_file('static/index.html')


@click.command()
@click.version_option()
def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
