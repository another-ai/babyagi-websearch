import requests
from bs4 import BeautifulSoup
import os
import re
import importlib
from extensions.doc_embedding import text_loader
import requests
from lxml import etree
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import os
import re
import importlib
import random
from newspaper import Article
import math


user_agents_list = [
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15',
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0',
   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/98.0.1108.43'
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
}

# OS configuration
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
STORAGE_PATH = os.getenv("SCRAPE_SOURCE_PATH", "") + "/scraper"


def web_search_tool(query: str, num_extracts: int, mode: str):
    links = []
    search_results = []

    # Google API search
    if mode == "google":
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query,
            "num": num_extracts,
            "start": 1
        }
        search_results = requests.get(url, params=params, timeout=5)

        if search_results.status_code == 200:
            try:
                json_data = search_results.json()
                if "items" in json_data:
                    search_results = json_data["items"]
                else:
                    print("Error: No items found in the response.")
                    search_results = []
                    if SERPAPI_API_KEY:
                        mode = "serpapi"
                        print("Switching to SERPAPI mode...")
                    else:
                        mode = "browser"
                        print("Switching to browser mode...")

            except ValueError as e:
                print(f"Error while parsing JSON data: {e}")

        else:
            print("\033[90m\033[3m" + f"Error: {search_results.status_code}\033[0m")
            if search_results.status_code == 429:
                if SERPAPI_API_KEY:
                    mode = "serpapi"
                    print("Switching to SERPAPI mode...")
                else:
                    mode = "browser"
                    print("Switching to browser mode...")
    
        print("\033[90m\033[3m" + "Completed search. Now scraping results...\n\033[0m")
        links = []
        for result in search_results:
            links.append(result['link'])
            print("\033[90m\033[3m" + f"Webpage URL: {result['link']}\033[0m")

    # SERPAPI search
    if mode == "serpapi":
        search_params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": num_extracts
        }
        search_results = GoogleSearch(search_params)
        search_results = search_results.get_dict()

        try:
            search_results = search_results["organic_results"]
        except:
            search_results = {}
            mode = "browser"
            print("Switching to browser mode...")

        search_results = simplify_search_results(search_results)
        print("\033[90m\033[3m" + "Completed search. Now scraping results...\033[0m")
        links = []
        for result in search_results:
            links.append(result.get('link'))
            print("\033[90m\033[3m" + f"Webpage URL: {result.get('link')}\033[0m")
    
    # Browser search
    if mode == "browser":
        access_counter = 0
        while (access_counter < 3):
            url = f"https://duckduckgo.com/html/?q={query}"
            index = math.floor(random.random() * len(user_agents_list))
            browser_header = {  'User-Agent': user_agents_list[index]   }
                                #'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3', 
                                #'accept-encoding': 'gzip, deflate, br', 
                                #'accept-language': 'en-US,en;q=0.9,en;q=0.8' }
            search_results = requests.get(url, headers=browser_header, timeout=5)
            if search_results.status_code == 200:
                try:
                    soup = BeautifulSoup(search_results.text, 'html.parser')
                    links = []
                    i = int(0)
                    for result in soup.select("a.result__url"):
                        url = result["href"]
                        if url:
                            links.append(url)
                            print("\033[90m\033[3m" + f"Webpage URL: {url}\033[0m")
                            i+=1
                        if i >= num_extracts:
                            access_counter = 3
                            break
                    
                    print("\033[90m\033[3m" + f"Completed search with {str(browser_header)}. Now scraping results...\n\033[0m")
                
                except Exception as e:
                    print("\033[90m\033[3m" + f"Error while parsing HTML data: {e}\033[0m")
                    access_counter = 3
                    links = []
                    search_results = []
            else:
                print(f"Request status code not OK: {search_results.status_code} with {browser_header}")
                access_counter+=1
                search_results = []

    # Error handling
    if mode not in ["google", "serpapi", "browser"]:
        print(f'Error: Smart search mode "{mode}" is out-of-range.')
    if not search_results:
        print("No search results found.")

    return search_results, links


def can_import(module_name):
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False
    

def simplify_search_results(search_results):
    simplified_results = []
    for result in search_results:
        simplified_result = {
            "position": result.get("position"),
            "title": result.get("title"),
            "link": result.get("link"),
            "snippet": result.get("snippet")
        }
        simplified_results.append(simplified_result)
    return simplified_results


def web_scrape_tool(url: str):
    content = fetch_url_content(url)
    if content is None:
        return None

    #text = extract_text(content)
    text = extract_text_extended(content)
    print("\033[90m\033[3m" + f"Scraping of {url} completed with length: {len(text)}...\033[0m")
    links = extract_links(content)
    return text, links


def fetch_url_content(url: str):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching the URL: {e}")
        return ""


def extract_links(content: str):
    soup = BeautifulSoup(content, "html.parser")
    links = [link.get('href') for link in soup.findAll('a', attrs={'href': re.compile("^https?://")})]
    return links


def extract_text(content: str):
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text(strip=True)
    return text


def extract_text_extended(content: str):
    soup = BeautifulSoup(content, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()

    text_parts = [tag.get_text(strip=True) for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])]
    return " ".join(text_parts)


def extract_text_newspaper3k(url: str):
    article = Article(url)
    article.download()
    article.parse()
    return article.text


def get_sitemap_urls(sitemap_url, web_page: str):
    response = requests.get(sitemap_url)
    xml = response.content
    tree = etree.fromstring(xml)
    
    namespaces = {'ns': web_page}
    urls = [url.text for url in tree.xpath('//ns:loc', namespaces=namespaces)]  
    return urls


def text_writer(file_path: str, input: str):
    if input:
        print(f"Writing web scrape results to {file_path}...")
        with open(file_path, 'w') as f:
            f.write(input)



# List of URLs
query = {
    "Fine-tuning of Llama on customer grade computer",
    "Context size maximation for Llama",
    "Fine-tuning mechanisms for Llama training",
    "Llama training with fine-tuning on customer grade computer",
    "7B-Llama fine-tuning with CPU for maximum context size",
    "Python code for Llama fine-tuning"
    "Setting up a Llama in Python",
    "How to use Langchain",
    "LLM training and deployment in Python",
    "How to use Llama in Python"
    }

# Scrape web pages 2 levels deep and store content in text files
all_links = []
for q in query:
    search_results, links = web_search_tool(query=q, mode="google", num_extracts=10)

    for link in links:
        content, lvl2_links = web_scrape_tool(link)

        if len(content) >= 1000 and link not in all_links:
            all_links.append(link)
            page = content + "\nSource: " + link
            file_name = link.replace("https://", "").replace("http://", "").replace("/", "_")
            file_name = file_name[0:26] + ".txt"
            print(f"Copy web scrape results for {file_name} and store in {STORAGE_PATH}...\n")
            text_writer(STORAGE_PATH + "/" + file_name, page)
        
print("Web scrape completed!")
