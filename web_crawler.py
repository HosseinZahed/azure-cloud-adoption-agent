import os
import requests
from markitdown import MarkItDown
import logging
from bs4 import BeautifulSoup

# Create an instance of MarkItDown with no plugins enabled
md = MarkItDown(enable_plugins=False, )

# Create a logger for the web crawler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_web_pages():
    # Ensure the output directory exists
    output_dir = "web_contents"
    os.makedirs(output_dir, exist_ok=True)

    # Ensure the temporary directory exists
    temp_dir = ".temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Read URLs from the web_resources.txt file
    with open("web_resources.txt", "r") as file:
        urls = file.readlines()

    for url in urls:
        url = url.strip()
        if not url:
            continue
        logger.info(f"Fetching content from {url}")

        try:
            # Fetch the web page content
            response = requests.get(url)
            response.raise_for_status()

            logger.info(f"Successfully fetched content from {url}")

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, features="html.parser")

            # Extract all divs with class "content"
            content_divs = "".join(div.prettify()
                                   for div in soup.find_all("div", class_="content"))

            # Save content divs to a temporary HTML file
            temp_file = os.path.join(temp_dir, f"temp.html")
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(content_divs)

            # Extract text using markitdown from the temporary HTML file
            logger.info(f"Converting HTML to markdown for {url}")
            text_content = md.convert(temp_file)

            # Save the content to a markdown file
            md_name = os.path.join(
                output_dir, f"{url.replace('https://', '').replace('http://', '').replace('/', '_')}.md")
            logger.info(f"Saving content to {md_name}")
            with open(md_name, "w", encoding="utf-8") as md_file:
                md_file.write(str(text_content))

            print(f"Content saved for {url} in {md_name}")
        except Exception as e:
            print(f"Failed to fetch or process {url}: {e}")


if __name__ == "__main__":
    fetch_web_pages()
