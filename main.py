import html
import json
import random
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

import emoji
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


DATALOGALERT_PROJECT_KEY = "othj-ahdi-womc-wquj-ludk-husj"
ACTIVE_MACHINE = "production"
MANUALLY_REMOVED_CHARS = [
    "\U0010019f",
    "\U001001ab",
    "\U0001F5D9",
    "\U0010fc00",
    "\U001001a9",
]


def request_url(my_url):
    my_url = urllib.parse.quote(my_url, safe='/:?=&%,|', encoding=None, errors=None)

    try:
        req = urllib.request.Request(my_url)
        f = urllib.request.urlopen(req)
        html_full = f.read().decode('utf-8')
        html_full = html.unescape(html_full)
        f.close

        return html_full

    except urllib.error.HTTPError as err:
        print('******************************')
        print('DOWNLOAD ERROR!')
        print('err.code: ' + str(err.code))
        print('url with error:', my_url)
        print('******************************')
        return None

    else:
        return None


def datalogalert(
    project_key=None,
    action=None,
    runtime_key=None,
    process_name=None,
    alert_name=None,
    counters=None,
    comment=None,
):
    if ACTIVE_MACHINE == 'development':
        return 'dummy-key'

    heartbeat_url = 'https://www.datalogalert.com/api/q?'
    if project_key is None:
        project_key = DATALOGALERT_PROJECT_KEY

    heartbeat_url = heartbeat_url + "&project_key=" + project_key
    if process_name is not None:
        heartbeat_url = heartbeat_url + "&process_name=" + process_name
    if runtime_key is not None:
        heartbeat_url = heartbeat_url + "&runtime_key=" + str(runtime_key)
    if action is not None:
        heartbeat_url = heartbeat_url + "&action=" + str(action)
    if counters is not None:
        heartbeat_url = heartbeat_url + "&counters=" + str(counters)
    if comment is not None:
        heartbeat_url = heartbeat_url + "&comment=" + str(comment)
    if alert_name is not None:
        heartbeat_url = heartbeat_url + "&alert_name=" + str(alert_name)

    heartbeat_url = heartbeat_url.replace("'", '"')

    print("posting datalogalert.com API:", heartbeat_url)

    x = 0
    max_retries = 20
    for attempt in range(max_retries):
        x = x + 1

        try:
            json_response = request_url(heartbeat_url)
            print("json_response:", json_response)
            json_response = json.loads(json_response)

            if action == "make_alert":
                return json_response["alert"]["alert_name"]
            return json_response["runtime"]["runtime_key"]
        except:
            print("Failed to call datalogalert API")
            print("url:", heartbeat_url)
            print("Retry count:", x, "of", max_retries)
            print("Sleeping", 30 * x, "secs...")
            time.sleep(30 * x)

        else:
            pass

    else:
        print("All attempts to call datalogalert API failed. Shutting down")
        raise


def pretty_print_dict(dct):
    if type(dct) not in [dict, list]:
        dct = json.loads(dct)

    print()
    print(json.dumps(dct, ensure_ascii=False, indent=2, default=str))
    print()


def remove_emojis(text):
    text = emoji.replace_emoji(text, replace='')

    for char in MANUALLY_REMOVED_CHARS:
        text = text.replace(char, "")

    text = unicodedata.normalize("NFKC", text)

    return text


def random_sleep(min_sec=5, max_sec=10):
    secs = random.uniform(min_sec, max_sec)
    print('sleep secs:', secs)
    time.sleep(secs)
    print('awake')

    return


def remove_empty_lines_and_strip(text):
    text = re.sub(r'\n\s*\n+', '\n', text)
    text = text.strip()

    return text


def data_16_local_machine_scrape_amedia_articles(max_runtime_in_minutes=20):
    end_time = datetime.utcnow() + timedelta(minutes=max_runtime_in_minutes)
    count_handled = 0

    runtime_key = None
    runtime_key = datalogalert(
        project_key=None,
        action='runtime_start',
        runtime_key=runtime_key,
        process_name='data_16_local_machine_scrape_amedia_articles',
        alert_name=None,
        counters=None,
        comment=None,
    )

    idx = 0
    driver = None
    stop_comment = 'completed'

    while True:
        if datetime.utcnow() > end_time:
            print('Overrunning time --> break')
            stop_comment = 'max_runtime_reached'
            break

        print('=')
        print("calling: https://www.buildpilot.com/next-to-scrape-kjds-ldpe-qxld")

        next_in_queue = json.loads(requests.post('https://www.buildpilot.com/next-to-scrape-kjds-ldpe-qxld').text)
        pretty_print_dict(next_in_queue)

        if next_in_queue["status"] == "no-queue":
            if driver is not None:
                driver.quit()
                driver = None
            print('BREAK')
            stop_comment = 'no_queue'
            break

        my_url = next_in_queue["ds"]["url"]

        if driver is None:
            print('Preare NEW driver')
            profile_path = '/home/olav/snap/firefox/common/.mozilla/firefox/1iapehrt.default'
            fp = webdriver.FirefoxProfile(profile_path)
            driver = webdriver.Firefox(fp)

        driver.get(my_url)
        random_sleep(8, 12)

        try:
            print()
            print('try to click away cookies')
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe[src*='consent'], iframe[id*='cookie']")
            driver.switch_to.frame(iframe)
            driver.find_element(By.CSS_SELECTOR, "button[aria-label='Godta alle']").click()
            driver.switch_to.default_content()
            print(' --> clicked')
            random_sleep(2, 5)
        except:
            print(' --> failed')
            pass

        print()
        print('try to driver.switch_to.default_content()')
        try:
            driver.switch_to.default_content()
            print(' --> success')
        except:
            print(' --> failed')
            pass
        print()

        button_to_login = driver.find_elements(By.XPATH, "//a[contains(text(), 'Logg inn')]")
        print('button_to_login:', button_to_login)
        if button_to_login:
            print('click to login')
            button_to_login[0].click()
            random_sleep(4, 6)

        if "Olav Brandt Pekeberg" in driver.page_source:
            print('"Olav Brandt Pekeberg" is in driver.page_source')
        else:
            print('"Olav Brandt Pekeberg" is NOT in driver.page_source')

        is_logged_in = driver.find_element(By.XPATH, "//*[contains(text(), 'Olav Brandt Pekeberg')]").is_displayed()
        print('is_logged_in:', is_logged_in)
        if is_logged_in is False:
            print('DEBUG Cannot find button with logged in')
            raise RuntimeError('DEBUG Cannot find button with logged in')

        html_full = driver.page_source

        if ">Ønsker du tilgang?<" in html_full:
            raise RuntimeError('DEBUG Prompt upgrade! 1')
        if ">Du trenger mer tilgang<" in html_full:
            raise RuntimeError('DEBUG Prompt upgrade! 2')

        soup = BeautifulSoup(driver.page_source, "html.parser")

        published_on_str = soup.find("meta", {"property": "article:published_time"})["content"]

        elements = []

        h1_ele = soup.find('h1', itemprop='headline')
        if h1_ele is None:
            h1_ele = soup.find("h1", class_=lambda c: c and "title" in c.split())
        h1 = h1_ele.decode_contents().strip()
        elements.append("# " + h1)
        elements.append("")

        p = soup.find('p', {'data-content': 'lead-text'})
        ingress = p.decode_contents().strip() if p else None
        if ingress:
            elements.append("## " + ingress)
            elements.append("")

        body = soup.find('div', {'data-content': 'body-text'})

        did_exclude_related_teaser = False

        block_tags = ['p', 'h2', 'h3', 'li']

        for tag in body.find_all(block_tags, recursive=True):
            if tag.find(block_tags):
                print('skip 0:', tag.get_text(strip=False))
                continue

            if tag.find_parent('a', class_='related-teaser'):
                print('skip 1:', tag.get_text(strip=False))
                did_exclude_related_teaser = True
                continue
            if ('related-teaser' in tag.get('class', [])) or tag.find_parent(class_='related-teaser'):
                print('skip 3:', tag.get_text(strip=False))
                did_exclude_related_teaser = True
                continue
            if tag.find('a', class_='related-teaser'):
                print('skip 4:', tag.get_text(strip=False))
                did_exclude_related_teaser = True
                continue
            if tag.name == 'p' and tag.get('data-content') == 'lead-text':
                print('skip 5:', tag.get_text(strip=False))
                continue
            if tag.find_parent('amedia-placeholder'):
                print('skip 6:', tag.get_text(strip=False))
                continue
            if tag.find_parent('div', class_='title-wrapper'):
                print('skip 7:', tag.get_text(strip=False))
                continue
            if tag.find_parent('graff-enkel-poll'):
                print('skip 8:', tag.get_text(strip=False))
                continue

            do_skip_class = False
            for skip_class in ["article-tags-bottom", "graff-enkel-poll", "brick-teaser-player-overlay"]:
                if (skip_class in tag.get('class', [])) or tag.find_parent(class_=skip_class):
                    print('skip 9: class', skip_class, '| content:', tag.get_text(strip=False))
                    do_skip_class = True
                    break
            if do_skip_class:
                continue

            if tag.name == 'p':
                raw = tag.decode_contents()

                raw = re.sub(
                    r'^\s*(\(<[^>]+>.*?<\/[^>]+>\)|<a[^>]*>\([^)]*\)<\/a>|\([^)]*\))\s*',
                    '',
                    raw
                )

                text = BeautifulSoup(raw, 'html.parser').get_text(strip=False)

            else:
                text = tag.get_text(strip=False)

            if not text:
                continue

            text = remove_empty_lines_and_strip(text)

            if text.startswith('Foto: '):
                print('skip 10:', tag.get_text(strip=False))
                text = None
                continue
            if text.lower() in ['les også:', 'annonse', 'lukk bildet', 'vi vil gjerne høre om smått og stort som foregår i distriktet']:
                print('skip 11:', tag.get_text(strip=False))
                text = None
                continue

            text = "\n".join([line for line in text.split("\n") if not line.startswith("Foto:")]).strip()

            if text == "":
                continue

            if tag.name == 'h2':
                text = "\n## " + text
            elif tag.name == 'li':
                text = "• " + text

            elements.append(text)

        article_text = '\n'.join(elements)

        article_text = remove_emojis(article_text)

        print('------------')
        print(article_text)
        print('------------')

        print("did_exclude_related_teaser:", did_exclude_related_teaser)

        payload = {
            "db_id": next_in_queue["ds"]["db_id"],
            "full_text": article_text,
            "published_on_str": published_on_str,
        }

        r = requests.post("https://www.buildpilot.com/locally-parsed-data-kjds-ldpe-qxld", json=payload)
        print('response:', r.text)

        idx += 1
        count_handled += 1
        print('idx:', idx)
        if idx % 10 == 0:
            print('Shit down Driver')
            driver.quit()
            driver = None

        if datetime.utcnow() > end_time:
            print('Overrunning time --> break')
            stop_comment = 'max_runtime_reached'
            break

        random_sleep(min_sec=30, max_sec=60)

    datalogalert(
        project_key=None,
        action='runtime_succeeded',
        runtime_key=runtime_key,
        process_name='data_16_local_machine_scrape_amedia_articles',
        alert_name=None,
        counters={
            'count_handled': count_handled,
            'queue': json.loads(requests.post('https://www.buildpilot.com/next-to-scrape-kjds-ldpe-qxld').text)["count_queue"],
        },
        comment=stop_comment,
    )


def main():
    data_16_local_machine_scrape_amedia_articles()


if __name__ == "__main__":
    main()
