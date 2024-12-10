import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import json
from datetime import datetime, timedelta

from reddit_conn import reddit

def login(driver,username,password):
    login_url="https://www.reddit.com/login/"
    driver.get(login_url)
    time.sleep(5)
    username_field=driver.find_element(By.NAME, "username")
    password_field=driver.find_element(By.NAME, "password")

    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    print("Logged in successfully")

def post_scrape(driver,keyword,maxposts=1,scroll_pause=5):
    output_data=[]
    post_data = {}
    cnt=0
    search_url=f"https://www.reddit.com/search/?q={keyword}"
    driver.get(search_url)
    time.sleep(5)
    
    def extract_posts():
        posts=driver.find_elements(By.XPATH, "//a[@data-testid='post-title-text']")
        for post in posts:
            nonlocal cnt
            nonlocal post_data
            cnt+=1
            href=post.get_attribute("href")
            text=post.text
            post_data["url"] = href
            post_data["post text"]=text
            post_data["img_url"]=["NA"]
            post_data["comments"]=[]
            output_data.append(post_data)
            post_data={}
    

    last_height = driver.execute_script("return document.body.scrollHeight")
    while(cnt<=maxposts):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        extract_posts()
    print(cnt)
    return output_data

def more_info_of_post(driver, post_data,commentsTimePeriod):
    start_time=time.time()-commentsTimePeriod
    for i in range(len(post_data)):
        search_url = post_data[i]["url"]
        driver.get(search_url)
        try:
            img_element = driver.find_element(By.ID, "post-image")
            img_url = img_element.get_attribute("src")
            post_data[i]["img_url"].append(img_url)
        except Exception as e:
            post_data[i]["img_url"].append("Error extracting image URL")
        post = reddit.submission(url=search_url)
        post.comments.replace_more(limit=0) 
        comments = []
        for comment in post.comments.list():
            if   start_time<= comment.created_utc <= time.time():
                timestamp = datetime.fromtimestamp(comment.created_utc).strftime("%Y-%m-%d %H:%M:%S")
                comments.append({
                    "username": comment.author.name if comment.author else "Deleted",
                    "comment": comment.body,
                    "created_utc": timestamp
                })
        print(comments)
        post_data[i]["comments"].append(comments)
    return post_data

def main():
    day=24*60*60
    commentsTimePeriod=365*day
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service("/usr/lib/chromium-browser/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    '''username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("PASSWORD") 
    login(driver,username,password)'''#Not needed for now. We can login if results are not accurate
    post_data=post_scrape(driver,"mdma+sell")
    post_data=more_info_of_post(driver,post_data,commentsTimePeriod)

    output_file = "output_data.json"
    with open(output_file, 'w') as json_file:
        json.dump(post_data, json_file, indent=4)
    driver.quit()

if __name__ == "__main__":
    main()

