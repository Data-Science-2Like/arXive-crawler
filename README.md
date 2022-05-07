# arXive-crawler

A crawler for retriving latex paper data from arXive. This tool aims to use the rules which are provided by arXive here https://arxiv.org/help/bulk_data.

## Bulk Metadata Access

### OAI-PMH

arXiv supports the OAI protocol for metadata harvesting which is described here https://www.openarchives.org/pmh/.
- The standard for this protocol is described here https://www.openarchives.org/OAI/openarchivesprotocol.html
- Python offers a module which implements the standard: https://pypi.org/project/pyoai/

```
-o /path/to/out meta --from START_DATE --until END_DATE
```
By default only paper in the compter science domain get crawled. This behavior can be changed in `metaCrawler.py`.

## Latex Data Crawling

This Crawler tries to abide by the rules delcared on https://arxiv.org/help/bulk_data.
Herefore the Parameters
- `burstSize`: 4
- `sleepLength`: 1  
can be adapted manually to change the download rate. All files get either saved as .pdf or .tar.gz depending on the avialability of source material.

**Disclaimer**: Even though we used the performance settings suggested by arXive we got sometimes blocked. So maybe use a more conservative crawling speed.

```
-o /path/to/out download --sleep 4 --burst --start START_ID --end END_ID [--proxy --diff]
```
Because we got blocked this tool supports the use of proxy servers. Activated by supplying the `--proxy` flag. When activated a list of proxies will be taken from https://free-proxy-list.net/.
**This option is very slow and therefore shouldn't be used.**

When you need to often restart the crawler it is helpful to use the `--diff` flag. When supplied the crawler will check which papers are already existing in the output directory and skip them accordingly.

```
-o /path/to/out zip --name FILE_NAME
```
Zips existing paper ids from output directory to single file. The ids in this file are also recognised by the `--diff` option of the crawler.


## Latex Expanding

This Crawler is able to automatically expand Latex files using the perl script latexpand from https://gitlab.com/latexpand/latexpand/-/blob/master/latexpand.
Latexpand is licensed under the BSD License https://opensource.org/licenses/BSD-3-Clause.

```
-o /path/to/out expand -i /path/to/in [--bib]
```

When `--bib` is supplied als the bibliography will be extract out of the LaTeX archives.

## Known Issues
- The crawler only reconizes the file types `.pdf`, `.tar.gz` and `.docx`. In very vew cases the downloaded file can also be a single tex file.

