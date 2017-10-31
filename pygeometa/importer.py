# =================================================================
#
# Terms and Conditions of Use
#
# Unless otherwise noted, computer program source code of this
# distribution # is covered under Crown Copyright, Government of
# Canada, and is distributed under the MIT License.
#
# The Canada wordmark and related graphics associated with this
# distribution are protected under trademark law and copyright law.
# No permission is granted to use them outside the parameters of
# the Government of Canada's corporate identity program. For
# more information, see
# http://www.tbs-sct.gc.ca/fip-pcim/index-eng.asp
#
# Copyright title to all 3rd party software distributed with this
# software is held by the respective copyright holders as noted in
# those files. Users are asked to read the 3rd Party Licenses
# referenced with those assets.
#
# Copyright (c) 2017 Government of Canada
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

from xml.etree import ElementTree as etree
import logging

import click
from owslib.iso import MD_Metadata
from six.moves.urllib.request import urlopen
import yaml

LOGGER = logging.getLogger(__name__)

IMPORT_FORMATS = 'iso19139-hnap'


class Importer(object):
    """generic importer mechanism"""

    def __init__(self, xml):
        """constructor"""

        self.xml = None
        self.mdata = None
        self.mcf = {
            'mcf': {
                'version': '1.0.0',
            },
            'metadata': {},
            'spatial': {},
            'identification': {},
            'distribution': {}
        }

    def export(self):
        """export MCF object as YAML"""

        return yaml.safe_dump(self.mcf, version=(1, 1),
                              default_flow_style=False, allow_unicode=True)


class ISO19139HNAP(Importer):
    """ISO 19139 HNAP importer"""

    def __init__(self, xml):
        """constructor"""
        Importer.__init__(self, xml)

        if xml.startswith(('http', 'ftp')):  # URL
            content = urlopen(xml).read()
            self.mdata = MD_Metadata(etree.fromstring(content))
        else:  # file on disk
            self.mdata = MD_Metadata(etree.parse(xml))

        self.mcf['metadata']['identifier'] = self.mdata.identifier
        self.mcf['metadata']['language'] = self.mdata.language
        self.mcf['metadata']['language_alternate'] = self.mdata.locales[0].id
        self.mcf['metadata']['charset'] = self.mdata.charset
        self.mcf['metadata']['hierarchylevel'] = self.mdata.hierarchy
        self.mcf['metadata']['datestamp'] = self.mdata.datestamp
        self.mcf['metadata']['dataseturi'] = self.mdata.dataseturi

    def __repr__(self):
        return '<ISO19139HNAP instance>'


@click.command('import')
@click.option('--xml',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to XML metadata (filepath or URL)')
@click.option('--formats', is_flag=True, help='List support import formats')
@click.option('--output', type=click.File('w', encoding='utf-8'),
              help='Name of output file')
def import_(xml, formats, output):
    """Import XML metadata into MCF format"""

    if formats:
        click.echo(IMPORT_FORMATS)
    elif xml is None:
        raise click.UsageError('Missing --xml option')
    else:
        mcf = ISO19139HNAP(xml).export()

        if output is None:
            click.echo(mcf)
        else:
            output.write(mcf)
