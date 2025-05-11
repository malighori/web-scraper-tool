# Send HTTP requests To web servers and retrieve web page content
import requests
# Parses and extracts data from HTML content
from bs4 import BeautifulSoup
import time
from datetime import datetime
# Automates browser (interactions)actions to scrape JavaScript-rendered (dynamic) pages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#  Resolves domain names to IPs and performs basic port scanning.
import socket

# Function to check if the site is static
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

# Scraping content from static site
def scrape_static(url):
    """Scrape using requests and bs4"""
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    text = "\n".join(p.get_text(strip=True) for p in soup.find_all("p")[:5])
    return soup, text

# Scraping content from dynamic site
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
    return soup, text

# Extracting services from the page
def extract_services(soup):
    services = []
    for section in soup.find_all(["section", "div", "article", "main", "footer"]):
        heading = section.find(["h2", "h3", "h4"])
        if heading and any(keyword in heading.text.lower() for keyword in ["service", "solution", "what we do", "offering", "products", "we provide"]):
            service_items = section.find_all(["p", "ul", "li"])
            services.extend([item.get_text(strip=True) for item in service_items])
    return services

# Extracting categories from the page
def extract_categories(soup):
    categories = []
    for section in soup.find_all("nav"):
        category_items = section.find_all("a", href=True)
        categories.extend([category.get_text(strip=True) for category in category_items])
    return categories

# Extracting locations from the page
def extract_locations(soup):
    locations = []
    for section in soup.find_all(["section", "div"]):
        heading = section.find(["h2", "h3", "h4"])
        if heading and any(keyword in heading.text.lower() for keyword in ["locations", "contact", "our offices"]):
            location_items = section.find_all(["p", "span"])
            locations.extend([item.get_text(strip=True) for item in location_items if "address" in item.get_text().lower()])
    return locations

# Fallback Wikipedia data for company
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

# Get the IP address of the website
def get_ip_address(url):
    try:
        domain = url.split("//")[-1].split("/")[0]
        ip = socket.gethostbyname(domain)
        return ip
    except Exception as e:
        return f"Could not resolve IP: {e}"

# Basic port scan for common ports (80, 443, 21, 22, 8080)
def scan_ports(ip, ports=[80, 443, 21, 22, 8080]):
    open_ports = []
    for port in ports:
        try:
            sock = socket.socket()
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    return open_ports

# Extract blog/news post links from the page
def extract_posts(soup):
    posts = []
    for a in soup.find_all("a", href=True):
        if any(x in a["href"].lower() for x in ["/blog", "/news", "/post", "/article"]):
            posts.append(a["href"])
    return list(set(posts))  # Remove duplicates

# Main autonomous agent function
def autonomous_agent(company, url):
    log_file = "agent_log.txt"
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n\n=== Scrape Session at {datetime.now()} ===\n")
        log.write(f"Target: {company} - {url}\n")

        # Step 1: Get IP address of the site
        ip = get_ip_address(url)
        log.write(f"Resolved IP: {ip}\n")

        # Step 2: Port scan the website if IP is resolved
        if "Could not resolve" not in ip:
            open_ports = scan_ports(ip)
            log.write(f"Open Ports: {open_ports}\n")
        else:
            log.write("Skipped port scan due to DNS resolution failure.\n")

        # Step 3: Scrape content (static or dynamic)
        if is_static_site(url):
            log.write("Strategy: Static scrape\n")
            soup, content = scrape_static(url)
        else:
            log.write("Strategy: Dynamic (Selenium) scrape\n")
            soup, content = scrape_dynamic(url)

        log.write("Top Content:\n")
        log.write(content + "\n")

        # Step 4: Extract services, categories, and locations
        services = extract_services(soup)
        if services:
            log.write("Services Found:\n")
            for service in services:
                log.write(f"- {service}\n")
        else:
            log.write("No services found.\n")

        categories = extract_categories(soup)
        if categories:
            log.write("Categories Found:\n")
            for category in categories:
                log.write(f"- {category}\n")
        else:
            log.write("No categories found.\n")

        locations = extract_locations(soup)
        if locations:
            log.write("Locations Found:\n")
            for location in locations:
                log.write(f"- {location}\n")
        else:
            log.write("No locations found.\n")

        # Step 5: Extract blog/news posts if available
        posts = extract_posts(soup)
        if posts:
            log.write("Possible blog/news/article links:\n")
            for post in posts:
                log.write(f"- {post}\n")
        else:
            log.write("No obvious post/article links found.\n")

        # Step 6: Scrape Wikipedia for structured data
        log.write("\nStructured Data (Wikipedia):\n")
        wiki_data = scrape_wikipedia(company)
        for key, val in wiki_data.items():
            log.write(f"{key}: {val}\n")

        print(f"[{datetime.now()}] Agent finished scraping {company}")

# Function to ensure the URL is correctly formatted
def ensure_https(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

# Main loop to run every 60 seconds (adjust as needed)
if __name__ == "__main__":
    TARGET_URL = input("Enter the website URL to scrape (e.g., https://www.tesla.com/): ").strip()
    TARGET_URL = ensure_https(TARGET_URL)  
    
    # Extract domain name from URL (used as company name)
    TARGET_COMPANY = TARGET_URL.split("//")[-1].split("/")[0]

    while True:
        autonomous_agent(TARGET_COMPANY, TARGET_URL)
        time.sleep(60) 