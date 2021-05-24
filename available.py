# Read the conf.yaml and ask what metrics you want to output in common.
import codecs
import os

import yaml
from datawrapper import DataWrapper

with codecs.open('conf.yml', 'r') as f:
    conf = yaml.load(f.read())


if __name__ == '__main__':
    try:
        token = os.environ['SD_TOKEN']
    except KeyError:
        token = raw_input('What is your token for Server Density: ').strip()
        os.environ['SD_TOKEN'] = token

    data = DataWrapper(token, conf)
    data.available() # generates a file called available.md
