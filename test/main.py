"""
A rudimentary URL downloader
"""

import os.path
import sys
from concurrent.futures import ThreadPoolExecutor
import signal
from functools import partial
from threading import Event
from urllib.request import urlopen
import argparse

from bs4 import BeautifulSoup

# The selenium module
from selenium import webdriver

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)


def get_next_episode_urls(url, driver, count, url_list, postfix=""):
    if postfix:
        url += "?wersja=" + postfix
    driver.get(url)
    src = driver.page_source
    parser = BeautifulSoup(src, "lxml")

    try:
        video = parser.find('video').get('src')
    except AttributeError:
        return None

    file_name = driver.title.replace(' ', '_').replace('/', '').replace("_-_CDA", '') + '.mp4'

    url_list.append((file_name, video))

    div = parser.findAll('div', attrs={'class': 'media-show'})[0]
    a = div.findAll('a')[0]
    next_url = a['href']
    if "http" not in next_url:
        next_url = "https://www.cda.pl" + next_url

    try:
        quality_span = a.findAll('span', attrs={'class': 'hd-ico-elem'})[0]
    except IndexError:
        quality_span = None

    quality = None
    if quality_span:
        quality = quality_span.text

    count -= 1

    if count >= 0:
        get_next_episode_urls(next_url, driver, count, url_list, quality)
    else:
        print("Next page: " + next_url)

    return url_list


def get_episode_url(url, driver, postfix=""):
    if postfix:
        url += "?wersja=" + postfix

    driver.get(url)
    src = driver.page_source

    parser = BeautifulSoup(src, "lxml")
    try:
        video = parser.find('video').get('src')
    except AttributeError:
        return None

    file_name = driver.title.replace(' ', '_').replace('/', '').replace("_-_CDA", '') + '.mp4'

    return file_name, video


def get_episode_urls(url, driver, skip):
    url_list = []
    driver.get(url)
    src = driver.page_source

    parser = BeautifulSoup(src, "lxml")
    data = parser.findAll('span', attrs={'class': 'wrapper-thumb-link'})

    if skip:
        index = len(data) - 1 if skip >= len(data) else skip
        data = data[index:]

    for div in data:
        links = div.findAll('a')
        try:
            quality_span = div.findAll('span', attrs={'class': 'hd-ico-elem'})[0]
        except IndexError:
            quality_span = None
        quality = None
        if quality_span:
            quality = quality_span.text
        for a in links:
            url = "https://www.cda.pl" + a['href']
            data = get_episode_url(url, driver, quality)
            if data:
                url_list.append(data)

    return url_list


progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)

done_event = Event()


def handle_sigint(signum, frame):
    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)


def copy_url(task_id: TaskID, url: str, path: str) -> None:
    """Copy data from a url to a local file."""
    # progress.console.log(f"Requesting {url}")
    response = urlopen(url)
    # This will break if the response doesn't contain content length
    progress.update(task_id, total=int(response.info()["Content-length"]))
    with open(path, "wb") as dest_file:
        progress.start_task(task_id)
        for data in iter(partial(response.read, 32768), b""):
            dest_file.write(data)
            progress.update(task_id, advance=len(data))
            if done_event.is_set():
                return
    progress.console.log(f"Downloaded {path}")


def download_all(urls):
    """Download multiple files to the given directory."""

    with progress:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for url in urls:
                filename = url[0]
                dest_path = os.path.join('.', filename)
                task_id = progress.add_task("download", filename=filename, start=False)
                pool.submit(copy_url, task_id, url[1], dest_path)


def site_login(driver):
    driver.get("https://www.cda.pl/login")
    driver.find_element_by_id("login").send_keys("quiteflame@gmail.com")
    driver.find_element_by_id("pass").send_keys("nataku666")
    driver.find_element_by_name("login").click()


def main(argv):
    parser = argparse.ArgumentParser(description="Downloads episodes from CDA.pl")

    episode_group = parser.add_argument_group("Episode", "Downloads single episode")
    episode_group.add_argument("-e", "--episode", type=str, help="single episode url")
    episode_group.add_argument("-q", "--quality", type=str, choices=["360p", "480p", "720p", "1080p"],
                               help="quality of single episode")

    folder_group = parser.add_argument_group("Folder", "Downloads whole folder")
    folder_group.add_argument("-f", "--folder", type=str, help="folder with episodes url")
    folder_group.add_argument("-s", "--skip", type=int, help="amount of episodes to skip in a folder")

    recursive_group = parser.add_argument_group("Recursive", "Downloads episodes recursively")
    recursive_group.add_argument("-n", "--next", type=str, help="starting episode url")
    recursive_group.add_argument("-c", "--count", type=int, help="count of next episodes")
    recursive_group.add_argument("-q1", "--quality_first", type=str, choices=["360p", "480p", "720p", "1080p"],
                                 help="quality of first episode")

    if len(argv) == 0:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    driver = webdriver.Firefox()

    site_login(driver)

    if args.folder:
        urls = get_episode_urls(args.folder, driver, args.skip)
        driver.close()
        download_all(urls)
        return

    if args.episode:
        url = get_episode_url(args.episode, driver, args.quality)
        driver.close()
        download_all([url])
        return

    if args.next:
        count = 10
        if args.count:
            count = args.count
        urls = get_next_episode_urls(args.next, driver, count, [], args.quality)
        driver.close()
        download_all(urls)
        return


if __name__ == "__main__":
    main(sys.argv[1:])
