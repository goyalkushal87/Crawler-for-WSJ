import re
import csv
import time
import requests
import newspaper
import nltk
import spacy
nltk.download('punkt')
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.parser import parse
from newspaper import Article
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class NewspaperScraper:
    def __init__ (self, newspaper, searchTerm, dateStart, dateEnd):
        self.newspaper = newspaper
        self.searchTerm = searchTerm
        self.dateStart = parse(dateStart)
        self.dateEnd = parse(dateEnd)
        self.links = []

    def get_newspaper_name (self):
        return self.newspaper

    def get_pages (self):
        print ('Unimplemented for ' + self.newspaper + ' scraper')
        return

    def check_dates (self, date):
        print("------------------------------")
        page_date = parse(date)
        #print(self.dateStart <= page_date,page_date <= self.dateEnd)
        print(page_date,"----------------", self.dateStart)
        if page_date >= self.dateStart and page_date <= self.dateEnd:
            return True
        return False

    def newspaper_parser (self, sleep_time=0):
        print ('41 running newspaper_parser()...')

        results = []
        count = 0
        #print(self.links)
        for l in self.links:
            
            article = Article(url=l)
            try:
                article.build()
                print(article.summary)
            except:
                time.sleep(60)
                continue

            data = {
                'title': article.title,
                'date_published': article.publish_date,
                'news_outlet': self.newspaper,
                'authors': article.authors,
                'feature_img': article.top_image,
                'article_link': article.canonical_link,
                'keywords': article.keywords,
                'movies': article.movies,
                'summary': article.summary,
                'text': article.text,
                'html': article.html
            }

            print (data['title'])
            #print(data['publish_date'])
            #print (data['text'])
            #print("")
            print("")
            results.append(data)

            count += 1
            #print (count)
            time.sleep(sleep_time)

        return results

    def write_to_csv (self, data, file_name):
        print ('writing to CSV...')
        #print(data)
        keys = data[0].keys()
        #print(keys)
        with open(file_name, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file,fieldnames =['title', 'summary','Entity_Name','Entity_Label'])
            dict_writer.writeheader()
            dict_writer.writerows(data)

    def write_to_mongo (self, data, collection):
        print ('writing to mongoDB...')
        count = 0

        for d in data:
            collection.insert(d)
            count += 1
            print (count)


class NewspaperScraperWithAuthentication(NewspaperScraper):
    def __init__ (self, newspaper, searchTerm, dateStart, dateEnd, userID, password):
        NewspaperScraper.__init__(self, newspaper, searchTerm, dateStart, dateEnd)
        self.userId = userID
        self.password = password

        if newspaper == 'Wall Street Journal':
            self.credentials = {
                'username': userID,
                'password': password
            }
            self.login_url = 'https://id.wsj.com/access/pages/wsj/us/signin.html'
            self.submit_id = 'basic-login-submit'

    def newspaper_parser (self, sleep_time=0):
        print ('115 running newspaper_parser()...')
        results = []
        count = 0
        binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        options = Options()
        options.set_headless(headless=True)
        options.binary = binary
        capabilities_argument = DesiredCapabilities().FIREFOX
        capabilities_argument["marionette"] = True
        
        browser = webdriver.Firefox(executable_path="C:/geckodriver/geckodriver",capabilities=capabilities_argument)
        credential_names = list(self.credentials.keys())

        browser.get(self.login_url)
        cred1 = browser.find_element_by_id(credential_names[0])
        cred2 = browser.find_element_by_id(credential_names[1])
        cred1.send_keys(self.credentials[credential_names[0]])
        cred2.send_keys(self.credentials[credential_names[1]])
        #ok3=
        browser.find_element_by_class_name(self.submit_id).click()
       # browser.execute_script("arguments[0].click();",ok3)
        time.sleep(15)

        cookies = browser.get_cookies()
        browser.close()

        s = requests.Session()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])
        nlp = spacy.load('en_core_web_lg')
        for l in self.links:
            print(l)
            page = s.get(l,headers={'User-Agent': 'Custom'})
            
            soup = BeautifulSoup(page.content)
            article = Article(url=l)
            article.set_html(str(soup))
            entitiesName =""
            entitiesLabel=""

            try:               
                
                article.parse()
                article.nlp()
                doc = nlp(article.title)
                for ent in doc.ents:
                    print(ent.text, ent.label_)
                    if(ent.label_ == "ORG"):
                     entitiesName = ent.text
                     entitiesLabel = ent.label_
                
            except:
                time.sleep(60)
                continue

            
            data = {
                'title': article.title,
                'summary': article.summary,
                'Entity_Name': entitiesName,
                'Entity_Label':entitiesLabel
            }

            print (article.title)
            print(article.summary)
            
            results.append(data)
            time.sleep(sleep_time)

            count += 1
            print (count)

        return results



class WSJScraper(NewspaperScraperWithAuthentication):
    def get_pages (self, sleep_time=3):
        print ('running get_pages()...')

        links = []
        stop = False
        index = 1
        print( self.searchTerm)
        liknsed =  'https://www.wsj.com/search/term.html?KEYWORDS='+self.searchTerm.rstrip()
        
        while not stop:
            page = requests.get('http://www.wsj.com/search/term.html?KEYWORDS='
                                + self.searchTerm.rstrip()
                                + '&min-date=' + str(self.dateStart.date()).replace('-', '/')
                                + '&max-date=' + str(self.dateEnd.date()).replace('-', '/')
                                + '&page=' + str(index)
                                + '&isAdvanced=true&daysback=4y&andor=AND&sort=date-desc&source=wsjarticle,wsjblogs,sitesearch,wsjpro',
                                headers={'User-Agent': 'Custom'}
                                )
            
            soup = BeautifulSoup(page.content,features="lxml")

            if soup.find('div', class_="headline-item") is None:
                stop = True
                continue

            for result in soup.find_all('div', class_="headline-item"):
                print("-----counting------------")
                pub_date = result.find('time', class_='date-stamp-container').get_text()
                category_article =  result.find('div', class_='category').get_text()
                
                if 'min' in pub_date:
                    pub_date = str((datetime.now(timezone('EST')) - timedelta(minutes=int(pub_date[0]))).date())
                elif 'hour' in pub_date:
                    pub_date = str((datetime.now(timezone('EST')) - timedelta(hours=int(pub_date[0]))).date())
                else:
                    pub_date = pub_date.split()
                    pub_date = pub_date[0] + ' ' + pub_date[1] + ' ' + pub_date[2]
                
                if self.check_dates(pub_date) and (category_article.lower().strip()==(self.searchTerm).lower().strip() or category_article.lower().strip() == "wsj pro  "+(self.searchTerm).lower().strip()) :
                    link = result.find('h3', class_="headline")
                    print("check date counter " + category_article)
                    ltext = link.find('a').get('href')
                    
                    if 'http://' not in ltext:
                        ltext = 'http://www.wsj.com' + ltext
                        
                    if ltext not in links and 'video' not in ltext:
                        print ("----------------------------------")
                        print (ltext)
                        print ("----------------------------------")
                        links.append(ltext)
                 
                    
            index += 1
            
            time.sleep(sleep_time)

        self.links = links
        return links


    def get_section (self, href):
        href = href[22:]
        try:
            return re.search('/.*?/', href).group(0)[1:-1]
        except:
            return 'error'''
