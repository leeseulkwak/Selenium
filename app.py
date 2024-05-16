import os
import openai
import csv
import time
from pathlib import Path
import pygetwindow as pgw
import pyperclip
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import streamlit as st

def generate_blog_post(topic, purpose, model):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API Key not found in environment variables")

    openai.api_key = api_key

    system_prompt = f"당신은 {topic}를 잘 알고 있는 네이버 블로그 SEO 전문가입니다."
    user_prompt = f"블로그 글의 목적은 {purpose}입니다. 이 목적을 참고하여 {topic}에 대한 블로그 글을 생성해 주세요."
    assistant_prompt = f"네이버 SEO를 고려하여 글의 제목을 추천해 주세요. \
                        그리고, 추천 해시태그를 작성된 글의 끝 부분에 추가해 주세요.\
                        단락 마다 단락의 내용에 대한 소제목을 붙여 주세요."

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": assistant_prompt},
        ]
    )

    return response['choices'][0]['message']['content']

def write_to_csv(topic, purpose, blog_post, filename="blog_post1.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(['Topic', 'Description', 'Blog Post'])
        writer.writerow([topic, purpose, blog_post])

def read_csv(file_path):
    ref = []
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            blog_post = row['Blog Post']
            title, content = extract_title_and_content(blog_post)
            ref.extend([title, content])
    return ref

def extract_title_and_content(blog_post):
    lines = blog_post.split('\n')
    title = ""
    content_start_index = 0

    for i, line in enumerate(lines):
        if line.startswith("### 제목:"):
            title = line.replace('### 제목:', '').strip().strip('"')
            content_start_index = i + 1
            break

    content = '\n'.join(lines[content_start_index:])
    return title, content.strip()

def find_element(bs, value, by=0, s=0):
    bylist = [By.ID, By.NAME, By.CLASS_NAME, By.CSS_SELECTOR, By.TAG_NAME, By.LINK_TEXT, By.PARTIAL_LINK_TEXT, By.XPATH]
    bystr = bylist[by]
    if s == 0:
        return bs.find_element(bystr, value)
    else:
        return bs.find_elements(bystr, value)

def find_el(bs, value, by=3, s=0):
    return find_element(bs, value, by, s)

def input_text(bs, id, user_input, by=3):
    pyperclip.copy(user_input)
    find_el(bs, id, by).click()
    Keys = selenium.webdriver.Keys
    selenium.webdriver.ActionChains(bs).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

def fetch_categories(browser):
    categories = {}
    cate_list = find_el(browser, 'div.cm-body a', 3, 1)
    for i in range(1, len(cate_list)):
        if cate_list[i].text == "":
            continue
        categories[cate_list[i].text] = cate_list[i].get_attribute('id').replace('category', '')
    return categories

def automate_blog_posting(ref, selected_category):
    id = 'leesel133'
    pw = 'Dltmf1690##'

    browser = webdriver.Chrome()
    browser.get("https://nid.naver.com/nidlogin.login")
    input_text(browser, "input#id", id, 3)
    input_text(browser, "input#pw", pw, 3)
    submit = find_el(browser, "button[type='submit']", 3)
    submit.click()
    time.sleep(3)

    find_el(browser, 'a.MyView-module__item_link___Dzbpq', 3, 1)[2].click()
    time.sleep(1)

    find_el(browser, 'a.MyView-module__link_service___Ok8hP', 3, 1)[1].click()
    browser.switch_to.window(browser.window_handles[-1])
    time.sleep(15)

    browser.switch_to.frame("mainFrame")
    try:
        find_el(browser, 'button.btn_close._btn_close', 3).click()
    except:
        pass
    time.sleep(2)

    categories = fetch_categories(browser)
    st.session_state['categories'] = categories

    if not selected_category:
        return

    cate_menu = find_el(browser, f'a#category{categories[selected_category]}').get_attribute('href')
    browser.get(cate_menu)
    time.sleep(2)

    post_link = find_el(browser, 'a.col._checkBlock._rosRestrict').get_attribute('href')
    browser.get(post_link)
    time.sleep(8)

    browser.switch_to.window(browser.window_handles[-1])
    try:
        find_el(browser, 'button.se-popup-button.se-popup-button-cancel').click()
    except:
        pass
    time.sleep(2)

    input_text(browser, 'span.se-placeholder.__se_placeholder.se-ff-nanumgothic.se-fs32', f'{ref[0]}')
    time.sleep(5)

    input_text(browser, 'span.se-placeholder.__se_placeholder.se-ff-nanumgothic.se-fs15', f'{ref[1]}')
    time.sleep(5)

    dir_path = Path.cwd()
    file_path = dir_path / "1.jpg"

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    find_el(browser, 'button.se-image-toolbar-button.se-document-toolbar-basic-button.se-text-icon-toolbar-button.__se-sentry', 3).click()
    file_input = find_el(browser, 'input#hidden-file', 3)
    file_input.send_keys(str(file_path))
    time.sleep(5)
    window = pgw.getWindowsWithTitle('열기')[0]
    window.close()
    time.sleep(5)

    close_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.se-help-panel-close-button')))
    close_button.click()
    time.sleep(5)
    print('레이어 닫기')

    publish_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.publish_btn__m9KHH')))
    publish_button.click()
    time.sleep(5)
    print('오른 쪽 상단 발행')

    try:
        browser.execute_script("document.getElementById('open_private').click();")
        print('라디오 버튼 직접 클릭 완료')
    except Exception as e:
        print(f'오류 발생: {e}')

    publish_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.confirm_btn__WEaBq')))
    publish_button.click()
    time.sleep(5)
    print('발행 완료')

    time.sleep(10)
    browser.quit()

def main():
    st.title("Blog Post Generator")

    topic = st.text_input("주제를 입력해주세요")
    purpose = st.text_input("목적을 입력해주세요")
    model = st.radio("Choose a model", ('gpt-4-turbo-preview', 'gpt-3.5-turbo'))

    if st.button("Generate Blog Post"):
        try:
            blog_post = generate_blog_post(topic, purpose, model)
            st.success("Blog post generated successfully.")
            st.text_area("Generated Blog Post", value=blog_post, height=300)

            write_to_csv(topic, purpose, blog_post)
            ref = read_csv('blog_post1.csv')
            st.session_state['ref'] = ref

            automate_blog_posting(ref, None)
            st.experimental_rerun()

        except Exception as e:
            st.error(f"An error occurred: {e}")

    if 'categories' in st.session_state:
        selected_category = st.selectbox('카테고리를 선택하세요', list(st.session_state['categories'].keys()))
        
        if st.button("Publish Blog Post"):
            try:
                automate_blog_posting(st.session_state['ref'], selected_category)
                st.success("Blog post published to Naver Blog successfully.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
