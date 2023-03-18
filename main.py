import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
import os
import zipfile
import openai


# Set your OpenAI API key
openai.api_key = "replace with your key"


def add_spaces_before_capitals(text):
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)


def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese characters
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)



def scrape_subpage(url, folder_path):
    # Send a GET request to the URL and get the page content
    page = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extract all the text content, including meta data
    all_text = soup.get_text()

    # Remove emojis from the text
    all_text = remove_emojis(all_text)
  
    # Add spaces before capital letters
    all_text = add_spaces_before_capitals(all_text)

    # Save the text content to a .txt file with the desired filename
    parsed_url = urlparse(url)
    clean_url = parsed_url.netloc.replace('www.', '')
    filename = "{} - {}.txt".format(clean_url, re.sub('[^\w\s-]', '', parsed_url.path).strip('-'))
    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(all_text)

    print(f"Scraped {url} and saved content to {file_path}")


# Input the website URL
url = input("Enter the URL of the website to scrape: ")

# Add the "http://" prefix if it's missing
if not url.startswith('http'):
    url = 'http://' + url

# Send a GET request to the URL and get the page content
page = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(page.content, 'html.parser')

# Extract all the links from the HTML content
links = []
for link in soup.find_all('a', href=True):
    href = link.get('href')
    if href.startswith('http') or href.startswith('https'):
        parsed_href = urlparse(href)
        if parsed_href.netloc == urlparse(url).netloc:
            links.append(href)
    else:
        links.append(urljoin(url, href))

# Remove duplicates from the list of links and filter out links not starting with the base URL
base_url = urlparse(url).netloc
links = set([link for link in links if link.startswith(('http://' + base_url, 'https://' + base_url))])

# Print all the links
print("List of subpage URLs:")
for link in links:
    print(link)

# Create a folder to save all the text files
parsed_url = urlparse(url)
clean_url = parsed_url.netloc.replace('www.', '')
folder_path = os.path.join(os.getcwd(), clean_url)
os.makedirs(folder_path, exist_ok=True)

# Scrape each subpage URL and save the text content as a separate file in the folder
for link in links:
    scrape_subpage(link, folder_path)

# Extract all the text content, including meta data
all_text = soup.get_text()

# Remove emojis from the text
all_text = remove_emojis(all_text)

# Add spaces before capital letters
all_text = add_spaces_before_capitals(all_text)

# Save the text content to a .txt file with the desired filename
content_filename = "{} - website_content.txt".format(clean_url)
content_file_path = os.path.join(folder_path, content_filename)
with open(content_file_path, 'w', encoding='utf-8') as file:
    file.write(all_text)

# Save the list of URLs to a .txt file with the desired filename
url_filename = "{} - subpage_urls.txt".format(clean_url)
url_file_path = os.path.join(folder_path, url_filename)
with open(url_file_path, 'w', encoding='utf-8') as file:
    for link in links:
        file.write("{}\n".format(link))

# Zip the folder with all the .txt files
zip_filename = "{}.zip".format(clean_url)
zip_file_path = os.path

# Zip the folder with all the .txt files
def create_zip_folder(folder_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

zip_filename = "{}.zip".format(clean_url)
zip_file_path = os.path.join(os.getcwd(), zip_filename)
create_zip_folder(folder_path, zip_file_path)

print(f"Website content has been saved to {content_file_path}")
print(f"List of subpage URLs has been saved to {url_file_path}")
print(f"All files have been zipped into {zip_file_path}")

# Ask the user which subpage's text they would like to send out as data to a webhook
print("\nSelect a subpage to send its text content to a webhook:")
for i, link in enumerate(links, start=1):
    print(f"{i}. {link}")

selected_link_number = int(input("Enter the number corresponding to the subpage URL: "))
selected_link = list(links)[selected_link_number - 1]

# Find the corresponding text file
parsed_url = urlparse(selected_link)
filename = "{} - {}.txt".format(clean_url, re.sub('[^\w\s-]', '', parsed_url.path).strip('-'))
file_path = os.path.join(folder_path, filename)

# Read the content of the selected subpage's text file
with open(file_path, 'r', encoding='utf-8') as file:
    selected_subpage_text = file.read()

# Send the text content to a webhook (replace 'your_webhook_url' with the actual webhook URL)
webhook_url = 'replace with your zapier webhook url'
payload = {'text': selected_subpage_text}
response = requests.post(webhook_url, json=payload)

if response.status_code == 200:
    print(f"Successfully sent the text content of {selected_link} to the webhook.")
else:
    print(f"Failed to send the text content of {selected_link} to the webhook. Status code: {response.status_code}")
