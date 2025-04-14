import os
import requests
from markitdown import MarkItDown
import logging
from bs4 import BeautifulSoup


# Create a logger for the web crawler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up directories
resources_dir = "resources"
temp_dir = ".temp"
output_dir = os.path.join(temp_dir, "web_contents")
output_images_dir = os.path.join(output_dir, "_images")


def fetch_web_pages():
    """
    Fetch web pages from a list of URLs and save their content to markdown files.
    This function reads URLs from a file named 'web_resources.txt' located in the 'resources' directory.
    It fetches the content of each URL, processes it to extract relevant information, and saves it to a markdown file.
    The markdown files are saved in the 'web_contents' directory, and a temporary directory is used for intermediate processing.
    """

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Ensure the temporary directory exists
    os.makedirs(temp_dir, exist_ok=True)

    # Read URLs from the web_resources.txt file
    web_resources_file = os.path.join(resources_dir, "web_resources.txt")
    with open(web_resources_file, "r", encoding="utf-8") as file:
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

            # Process the content of the web page
            process_url_content(url, response)

        except Exception as e:
            print(f"Failed to fetch or process {url}: {e}")


def process_url_content(url: str, response: str) -> None:
    """
    Process the content of a web page and save it to a markdown file.
    Args:
        url (str): The URL of the web page.
        response (str): The HTML content of the web page.
    """

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, features="html.parser")

    # Extract all divs with class "content"
    content_divs = "".join(div.prettify()
                           for div in soup.find_all("div", class_="content"))

    # Save content divs to a temporary HTML file
    temp_file = os.path.join(temp_dir, "temp.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(content_divs)

    # Extract text using markitdown from the temporary HTML file
    text_content = md.convert(temp_file)

    # Save the content to a markdown file
    md_file = os.path.join(
        output_dir, f"{url.replace('https://', '').replace('http://', '').replace('/', '_')}.md")

    with open(md_file, "w", encoding="utf-8") as md_file:
        md_file.write(str(text_content))

    print(f"Content saved for {url} in {md_file}")

    fetch_images(soup, url)


def fetch_images(soup, url):
    """
    Extract and save images from the content of a web page.
    Args:
        soup (BeautifulSoup): Parsed HTML content of the web page.
        url (str): The URL of the web page.
    """
    # Ensure the output images directory exists
    os.makedirs(output_images_dir, exist_ok=True)

    # Omit the last part of the URL after / to handle relative paths correctly
    url = url.rsplit('/', 1)[0]
    print(url)

    # Extract images from the content
    images = soup.find_all("img")

    # Save images to the output directory
    for img in images:
        img_url = img.get("src")
        if img_url and not img_url.startswith("http"):

            img_url = f"{url}/{img_url}"

        try:
            img_response = requests.get(img_url)
            img_response.raise_for_status()

            # Save the image
            img_name = os.path.basename(img_url)
            img_path = os.path.join(output_images_dir, img_name)

            with open(img_path, "wb") as f:
                f.write(img_response.content)

            print(f"Image saved: {img_path}")

        except Exception as e:
            print(f"Failed to fetch or save image {img_url}: {e}")


if __name__ == "__main__":
    # Create an instance of MarkItDown with no plugins enabled
    md = MarkItDown(enable_plugins=False)

    # Fetch web pages and save their content
    fetch_web_pages()
