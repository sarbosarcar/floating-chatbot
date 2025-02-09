from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
import json
import requests

# Setup Chrome with headless mode for faster processing
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in background
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

BASE_URL = "https://srijanju.in"
def scrape(link):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    time.sleep(2)  # Wait for JavaScript to load

    page_data = {
        "url": link,
        "title": driver.title,
        "links": [],
        "content": ""
    }
    for a_tag in driver.find_elements(By.TAG_NAME, "a"):
        href = a_tag.get_attribute("href")
        if href:
            if "@" in href:
                page_data["links"].append({
                    "text": f"Mail ID : {a_tag.text}",
                    "href": href,
                })
            elif href.startswith("tel:"):
                page_data["links"].append({
                    "text": f"Phone Number : {a_tag.text}",
                    "href": href,
                })
            else:
                page_data["links"].append({
                    "text": a_tag.text,
                    "href": href,
                })
    grouped_content = {}
    current_header = None
    content=""
    for element in driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6 | //p"):
        # if element.tag_name.startswith('h'):
        #     current_header = element.text
        #     grouped_content[current_header] = []
        # elif element.tag_name == 'p' and current_header:
        #     grouped_content[current_header].append(element.text)
        #     page_data[current_header] = element.text
        content += element.text + "\n"
        page_data["content"] = content

    driver.quit()
    return page_data

def extract_links(link):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    time.sleep(2)  # Wait for JavaScript to load
    pdf = []
    links = set()
    for a_tag in driver.find_elements(By.TAG_NAME, "a"):
        href = a_tag.get_attribute("href")
        if href=="/":
            continue
        elif href==BASE_URL:
            continue
        elif href and href.endswith(".pdf"):
            pdf.append(href)
        elif href and BASE_URL in href:  # Ensure the link belongs to the same domain
            links.add(href)
        elif href and href.startswith("/"):  # Convert relative links to absolute
            links.add(BASE_URL + href)

    driver.quit()
    links.discard(BASE_URL)
    return list(links), pdf

def main(url, visited=set()):
    content = []
    content.append(scrape(url))
    links, pdfs = extract_links(url)
    print(links)
    for link in links:
        try:
            if link in visited:
                continue
            else:
                visited.add(link)
                print(visited)
                print(f"Scraping: {link}")
                content.append(scrape(link))
        except Exception as e:
            print(f"Error: {e}")
            try:
                print(f"Retrying: {link}")
                content.append(scrape(link))
            except Exception as e:
                print(f"Failed to scrape: {link}")
                continue
    with open('data/content.json', 'a') as file:
        json.dump(content, file, indent=4)

    #save PDFs
    for pdf in pdfs:
        #save pdf to data folder
        pdf_response = requests.get(pdf)
        pdf_name = os.path.join('data', os.path.basename(pdf))
        with open(pdf_name, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)

main(BASE_URL, set())
main("https://srijanju.in/events/", set(BASE_URL))