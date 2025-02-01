import time
import re
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, ConnectionError, HTTPError, Timeout
import logging
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from pathlib import Path

# 定数の定義
RAKUTEN_SEARCH_URL = "https://search.rakuten.co.jp/search/mall/"
ITEM_ID_PATTERN = re.compile(r'https://item\.rakuten\.co\.jp/[^/]+/([^/?]+)')
COLUMNS = ['ランキング', '検索商品IDフラグ', '商品URL', '商品名']

def execute_search(keyword, page_number, search_item_id, shop_id):
    """検索実行関数"""
    logging.info('execute_searchに入りました')
    logging.info(f'キーワード{keyword}')
    logging.info(f'ページナンバー{page_number}')
    logging.info(f'検索ID{search_item_id}')
    logging.info(f'ショップID{shop_id}')

    output_df = pd.DataFrame(columns=COLUMNS)
    rank_count = 1
    total_product_count = 0

    # 引数のチェック
    error_message = inputcheck(keyword, page_number, search_item_id, shop_id)
    if error_message:
        logging.error(error_message)
        return error_message

    for i in range(page_number):
        logging.info(f'for文に入りました{i + 1}回目')
        url = create_search_url(keyword, i + 1)
        logging.info(f'検索URL{url}')
        product_cards, product_count = fetch_product_cards(url)
        if product_cards :
            logging.info('fetch_product_cards後のproduct_cardsあり')
        else :
            logging.info('fetch_product_cards後のproduct_cardsなし')
        logging.info(f'商品カウント{product_count}')

        total_product_count += product_count

        for product_card in product_cards:
            logging.info(f'product_card{product_card}')
            if not check_pr_in_title(product_card):
                shop_info_dict = extract_shop_info(product_card)
                # logging.info(f'shop_info_dict: {shop_info_dict}')

                item_id_flg = '○' if shop_info_dict['item_id'] == search_item_id and shop_info_dict['url'].split('/')[3] == shop_id else ''
                output_df.loc[len(output_df)] = [
                    rank_count,
                    item_id_flg,
                    shop_info_dict['url'],
                    shop_info_dict['name']
                ]
                rank_count += 1

        time.sleep(0.5)

    filepath = output_csv(output_df)
    path_parts = Path(filepath).parts

    if len(path_parts) >= 3:
        last_two_dirs = os.path.join(path_parts[-2], path_parts[-1])
    else:
        last_two_dirs = None

    result = (
        f'検索ワード: {keyword}\nページ数: {page_number}\n商品ID: {search_item_id}\n店舗ID: {shop_id}\n\n'
        '上記の条件でスクレイピングが完了しました\n'
        f'CSVファイルが {last_two_dirs} に保存されました。'
    )
    return result

def inputcheck(keyword, page_number, item_id, shop_id):
    """引数のチェックメソッド"""
    if not keyword:
        return "検索キーワードが指定されていません"
    if not page_number:
        return "検索ページ数が指定されていません"
    if not item_id:
        return "商品IDが指定されていません"
    if not shop_id:
        return "店舗IDが指定されていません"
    if not re.fullmatch(r'^[0-9a-zA-Z-_"!#$%&\'()*+,\-.;=<>\?@[\\\]^_`{|}~]+$', item_id):
        return "商品IDは半角英数字および記号である必要があります"
    return None

def create_search_url(keyword, page_index):
    """検索URLの作成メソッド"""
    return urljoin(RAKUTEN_SEARCH_URL, quote(keyword) + f"/?p={page_index}")

def fetch_product_cards(url):
    """商品カードを取得するメソッド"""
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Google Chromeのユーザーエージェントを指定
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
        
        # WebDriverの設定
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(url)
        
        # 動的コンテンツの読み込みを待つ
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "searchresultitem"))
        )
        
        # ページのHTMLを取得
        page_source = driver.page_source
        if page_source :
            logging.info('page_sourceあり')
        else :
            logging.info('page_sourceなし')
        
        search_html = BeautifulSoup(page_source, "html.parser")
        if search_html :
            logging.info('search_htmlあり')
        else :
            logging.info('search_htmlなし')
        
        # HTMLを保存してデバッグ（デバッグの時に解除）
        # with open('debug_page_source.html', 'w', encoding='utf-8') as f:
        #     f.write(page_source)
        
        # 商品カードを取得
        product_cards = search_html.find_all(
            class_="dui-card searchresultitem overlay-control-wrapper--3KBO0 title-control-wrapper--1rzvX"
        )
        if not product_cards :
            product_cards = search_html.find_all(
            class_="dui-card searchresultitem overlay-control-wrapper--2W6PV title-control-wrapper--1YBX9"
        )

        if product_cards :
            logging.info('product_cardsあり')
        else :
            logging.info('product_cardsなし')
        
        driver.quit()
        
        return product_cards, len(product_cards)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return [], 0

def check_pr_in_title(product_card):
    """PR判定メソッド"""
    title_element = product_card.find('div', class_='title--2KRhr title-grid--18AUw').find(
        'a', class_='title-link--3Yuev'
    )
    # title_element = product_card.find('div', class_='title--I67Sk title--zfJkV title-grid--XKKDL').find(
    #     'a', class_='title-link--3Ho6z'
    # )
    logging.info(f"リンクテキストの内容: {title_element}")
    logging.info(f"リンクテキストのタイトル: {title_element.get_text()}")
    if title_element is not None:
        return '[PR]' in title_element.get_text()
    else:
        return False


def extract_shop_info(product_card):
    """product_cardからショップURL、ショップ名、商品IDを取得するメソッド"""
    # shop_url_decode = product_card.find('div', class_='title--I67Sk title--zfJkV title-grid--XKKDL').find(
    #     'a', class_='title-link--3Ho6z')['href']
    # shop_name = product_card.find('div', class_='title--I67Sk title--zfJkV title-grid--XKKDL').find(
    #     'a', class_='title-link--3Ho6z').text
    # item_id_pattern_match = ITEM_ID_PATTERN.search(shop_url_decode)
    # item_id = item_id_pattern_match.group(1) if item_id_pattern_match else None

    shop_url_decode = product_card.find('div', class_='title--2KRhr title-grid--18AUw').find(
        'a', class_='title-link--3Yuev')['href']
    shop_name = product_card.find('div', class_='title--2KRhr title-grid--18AUw').find(
        'a', class_='title-link--3Yuev').text
    item_id_pattern_match = ITEM_ID_PATTERN.search(shop_url_decode)
    item_id = item_id_pattern_match.group(1) if item_id_pattern_match else None
    

    return {'url': shop_url_decode, 'name': shop_name, 'item_id': item_id}

def output_csv(output_df):
    """作ったCSV（文字コードはshift_jis）を出力するメソッド"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"output_{timestamp}.csv"
    home = Path.home()
    download_folder = home / 'Downloads'
    filepath = download_folder / filename
    output_df.to_csv(filepath, index=False, encoding='cp932')
    print(f"CSVファイルが {filepath} に保存されました。")
    return filepath