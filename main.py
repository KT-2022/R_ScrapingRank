import flet as ft
import os
from search_logic import execute_search
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import random
import time
import glob
from logging_config import configure_logging, close_logging
from layout import create_layout, add_elements_to_page  # layout.py から関数をインポート

logger, log_handler = configure_logging()

def show_snackbar(page, message):
    snackbar = ft.SnackBar(
        content=ft.Text(message, color=ft.colors.WHITE, text_align = ft.TextAlign.CENTER),
        duration=3000,  # 表示時間（ミリ秒単位）
        bgcolor=ft.colors.BLACK54,
        behavior=ft.SnackBarBehavior.FLOATING  # スナックバーを浮動させる
    )
    page.snack_bar = snackbar
    page.snack_bar.open = True
    page.update()

def configure_page(page):
    """ページの設定を行う関数"""
    page.title = "楽天ランキング検索アプリ"
    page.window.width = 780
    page.window.height = 500
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)
    page.theme_mode = ft.ThemeMode.LIGHT

def load_item_ids(file_path):
    """商品IDをファイルから読み込む関数"""
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        item_ids = []
        for line in f.read().splitlines():
            parts = line.split('|')
            if len(parts) == 3:
                item_ids.append(parts)
    return item_ids

def create_gesture_detector(content, item_id):
    return ft.GestureDetector(
        content=content,
        on_tap=lambda e: on_row_selected(item_id)
    )

def update_table(table, item_ids, selected_index=None):
    """テーブルを更新する関数"""
    table.rows.clear()
    for index, item in enumerate(item_ids):
        shop_id, item_id, item_name = item
        print(f"Adding row with shop_id: {shop_id}, item_id: {item_id}, item_name: {item_name}")  # デバッグ用出力
        selected = index == selected_index
        row = ft.DataRow(
            cells=            [
                ft.DataCell(content=ft.GestureDetector(
                    content=ft.Text(shop_id),
                    on_tap=lambda e, index=index, shop_id=shop_id, item_id=item_id: on_row_selected_by_index(index, shop_id, item_id)
                )),
                ft.DataCell(content=ft.GestureDetector(
                    content=ft.Text(item_id),
                    on_tap=lambda e, index=index, shop_id=shop_id, item_id=item_id: on_row_selected_by_index(index, shop_id, item_id)
                )),
                ft.DataCell(content=ft.GestureDetector(
                    content=ft.Text(item_name),
                    on_tap=lambda e, index=index, shop_id=shop_id, item_id=item_id: on_row_selected_by_index(index, shop_id, item_id)
                ))
            ],
            selected=selected,
            on_select_changed=lambda e, index=index, shop_id=shop_id, item_id=item_id: on_row_selected_by_index(index, shop_id, item_id)  # 修正
        )
        table.rows.append(row)
        print(f"Created row: {row}")  # デバッグ用出力

    table.update()

def on_row_selected(item_id):
    """行が選択されたときの処理"""
    global selected_row_index, selected_item_id

    selected_row_index = -1
    selected_item_id = item_id  # 選択された商品IDを保持
    for index, row in enumerate(table.rows):
        print(f"Checking row index: {index}, with item_id: {row.cells[0].content.content.value}, row: {row}")  # デバッグ用出力
        if row.cells[0].content.content.value == item_id:
            selected_row_index = index
            break

    if selected_row_index != -1:
        print(f"Selected row found at index {selected_row_index}: {table.rows[selected_row_index]}")
        update_table(table, item_ids, selected_row_index)  # 選択された行のインデックスを渡してテーブルを再生成
    else:
        print("選択された行が見つかりませんでした")

def on_row_selected_by_index(index, shop_id, item_id):
    """行が選択されたときの処理（インデックスベース）"""
    global selected_item_id, selected_shop_id
    selected_item_id = item_id  # 商品IDを選択
    selected_shop_id = shop_id  # 店舗IDを選択
    print(f"選択された商品ID: {selected_item_id}, 店舗ID: {selected_shop_id}")
    for i, row in enumerate(table.rows):
        row_shop_id = item_ids[i][0]
        row_item_id = item_ids[i][1]
        row.selected = (row_shop_id == shop_id and row_item_id == item_id)  # 店舗IDと商品IDが一致した場合に選択
    table.update()

def main(page: ft.Page):
    global item_ids, table, selection_dialog, register_dialog, register_item_id, register_item_name, register_shop_id, itemID

    # 画面設定
    configure_page(page)

    # レイアウト定義
    query_input, dropdown, itemID, register_shop_id, search_button, select_button, register_button, note_text, progress_bar, result_text, result_dialog, selection_dialog, register_dialog, table, register_item_id, register_item_name = create_layout(page)

    # ページに要素を追加
    add_elements_to_page(page, query_input, dropdown, itemID, register_shop_id, search_button, select_button, register_button, note_text, progress_bar, result_text, result_dialog, selection_dialog, register_dialog)

    # 商品IDをファイルから読み込む
    item_ids = load_item_ids('item_ids.txt')

    # ページに要素を追加してから、テーブルを更新
    page.update()
    update_table(table, item_ids)

    # 検索実行時の処理
    def on_execute(e):
        search_button.content.disabled = True
        select_button.content.disabled = True
        register_button.content.disabled = True
        page.update()

        keyword = query_input.value
        page_number = int(dropdown.value)
        item_ID = itemID.value  # 商品IDをテキストフィールドから取得
        shop_ID = register_shop_id.value  # 店舗IDをテキストフィールドから取得
        progress_bar.visible = True
        page.update()

        result = execute_search(keyword, page_number, item_ID, shop_ID)

        progress_bar.visible = False
        page.update()
        search_button.content.disabled = False
        result_text.value = result
        result_dialog.open = True
        page.update()

    # ダイアログを閉じる
    def close_dialog(e):
        result_dialog.open = False
        page.update()

    # 商品ID選択時の処理
    def on_select(e):
        itemID.value = ""
        register_shop_id.value = ""
        page.update()
        update_table(table, item_ids)

        if not item_ids:  # データが空の場合
            show_snackbar(page, "商品IDデータを取得できませんでした。商品IDを登録してください。")
        else:
            selection_dialog.open = True
        page.update()

    # 商品IDを反映する処理
    def on_reflect(e):
        global selected_item_id, selected_shop_id, itemID, register_shop_id
        if selected_item_id:
            itemID.value = selected_item_id  # 確定された商品IDをテキストフィールドに反映
            register_shop_id.value = selected_shop_id  # 確定された店舗IDをテキストフィールドに反映
            print(f"選択された商品ID: {itemID.value}, 選択された店舗ID: {register_shop_id.value}")  # デバッグログ
        else:
            print("選択された商品IDがありません")
        selection_dialog.open = False
        page.update()

    # 商品IDをファイルに登録する処理
    def on_register(e):
        register_dialog.open = True
        page.update()

    # 新しい商品IDと商品名を登録する処理
    def on_register_new_item(e):
        print("on_register_new_item called")  # デバッグメッセージ追加
        new_shop_id = register_shop_id.value
        new_item_id = register_item_id.value
        new_item_name = register_item_name.value
        if new_item_id and new_item_name and new_shop_id:  # すべて値があることを確認
            with open('item_ids.txt', 'a', encoding='utf-8') as f:
                f.write(new_shop_id + '|' + new_item_id + '|' + new_item_name + '\n')
            item_ids.append((new_shop_id, new_item_id, new_item_name))  # メモリ上のリストにも追加
            register_shop_id.value = ''  # 入力フィールドをクリア
            register_item_id.value = ''  # 入力フィールドをクリア
            register_item_name.value = ''  # 入力フィールドをクリア
            update_table(table, item_ids)  # テーブルを更新
            page.update()
        else:
            print("商品ID、商品名、および店舗IDを入力してください。")  # デバッグメッセージ追加
        register_dialog.open = False
        page.update()

    # イベントリスナーの設定
    search_button.content.on_click = on_execute
    select_button.content.on_click = on_select
    register_button.content.on_click = on_register
    result_dialog.actions[0].on_click = close_dialog
    selection_dialog.actions[0].on_click = on_reflect
    register_dialog.actions[0].on_click = on_register_new_item  # イベントリスナーを設定

if __name__ == "__main__":
    ft.app(target=main)
    close_logging(logger)

