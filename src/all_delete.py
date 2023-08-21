import os
import re
import time

import requests
from bs4 import BeautifulSoup

def cut_meshi(id, meal, csrf_token,session):
    data = {"id": id, "meal": meal}  # reserve_idを適切な値に置き換える  # meal_timeを適切な値に置き換える
    headers = {"X-CSRF-TOKEN": csrf_token}  # CSRFトークンの値を設定する
    url = "https://www.ishikawatoyama.jp/kisshoku/student/reserve/update"
    response = session.post(url, headers=headers, data=data)
    if response.status_code == 200:
        json_data = response.json()
        print("ok")
    else:
        print("Request failed with status code:", response.status_code)

def delete_all_meals():
    # ログインするための情報
    login_url = "https://www.ishikawatoyama.jp/kisshoku/student/login"
    # ここに自分のパスワードを入力

    # セッションを作成
    session = requests.Session()

    # ログインページにアクセスしてHTMLを取得
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # CSRFトークンを抽出
    csrf_token = soup.find("input", {"name": "_token"})["value"]

    # ログインに必要なデータを作成
    data = {
        "_token": csrf_token,
        "email": os.environ["email"],
        "password": os.environ["password"],
    }

    # ログインリクエストを送信
    login_response = session.post(login_url, data=data)
    html_code = session.get(
        "https://www.ishikawatoyama.jp/kisshoku/student/reserve"
    ).text
    soup = BeautifulSoup(html_code, "html.parser")
    # 中にspanタグを持ち、classがicon-not-availableのbutton要素を抽出
    target_buttons = soup.find_all("button", class_="canteen-icon")
    filtered_buttons = [
        button
        for button in target_buttons
        if button.find("span", class_="icon-available")
    ]
    # soupの中からmeta name="csrf-token"のcontentを取得
    csrf_token = soup.find("meta", attrs={"name": "csrf-token"}).get("content")
    csrf_token
    eat_data = []
    pattern = re.compile(r"reserveChange\(this, (\d+), (\d+)\)")
    for button in filtered_buttons:
        onclick_value = button.get("onclick")
        match = pattern.search(onclick_value)
        if match:
            second_argument = match.group(1)
            third_argument = match.group(2)
            eat_data.append([int(second_argument), int(third_argument)])

    for ed in eat_data:
        cut_meshi(ed[0], ed[1], csrf_token,session)
        time.sleep(5)
