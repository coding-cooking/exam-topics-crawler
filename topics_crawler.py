import requests
from bs4 import BeautifulSoup
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--disable-bots")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

base_url = "https://www.examtopics.com/exams/amazon/aws-certified-solutions-architect-associate-saa-c03/view/"

data = []

try:

    for page_num in range(1, 101):
        print(f"Fetching page {page_num}...")

        url = f"{base_url}{page_num}/"
        driver.get(url)

        time.sleep(10)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'exam-question-card'))
            )
        except Exception as e:
            print(f"Timeout or error loading page {page_num}: {e}")
            driver.save_screenshot(f'page_{page_num}_error.png')
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        questions = soup.find_all('div', class_='exam-question-card')

        if not questions:
            print("No more questions found. Stopping...")
            break

        for question in questions:
            try:
                topic_id = question.find('div', class_='card-header').text.strip().split('\n', 1)[0].strip()
                topic_id = topic_id.replace('Question #', '').strip()
                question_text = question.find('p', class_='card-text').text.strip()  # Update class

                choices = []
                correct_answers = []
                for li in question.find_all('li', class_='multi-choice-item'):
                    letter = li.find('span', class_='multi-choice-letter').text.strip().replace('.', '')
                    choice_text = li.text.strip().split('\n', 1)[-1].strip()
                    choice_text = choice_text.replace('Most Voted', '').strip()

                    if 'correct-hidden' in li.get('class', []):
                        correct_answers.append(letter)

                    choices.append({'letter': letter, 'text': choice_text})

                data.append({
                    'topic_id': topic_id,
                    'question': {
                        'questionContent': question_text,
                        'questionImage': '',
                    },
                    'choices': {
                        choice['letter']: {
                            'choice_image': '',
                            'choice_text': choice['text']
                        } for choice in choices
                    },
                    'answers': correct_answers,
                })

            except Exception as question_error:
                print(f"Error processing a question on page {page_num}: {question_error}")

except requests.RequestException as e:
    print(f"Error: {e}")

finally:
    # Save the data to a JSON file
    with open('saa_c03_questions.json', 'w') as f:
        json.dump(data, f, indent=4)

    driver.quit()
