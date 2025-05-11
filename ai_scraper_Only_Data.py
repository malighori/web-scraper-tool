import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def is_static_site(url):
    """Try fetching with requests. If basic tags exist, it's likely static."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        if soup.find("h1") or soup.find("p"):
            return True
    except:
        pass
    return False

def scrape_static(url):
    """Scrape using requests and bs4"""
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    text = "\n".join(p.get_text(strip=True) for p in soup.find_all("p")[:5])
    return text

def scrape_dynamic(url):
    """Scrape using headless browser"""
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # wait for JavaScript
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    text = "\n".join(p.get_text(strip=True) for p in soup.find_all("p")[:5])
    driver.quit()
    return text

def scrape_wikipedia(company):
    """Fallback to Wikipedia for structured info"""
    url = f"https://en.wikipedia.org/wiki/{company.replace(' ', '_')}"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    info_box = soup.find("table", {"class": "infobox"})
    info = {}
    if info_box:
        for row in info_box.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                info[th.text.strip()] = td.text.strip()
    return info

def autonomous_agent(company, url):
    log_file = "agent_log.txt"
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n\n=== Scrape Session at {datetime.now()} ===\n")
        log.write(f"Target: {company} - {url}\n")

        if is_static_site(url):
            log.write("Strategy: Static scrape\n")
            content = scrape_static(url)
        else:
            log.write("Strategy: Dynamic (Selenium) scrape\n")
            content = scrape_dynamic(url)

        log.write("Top Content:\n")
        log.write(content + "\n")

        log.write("\nStructured Data (Wikipedia):\n")
        wiki_data = scrape_wikipedia(company)
        for key, val in wiki_data.items():
            log.write(f"{key}: {val}\n")

        print(f"[{datetime.now()}] Agent finished scraping {company}")

# Run every 10 seconds
TARGET_COMPANY = "Tesla, Inc."
TARGET_URL = "https://www.tesla.com/"

if __name__ == "__main__":
    while True:
        autonomous_agent(TARGET_COMPANY, TARGET_URL)
        time.sleep(60)
