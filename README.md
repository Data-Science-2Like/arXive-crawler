# arXive-crawler

A crawler for retriving latex paper data from arXive. This tool aims to use the rules which are provided by arXive here https://arxiv.org/help/bulk_data.

## Bulk Metadata Access

### OAI-PMH

arXiv supports the OAI protocol for metadata harvesting which is described here https://www.openarchives.org/pmh/.
- The standard for this protocol is described here https://www.openarchives.org/OAI/openarchivesprotocol.html
- Python offers a module which implements the standard: https://pypi.org/project/pyoai/

## Latex Data Crawling

This Crawler tries to abide by the rules delcared on https://arxiv.org/help/bulk_data.
Herefore the Parameters
- burstSize: 4
- sleepLength: 1
can be adapted manually to change the download rate. All files get either saved as .pdf or .tar.gz depending on the avialability of source material.

## Latex Expanding

This Crawler is able to automatically expand Latex files using the perl script latexpand from https://gitlab.com/latexpand/latexpand/-/blob/master/latexpand.
Latexpand is licensed under the BSD License https://opensource.org/licenses/BSD-3-Clause.