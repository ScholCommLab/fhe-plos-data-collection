
# coding: utf-8

# # Collect PLOS2016 - Facebook Engagement

import configparser
import csv
import datetime
import json
import math
import pickle
import queue
from pathlib import Path
from random import shuffle

import pandas as pd
import requests
from ratelimit import RateLimitException, limits, sleep_and_retry

from facebook import GraphAPI, GraphAPIError

from tqdm.auto import tqdm
tqdm.pandas()


# ## Constants

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


base_dir = Path("../data/pipeline/")

input_csv = base_dir / "plos_ncbi.csv"
urls_csv = base_dir / "urls.csv"
query_csv = base_dir / "queries.csv"
og_csv = base_dir / "fb_objects.csv"

config_file = "../config.cnf"

batchsize = 50
sample_size = None
continue_crawl = True
shuffle_urls = True


# Load config
Config = configparser.ConfigParser()
Config.read(config_file)

FACEBOOK_APP_ID = Config.get('facebook', 'app_id')
FACEBOOK_APP_SECRET = Config.get('facebook', 'app_secret')
FACEBOOK_USER_TOKEN = Config.get('facebook', 'user_token')

RATELIMIT = int(Config.get('ratelimit', 'period'))


# ## Step 1 - Load FB credentials


def get_app_access(app_id, app_secret, version="2.10"):
    """Exchange a short-lived user token for a long-lived one"""
    payload = {'grant_type': 'client_credentials',
               'client_id': app_id,
               'client_secret': app_secret}

    try:
        response = requests.post(
            'https://graph.facebook.com/oauth/access_token?', params=payload)
    except requests.exceptions.RequestException:
        raise Exception()

    token = json.loads(response.text)
    token['created'] = str(datetime.datetime.now())
    return token


def extend_user_access(user_token, app_id, app_secret, version="2.10"):
    """Uses a short-lived user token to create a long lived one"""
    payload = {'grant_type': 'fb_exchange_token',
               'client_id': app_id,
               'client_secret': app_secret,
               'fb_exchange_token': user_token}

    try:
        response = requests.post(
            'https://graph.facebook.com/oauth/access_token?', params=payload)
    except requests.exceptions.RequestException:
        raise Exception()

    token = json.loads(response.text)
    token['created'] = str(datetime.datetime.now())
    return token


def token_expiry(token):
    remain = datetime.timedelta(seconds=token['expires_in'])
    created = datetime.datetime.strptime(
        token['created'], "%Y-%m-%d %H:%M:%S.%f")
    print("Token expires {}\n{} left".format(str(created+remain), str(remain)))


def expires_soon(token, tolerance=1):
    remain = datetime.timedelta(seconds=token['expires_in'])
    created = datetime.datetime.strptime(
        token['created'], "%Y-%m-%d %H:%M:%S.%f")
    now = datetime.datetime.now()

    if (now - created+remain).days < tolerance:
        return True
    else:
        return False


try:
    with open("token.pkl", "rb") as pkl:
        token = pickle.load(pkl)
        print("Found pickled token")

    if expires_soon(token):
        token = extend_user_access(
            FACEBOOK_USER_TOKEN, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
        print("Created new token, because of soon expiry")
except FileNotFoundError:
    print("No token found. Creating new one...")
    token = extend_user_access(
        FACEBOOK_USER_TOKEN, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)

print("Saving token")
token_expiry(token)
with open("token.pkl", "wb") as pkl:
    pickle.dump(token, pkl)


fb_graph = GraphAPI(token['access_token'], version="2.10")


# ## Step 2 - Load and prepare URLs


raw = pd.read_csv(urls_csv, index_col="url_id")
urls = raw

query_columns = ["url_id", "error_msg", "queried_at"]
try:
    if continue_crawl:
        queries = pd.read_csv(query_csv, index_col="query_id")
        urls = urls.drop(queries[queries.error_msg.isnull()].url_id)
        query_index = max(queries.index)+1
    else:
        raise
except:
    queries = pd.DataFrame(columns=query_columns)
    query_index = 0

if sample_size:
    urls = urls.sample(sample_size)


og_columns = ["og_id", "query_id", "received_at", "fb_url",
              "og_description", "og_title", "og_type", "og_updated_time",
              "reactions", "shares", "comments", "plugin_comments"]
og_objects = pd.DataFrame(columns=og_columns)


# ## Step 3 - Run queries


def process_result(url_id, query_index, result, og_objects, query_f, og_f, now):
    query_f.writerow([query_index, url_id, result['err_msg'], str(now)])

    # if result, record og object
    if 'og_obj' in result:
        i = og_objects.shape[0]

        og_id = result['og_obj']['id']
        received_at = str(result['received'])
        fb_url = result["fb_url"]

        og = {}
        for field in ['description', 'title', 'type', 'updated_time']:
            try:
                og[field] = result['og_obj'][field]
            except:
                og[field] = None

        reactions = int(result['og_eng']['reaction_count'])
        shares = int(result['og_eng']['share_count'])
        comments = int(result['og_eng']['comment_count'])
        plugin_comments = int(result['og_eng']['comment_plugin_count'])

        row = [og_id, query_index, received_at, fb_url,
               og['description'], og['title'], og['type'], og['updated_time'],
               reactions, shares, comments, plugin_comments]

        og_f.writerow(row)


def query_url(url):
    result = {}
    try:
        r = fb_graph.get_object(id=url.strip(), fields="engagement,og_object")
    except Exception as e:
        result['received'] = datetime.datetime.now()
        result['err_msg'] = str(e)
        print(e)
        return result

    result['received'] = datetime.datetime.now()
    result['err_msg'] = None
    result['fb_url'] = r['id']

    if 'og_object' in r:
        result["og_obj"] = r['og_object']
        result["og_eng"] = r['engagement']

    return result


def query_urls(urls):
    results = {}

    try:
        responses = fb_graph.get_objects(
            ids=[url.strip() for url in urls],
            fields="engagement,og_object")
    except Exception as e:
        print(e)
        raise

    received = datetime.datetime.now()

    for url, r in responses.items():
        result = {}

        result['received'] = received
        result['err_msg'] = None
        result['fb_url'] = r['id']

        if 'og_object' in r:
            result["og_obj"] = r['og_object']
            result["og_eng"] = r['engagement']

        results[url] = result
    return results


@sleep_and_retry
@limits(calls=1, period=RATELIMIT)
def process_url(batch, og_objects, query_f, og_f):
    """"""
    global query_index
    try:
        now = datetime.datetime.now()
        result = query_url(batch.url)
        process_result(batch.name, query_index, result,
                       og_objects, query_f, og_f, now)
    except Exception as e:
        query_f.writerow([query_index, batch.name, e, str(now)])
    query_index += 1


@sleep_and_retry
@limits(calls=1, period=RATELIMIT)
def process_batch(batch, og_objects, query_f, og_f, failed_batches):
    """"""
    global query_index
    try:
        now = datetime.datetime.now()
        results = query_urls(batch.url.tolist())

        # successful batch query
        for url, result in results.items():
            url_id = batch[batch.url == url].index[0]
            process_result(url_id, query_index, result, og_objects, query_f, og_f, now)
            query_index += 1

    # failed batch query
    except Exception as e:
        failed_batches.put((e, batch.index))

        # Process failed batches
        pbar = tqdm(total=failed_batches.qsize() * batchsize, desc="Failed batches")
        while not failed_batches.empty():
            e, bad_batch = failed_batches.get()
            if len(bad_batch) > 4:
                batch_indices = chunker(bad_batch, math.ceil(len(bad_batch)/2))

                for batch_ind in batch_indices:
                    batch = urls.loc[batch_ind]

                    q_len = failed_batches.qsize()
                    process_batch(batch, og_objects, query_writer, og_writer, failed_batches)
                    if failed_batches.qsize() == q_len:
                        pbar.update(len(batch_ind))

            else:
                for i in bad_batch:
                    process_url(urls.loc[i], og_objects, query_writer, og_writer)
                    pbar.update(1)
        pbar.close()


write_query_ids = False
write_og_ids = False
if not query_csv.exists():
    write_query_ids = True
if not og_csv.exists():
    write_og_ids = True

with open(str(query_csv), "a") as query_f, open(str(og_csv), "a") as og_f:
    query_writer = csv.writer(query_f, delimiter=",")
    og_writer = csv.writer(og_f, delimiter=",")

    # Write column labels
    if write_query_ids:
        query_writer.writerow(["query_id"] + queries.columns.tolist())

    if write_og_ids:
        og_writer.writerow(og_objects.columns.tolist())

    # Keep track of indices that failed during batchmode
    failed_batches = queue.Queue()

    # Initialise indices for batches
    if len(urls) < batchsize:
        batchsize = len(urls)

    indices = list(urls.index)
    if shuffle_urls:
        shuffle(indices)
    batch_indices = chunker(indices, batchsize)

    # Keep appending in batches of 50
    for batch_ind in tqdm(batch_indices, total=len(urls)//batchsize, desc="Batches"):
        batch = urls.loc[batch_ind]
        process_batch(batch, og_objects, query_writer, og_writer, failed_batches)
