from random import choice
from urllib2 import urlopen
import sys

from lxml import etree
from lxml.html import tostring
from lxml.html.clean import Cleaner
from w3lib import encoding
from pyquery import PyQuery as pq

from mdr import MiningDataRegion, MiningDataRecord, MiningDataField


class DomTreeBuilder(object):
    def __init__(self, html, **options):
        cleaner = Cleaner(style=True, page_structure=False)
        self.html = cleaner.clean_html(html)
        self.options = options

    def build(self):
        parser = etree.HTMLParser(encoding='utf-8')
        return etree.fromstring(self.html, parser)

def annotate(regions):
    """
    annotate the regions with PyQuery. quite neat!
    """
    colors = ['#ffff42', '#ff0000', '#00ff00', '#ff00ff']

    for i, region in enumerate(regions):
        p = pq(region.parent[region.start])
        others = [region.parent[j] for j in xrange(region.start + 1, region.start + region.covered)]
        div = p.wrap('<div class="mdr_region" id={} style="color:{}; border:solid 5px"></div>'.format(i, choice(colors)))
        for e in others:
            div.append(e)

def main(html=None):
    builder = DomTreeBuilder(html, debug=False)
    root = builder.build()

    with open('verbose.html', 'w') as f:
        print >>f, tostring(root, pretty_print=True)

    region_m = MiningDataRegion(root, threshold=0.3, debug=False)
    regions = region_m.find_regions(root)

    for i, region in enumerate(regions):
        print 'region {}: {}[{}], {}, {}, {}'.format(i, region.parent.tag, region.start,
                                                     region.parent[region.start].tag, region.k, region.covered)

    record_m = MiningDataRecord()
    records_list = []

    for region in regions:
        records_list.append(record_m.find_records(region))

    mdf = MiningDataField()

    for i, records in enumerate(records_list):
        print 'records #{} length: {} elements/record: {} elements: {}'.format(i, len(records), \
                                                                                  len(records[0]), records[0])
        mdf.align_records(*records)

    # always annotate at last to avoid modify the DOM tree
    annotate(regions)

    with open('output.html', 'w') as f:
        print >> f, tostring(root, pretty_print=True)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        info = urlopen(sys.argv[1])
        _, html = encoding.html_to_unicode(info.headers.get('content_type'), info.read())
    else:
        html = open('1.html').read()
    main(html=html)