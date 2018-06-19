
# coding: utf-8

# In[89]:


import datetime
import configparser
import json
import math
import requests
import queue
import csv

import ratelimit
import pandas as pd
from facebook import GraphAPI, GraphAPIError

# from tqdm._tqdm_notebook import tqdm_notebook as tqdm
from tqdm import tqdm


# In[ ]:


# tqdm.pandas()


# ## Step 0 - Define helpers, load configs, etc

# In[69]:


input_csv = "../data/plos2016.csv"
urls_csv = "../data/urls.csv"
query_csv = "../data/queries.csv"
og_csv = "../data/og_objects.csv"

batchsize = 50


# In[71]:


def get_fb_access_token(app_id, app_secret):
    payload = {'grant_type': 'client_credentials',
               'client_id': app_id,
               'client_secret': app_secret}

    try:
        response = requests.post('https://graph.facebook.com/oauth/access_token?', params = payload)
    except requests.exceptions.RequestException:
        raise Exception()

    access_token = json.loads(response.text)['access_token']
    print("Generated access token: " + access_token)


# In[72]:


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(1, len(seq), size))


# In[73]:


def query_url(url):
    result = {}
    try:
        r = fb_graph.get_object(id=url.strip(), fields="engagement,og_object")
    except Exception as e:
        result['received'] = datetime.datetime.now()
        result['err_msg'] = str(e)
        return result
        
    result['received'] = datetime.datetime.now()
    result['err_msg'] = None
    result['fb_url'] = r['id']
    
    if 'og_object' in r:
        result["og_obj"] = r['og_object']
        result["og_eng"]  = r['engagement']
    
    return result


# In[74]:


def query_urls(urls):
    results = {}
    
    try:
        responses = fb_graph.get_objects(
            ids=[url.strip() for url in urls],
            fields="engagement,og_object")
    except Exception as e:
        raise

    received = datetime.datetime.now()

    for url, r in responses.items():        
        result = {}

        result['received'] = received
        result['err_msg'] = None
        result['fb_url'] = r['id']

        if 'og_object' in r:
            result["og_obj"] = r['og_object']
            result["og_eng"]  = r['engagement']

        results[url] = result
    return results 


# # Step 1 - Load FB credentials

# In[ ]:


# Load config
Config = configparser.ConfigParser()
Config.read('../config.cnf')
FACEBOOK_APP_ID = Config.get('facebook', 'app_id')
FACEBOOK_APP_SECRET = Config.get('facebook', 'app_secret')


# In[75]:


# access_token = get_fb_access_token(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
temp_token = "EAAEFTB4qA1gBACQG3PkgcmKiPqcflBAVluklgES9SZCN6yMeIB3ukdcE52ZAwSBha2xg5ioN6yZBMQDOAhPS0ZBVkRWU6wyDkzTSCzt5Rh0ZBknZBCy5QH5An7874x68ffI4usrQ5ZBBCd9taWyG5miMHsVO8yjjDEZD"
fb_graph = GraphAPI(temp_token, version="2.10")


# In[76]:


# fb_graph.extend_access_token(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)


# # Step 2 - Load URLs

# In[133]:


urls = pd.read_csv(urls_csv, index_col="url_id")
# urls = urls.sample(500)


# ## Step 3 - Run queries

# In[134]:


def process_result(url_id, result, queries, og_objects, query_f, og_f, now):
    query_id = queries.shape[0]
    queries.loc[query_id] = [url_id, result['err_msg'], str(now)]
    # queries.loc[[query_id]][query_columns].to_csv(query_f, header=False, )
    
    query_f.writerow([query_id, url_id, result['err_msg'], str(now)])
                             
    # if result, record og object
    if 'og_obj' in result:
        i = og_objects.shape[0]

        og_id = result['og_obj']['id']
        reactions = int(result['og_eng']['reaction_count'])
        shares = int(result['og_eng']['share_count'])
        comments = int(result['og_eng']['comment_count'])
        plugin_comments = int(result['og_eng']['comment_plugin_count'])

        for field in ['description', 'title', 'type', 'updated_time']:
            try:
                og_objects.loc[i, "og_{}".format(field)] = result['og_obj'][field]
            except:
                og_objects.loc[i, "og_{}".format(field)] = None
        
        og_objects.loc[i, "fb_url"] = result["fb_url"]
        og_objects.loc[i, "og_id"] = og_id
        og_objects.loc[i, "query_id"] = query_id
        og_objects.loc[i, "received_at"] = str(result['received'])
        og_objects.loc[i, ["reactions", "shares", "comments", "plugin_comments"]] = [reactions, shares, comments, plugin_comments]
        
        # og_objects.loc[[i]][og_columns].to_csv(og_f, header=False)
        
        og_f.writerow(og_objects.loc[i][og_columns].tolist())


# In[135]:


def process_url(batch, queries, og_objects, query_f, og_f):
    """"""
    now = datetime.datetime.now()
    result = query_url(batch.url)
    process_result(batch.name, result, queries, og_objects, query_f, og_f, now)


# In[136]:


def process_batch(batch, queries, og_objects, query_f, og_f, failed_batches):
    """"""
    try:
        now = datetime.datetime.now()
        results = query_urls(batch.url.tolist())

        # successful batch query
        for url, result in results.items():
            url_id = batch[batch.url == url].index[0]
            process_result(url_id, result, queries, og_objects, query_f, og_f, now) 
        
    # failed batch query
    except GraphAPIError as e: 
        failed_batches.put((e, batch_ind))


# In[137]:


# Create DF for queries
query_columns = ["url_id", "error_msg", "queried_at"]
queries = pd.DataFrame(columns=query_columns)

# Create DF for graph objects
og_columns = ["og_id", "query_id", "received_at", "fb_url",
              "og_description", "og_title", "og_type", "og_updated_time",
              "reactions", "shares", "comments", "plugin_comments"]
og_objects = pd.DataFrame(columns=og_columns)

with open(query_csv, "w") as query_f, open(og_csv, "w") as og_f:
    query_writer = csv.writer(query_f, delimiter=",")
    og_writer = csv.writer(og_f, delimiter=",")
    
    # Write column labels 
    query_writer.writerow(["query_id"] + queries.columns.tolist())
    og_writer.writerow(og_objects.columns.tolist())

    # Keep track of indices that failed during batchmode
    failed_batches = queue.Queue()

    # Initialise indices for batches
    batch_indices = chunker(urls.index, batchsize)

    # Keep appending in batches of 50
    for batch_ind in tqdm(batch_indices,
                          total=len(urls)//batchsize,
                          desc="Batches"):
        batch = urls.loc[batch_ind] 
        process_batch(batch, queries, og_objects, query_writer, og_writer, failed_batches)
    
    # Process failed batches
    pbar = tqdm(total=failed_batches.qsize()*batchsize,
                desc="Failed batches")
    while not failed_batches.empty():
        e, bad_batch = failed_batches.get()
        print(e, bad_batch)
        if len(bad_batch) > 4:
            batch_indices = chunker(bad_batch, math.ceil(len(bad_batch)/2))
                
            for batch_ind in batch_indices:
                batch = urls.iloc[batch_ind]
                
                q_len = failed_batches.qsize()
                process_batch(batch, queries, og_objects, query_writer, og_writer, failed_batches)
                if failed_batches.qsize() == q_len:
                    pbar.update(len(batch_ind))
                    
        else:
            for i in bad_batch:
                process_url(urls.loc[i], queries, og_objects, query_f, og_f)
                pbar.update(1)
    pbar.close()

