import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import json
from datetime import datetime

from Service.index import imageUrlDetection
from Service.textAnalysis import detectDrugFromText
from reddit_conn import reddit


def login(driver, username, password):
    login_url = "https://www.reddit.com/login/"
    driver.get(login_url)
    time.sleep(5)
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")

    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    print("Logged in successfully")


def post_scrape(driver, keyword, maxposts=1, scroll_pause=5):
    output_data = []
    post_data = {}
    cnt = 0
    search_url = f"https://www.reddit.com/search/?q={keyword}"
    driver.get(search_url)
    time.sleep(5)

    def extract_posts():
        posts = driver.find_elements(
            By.XPATH, "//a[@data-testid='post-title-text']")
        for post in posts:
            nonlocal cnt
            nonlocal post_data
            cnt += 1
            href = post.get_attribute("href")
            text = post.text
            post_data["url"] = href
            post_data["post text"] = text
            post_data["images"] = []
            post_data["comments"] = []
            output_data.append(post_data)
            post_data = {}

    last_height = driver.execute_script("return document.body.scrollHeight")
    while (cnt <= maxposts):
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        extract_posts()
    return output_data


async def more_info_of_post(driver, post_data):
    print(len(post_data))
    for i in range(len(post_data)):
        flag = False
        search_url = post_data[i]["url"]
        driver.get(search_url)
        # try:
        #     img_elements = driver.find_elements(By.XPATH, "//img[@src]")
        #     for img in img_elements:
        #         img_res = {"url": img.get_attribute("src"), "flags": imageUrlDetection(img.get_attribute("src"))}
        #         if img_res["flags"].get("drug", 0) > 0:
        #             flag = True
        #         post_data[i]["images"].append(img_res)
        # except Exception as e:
        #     print(f"Error extracting images: {e}")
        # try:    
        #     post = reddit.submission(url=search_url)
        #     post.comments.replace_more(limit=0)
        #     post_data[i]["username"] = post.author.name if post.author else "Deleted"
        # except Exception as e:
        #     print(f"Error occured {e}")
        #     post_data[i]["username"] = "Unknown"
        try:
            comments = []
            comment_elements = driver.find_elements(By.CSS_SELECTOR, ".Comment")
            count = 0
            for element in comment_elements:
                if(count > 5):
                    break
                count += 1
                author = element.find_element(By.CSS_SELECTOR, ".Comment__author").text
                body = element.find_element(By.CSS_SELECTOR, ".Comment__body").text
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                comments.append({"username": author, "comment": body, "created_utc": timestamp})
            post_data[i]["comments"].append(comments)
        except Exception as e:
            print(f"Error extracting comments: {e}")

        post_analysis = detectDrugFromText(post_data[i])
        print(post_analysis)
        if flag or isinstance(post_analysis, dict) and post_analysis.get("potential_drug_trafficking_detected") == "true":
            yield post_analysis



async def scrape_posts(keyword):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service("/usr/lib/chromium-browser/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    '''username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("PASSWORD") 
    login(driver,username,password)'''  # Not needed for now. We can login if results are not accurate
    post_data = post_scrape(driver, keyword=keyword)
    print("Done")
    async for res in more_info_of_post(driver, post_data):
        #write to a json file
        yield res
    driver.quit()

# import asyncio
# async def main():
#     async for res in scrape_posts("weed"):
#         yield res
#         print(res)
        
# asyncio.run(main())