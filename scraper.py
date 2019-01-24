import os
from datetime import timedelta, date
from urllib.parse import urljoin
from pathlib import Path
import pickle

import gevent.monkey
gevent.monkey.patch_all()
from lxml import html
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

FOLDER = "APOD"
SAVE_DIR = Path.expanduser(Path('~/')) / FOLDER
Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)
MAX_JOBS = 8
HISTORY = SAVE_DIR / 'history1.pkl'
PROCESSED = pickle.load(open(HISTORY, 'rb')) if HISTORY.exists() else set()
START_DATE = date(2018, 6, 16)
END_DATE = date(2019, 1, 25)


def requests_retry_session(
    retries=5,
    backoff_factor=0.2,
    status_forcelist=(500, 502, 503, 504),
    session=None,
):
    session = session or requests.Session()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    session.headers.update(header)
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def download(info):
    print('Downloading:', info)
    resp = SESS.get(info['url'])
    tree = html.fromstring(resp.content)
    rel_links = tree.xpath('//a/@href')
    img_links = filter(lambda x: x.startswith('image/'), rel_links)
    for link in img_links:
        img_url = urljoin('https://apod.nasa.gov/apod/', link)
        save_dir = SAVE_DIR / info['year'] / info['month']
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        file_path = save_dir / os.path.basename(link)
        # check if file already exists on disk
        if file_path.exists():
            continue
        img = SESS.get(img_url)
        with open(file_path, 'wb') as outfile:
            outfile.write(img.content)
        print('Download complete:', file_path)
    PROCESSED.add(info['url'])


def save_history():
    with open(HISTORY, 'wb') as outfile:
        pickle.dump(PROCESSED, outfile)


def main():
    global SESS
    SESS = requests_retry_session()
    jobs = []
    total_days = int((END_DATE - START_DATE).days)
    for n in range(total_days):
        ymd = (START_DATE + timedelta(n)).strftime("%y%m%d")
        url = f"https://apod.nasa.gov/apod/ap{ymd}.html"
        info = {'url': url, 'year': ymd[:2], 'month': ymd[2:4], 'day': ymd[4:]}
        if url in PROCESSED:
            continue
        jobs.append(gevent.spawn(download, info))
        if len(jobs) == MAX_JOBS or n == total_days-1:
            try:
                gevent.wait(jobs)
                jobs.clear()
            except (Exception, KeyboardInterrupt, SystemExit) as e:
                save_history()
                print('ERROR:', e)
    save_history()


if __name__ == '__main__':
    main()
