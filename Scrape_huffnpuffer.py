# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 14:14:37 2023

@author: benjamin becel
"""

import requests
from bs4 import BeautifulSoup
import csv
from collections import deque
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tqdm import tqdm
import demoji
import pandas as pd 
import ast
from collections import Counter
import matplotlib.pyplot as plt
from textblob import TextBlob
import numpy as np
import time
import os




class Scraper:
    def __init__(self, base_url,browser = "chrome"):
        

        BROWSER_INIT = {
                        'chrome' :{ 'driver':webdriver.Chrome,  'service':ChromeService, 'manager':ChromeDriverManager,      'options':ChromeOptions },
                        'firefox':{ 'driver':webdriver.Firefox, 'service':FirefoxService,'manager':GeckoDriverManager,       'options':FirefoxOptions},
                        'edge'   :{ 'driver':webdriver.Edge,    'service':EdgeService,   'manager':EdgeChromiumDriverManager,'options':EdgeOptions   }
                        }
        
        if browser not in BROWSER_INIT.keys():
            raise Exception("Browser not supported")
        
        
        driver  = BROWSER_INIT[browser]['driver']
        manager = BROWSER_INIT[browser]['manager']
        service = BROWSER_INIT[browser]['service'](manager().install())
        options = BROWSER_INIT[browser]['options']()
        options.add_argument('--headless')

        self.driver = driver(service=service, options=options)
                
        self.base_url = base_url
        self.session = requests.Session()

    
def find_products_href():
    base_url = "https://www.huffandpuffers.com"
    next_page_address = {'href':"/collections/disposable-salt-nicotine-devices"}
    products = []

    while next_page_address is not None: 

        url = base_url + next_page_address['href']
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to load page {}\n Status code: {}".format(url, response.status_code))
        
        soup = BeautifulSoup(response.content, 'html.parser')

        #Get all product from the current page
        for product in soup.find_all('product-item', class_='product-item'):
            products.append(product.find('a',class_='product-item-meta__title')['href'])


        next_page_address = soup.find('nav', class_='pagination__nav').find('a', rel='next')
        #continues if next_page_address is not None
    
    return products

        
# Read the last row of the CSV file
def get_start_idx(csvpath, products):
    with open(csvpath, "r",encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=";")
        last_row = deque(csvreader, maxlen=1)[0]  # read last row
        if last_row[0] == 'product' : #last row = header so no data imported yet
            scrape_from_idx = 0
        else : 
            scrape_from_idx = products.index("/products/"+last_row[0])+1
    print(f"Scrap item from item number : {scrape_from_idx}.")
    return scrape_from_idx
        


def main(csvpath, base_url):
    
    products_hrefs = find_products_href()
    scrape_from_idx = get_start_idx(csvpath, products_hrefs)

    scraper = Scraper(base_url = base_url,browser='edge')

    try:

        with open(csvpath, "a", newline="", encoding="utf-8") as csvfile : 

            for product_href in tqdm(products_hrefs[scrape_from_idx:]) :
                url = base_url+product_href
                response = scraper.session.get(url)
                if response.status_code != 200:
                    raise Exception("Failed to load page {}\n Status code: {}".format(url, response.status_code))
                
                soup = BeautifulSoup(response.content, 'html.parser')

                #Get flavor option and price per option
                options = []
                option_flavor = soup.find('div', class_='product__info').find('select', class_="select").find_all("option")
                for i in option_flavor :
                    options.append({'option' : i.string.split(' - $')[0],
                                    'price' : float(i.string.split(' - $')[1])})

                #Get description and ingredient
                description_ingredient = soup.find_all("div", class_="product-tabs__tab-item-content rte")

                #Get specification and package content
                description = description_ingredient[0].find_all('ul')
                specification = [x.text for x in description[0].find_all('li')]
                package_content = [x.text for x in description[-1].find_all('li')]

                #Get ingredient
                try : 
                    soup_ingredient = description_ingredient[1].find('span', class_="metafield-multi_line_text_field")
                    ingredient = [x for x in soup_ingredient.text.split('\n')]
                except :
                    ingredient = ['Not shared']

                #Reviews part
                
                #Get average note
                average_score = soup.find('div', class_="okeReviews-badge okeReviews-badge--large okeReviews-badge--rating")
                if average_score is not None:
                    average_score = average_score.find_all('span')
                    average_score = float(average_score[1].string)

                #Get nomber of reviews    
                nb_review = soup.find('div', class_="okeReviews-reviewsAggregate")
                if nb_review is not None:
                    nb_review = int(nb_review["data-oke-reviews-review-count"])
                else:
                    nb_review = 0                  

                #Get dsitribution of the rating 
                scores_distribution = soup.find_all('div', class_="okeReviews-ratingDistribution-item-value-count")
                scores_distribution = [i.text.split('\n')[1].split(' ')[0] for i in scores_distribution]
                if len(scores_distribution) == 5:
                    scores_distribution = {5 : int(scores_distribution[0]),
                                            4 : int(scores_distribution[1]),
                                            3 : int(scores_distribution[2]),
                                            2 : int(scores_distribution[3]),
                                            1 : int(scores_distribution[4])}
                else:
                    scores_distribution = {5 : None,
                                            4 : None,
                                            3 : None,
                                            2 : None,
                                            1 : None}                        

                #Get Recommanded value
                recommand = soup.find('span', class_="okeReviews-reviewsAggregate-recommends-badge okeReviews-badge okeReviews-badge--recommended")
                if recommand is not None:
                    try:                        
                        recommand = int(nb_review.text[:-1])
                    except:
                        recommand = None

                #Get caracteristic scores (flavor,sweetness,long lasting)
                values = []

                soup_caracteristic = soup.find('div', class_="okeReviews-reviewsAggregate-mod-itm okeReviews-reviewsAggregate-mod-itm--attRtgAv")
                if soup_caracteristic is not None:
                    soup_caracteristic = soup_caracteristic.find_all('div',class_="or-rg-bar-bg")
                    for text_score in soup_caracteristic : 
                        temp = text_score['style'].split(' ')
                        values.append(float(temp[1][:-1])) 

                    caracteristics_scores = {'flavor' : values[0],
                                            'sweetness' : values[1],
                                            'long_lasting' : values[2]}
                else:
                    caracteristics_scores = {'flavor' : None,
                                            'sweetness' : None,
                                            'long_lasting' : None}


                # Load the page
                scraper.driver.get(url)
                next_button_list = scraper.driver.find_elements(By.XPATH, '//button[@class="okeReviews-reviews-showMore okeReviews-showMore js-okeReviews-showMore"]')
                if len(next_button_list) > 0:                            
                    # Find the button element to load all the review                    
                    button_element = scraper.driver.find_element(By.XPATH, '//button[@class="okeReviews-reviews-showMore okeReviews-showMore js-okeReviews-showMore"]')
                    #Get the review
                    reviews = scraper.driver.find_elements(By.XPATH,'//div[@class="okeReviews-reviews-main js-okeReviews-reviews-main"]//div[@class="js-okeReviews-reviewContent okeReviews-review-main-content-body"]')            
                    
                    secur = 0
                    while len(reviews) != nb_review and secur < 100000:
                        
                        time.sleep(0.2)
                        # checl if button is present
                        if EC.presence_of_element_located((By.XPATH, '//button[@class="okeReviews-reviews-showMore okeReviews-showMore js-okeReviews-showMore"]')):
                            # scroll view centered to the button
                            scraper.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_element)
                            
                            try:
                                # Click the button            
                                WebDriverWait(scraper.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="okeReviews-reviews-showMore okeReviews-showMore js-okeReviews-showMore"]'))).click()                        
                            except:
                                nb_review = len(reviews)

                        #Get the review
                        reviews = scraper.driver.find_elements(By.XPATH,'//div[@class="okeReviews-reviews-main js-okeReviews-reviews-main"]//div[@class="js-okeReviews-reviewContent okeReviews-review-main-content-body"]')
                        secur += 1
                    #Create a list of the comments
                    comments = []
                    for review in tqdm(reviews) :
                        comment = review.text
                        comments.append(demoji.replace_with_desc(comment)) # Also replace emoji for sentence to facilitate export

                    #Agregate result
                    product_info = {"product" : product_href.split('/')[2],
                                    "options" : options,
                                    "average_score" : average_score,
                                    "recommand" : recommand,
                                    "specifications" : specification,
                                    "package_content" : package_content,
                                    "ingredients" : ingredient,
                                    "nb_review" : nb_review,
                                    "scores_distribution" : scores_distribution,
                                    "caracteristics_scores" : caracteristics_scores,
                                    "reviews" : comments}
                else:
                    print('no review')
                    #Agregate result
                    product_info = {"product" : product_href.split('/')[2],
                                    "options" : options,
                                    "average_score" : None,
                                    "recommand" : None,
                                    "specifications" : specification,
                                    "package_content" : package_content,
                                    "ingredients" : ingredient,
                                    "nb_review" : 0,
                                    "scores_distribution" : None,
                                    "caracteristics_scores" : None,
                                    "reviews" : None}
                
                
                fieldnames = list(product_info.keys())  # Get the keys of the dictionary
                csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter = ";")
                
                # Write the header row if the file is empty
                if csvfile.tell() == 0:
                    csvwriter.writeheader()

                csvwriter.writerow(product_info)
    except Exception as e:
        print(e)
        scraper.driver.quit()
        raise e
    
#Fonction for analysis

#Correction from to the imported data 
def str_to_structured (data):
    for column in data.columns :
        if data[column].dtype == object :
            data[column] = data[data['nb_review']>0][column].apply(ast.literal_eval)
    return data

#Most_commun_words
def most_commun_words (texts,n):
    # Join all the texts together into a single string
    all_text = " ".join(texts)

    # Split the string into individual words
    words = all_text.split()
    
    # Words to remove
    words_to_remove = ['the', 'and', 'I','a','it','is','i','to','of','was','but','this','are','my','for']

    # Remove specific words from the list of words
    words = [word for word in words if word.lower() not in words_to_remove]
    
    # Count the frequency of each word
    word_counts = Counter(words)

    # Get the two most common words and their frequencies
    most_common_words = word_counts.most_common(n)
    return most_common_words

#Graph to most commun words
def show_most_commun_words (data) :
    # Initialize an empty dictionary to store the word counts
    word_counts = {}

    # Loop through each sublist in the input data
    for sublist in data:
        # Loop through each tuple in the sublist
        for word, count in sublist:
            # Add the count to the existing count for the word, or initialize the count to zero
            word_counts[word] = word_counts.get(word, 0) + count

    # Sort the word_counts dictionary by count in descending order
    word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    # Get the list of words and their counts
    words = [x[0] for x in word_counts]
    counts = [x[1] for x in word_counts]

    # Set the size of the figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Create a bar chart of the summed count of each word
    ax.bar(words[:20], counts[:20])
    ax.set_xlabel('Word')
    ax.set_ylabel('Count')
    ax.set_title('Summed Count of Words')
    plt.show()
    
#Return the best caracteristic of a product
def best_caracteristic (caracterictics):
    caracterictics_score = sorted(caracterictics.items(), key=lambda x: x[1], reverse=True)
    return caracterictics_score[0]

#Print how many product as each best carateristic
def show_best_caracteristic (data) :
    count_best_carac = Counter(data.apply(lambda x : x[0]))
    
    # Set the size of the figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Create a bar chart of the summed count of each word
    ax.bar(count_best_carac.keys(),count_best_carac.values())
    ax.set_xlabel('caracteristic')
    ax.set_ylabel('Count')
    ax.set_title('Summed Count of the best caracteristics')
    plt.show()
    
#Note for each carac when prefered
def note_by_best_caracteristic (data):
    avg_note_carac = {"flavor" : 0, "long_lasting" : 0, "sweetness" : 0}
    for i in avg_note_carac.keys() : 
        avg_note_carac[i]  = data[data['best_caracteristic'].apply(lambda x : x[0])==i]['average_score'].mean()
    return avg_note_carac

#Show a graph corelation between score and caracteristic
def show_note_by_caracteristic (data,caracteristic):
    graph = {'x' : [],'y' : []}
    graph['x'] = list(data['caracteristics_scores'].apply(lambda x : x[caracteristic]))
    graph['y'] = list(data['average_score'])
    
    graph = sorted(graph.items(), key=lambda x: x[0], reverse=True)
    
    # Set the size of the figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Create a bar chart of the summed count of each word
    ax.scatter(graph[1][1],graph[0][1])
    ax.set_xlabel(caracteristic)
    ax.set_ylabel('Average article note')
    ax.set_title(f'Article note by {caracteristic} score')
    plt.show()
    
#Get the polarity of a pull of rewiews
def polarity_review (reviews) :
    list_polarity = []
    for review in reviews :
        blob = TextBlob(review)
        list_polarity.append(blob.sentiment.polarity)
        
    return np.mean(list_polarity)
    

if __name__ == "__main__":
    csvpath = "product_huff_puffer.csv"
    base_url = "https://www.huffandpuffers.com/"

    if not os.path.exists(csvpath) : #If the file doesn't exist, create it and add the header
        with open(csvpath, "w", newline="") as csvfile :
            csvwriter = csv.writer(csvfile, delimiter=";")
            csvwriter.writerow(["product","options","average_score","recommand","specifications","package_content","ingredients","nb_review","scores_distribution","caracteristics_scores","reviews"])


    main(csvpath, base_url)