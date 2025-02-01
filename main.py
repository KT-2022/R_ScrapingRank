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

logger, log_handler = configure_logging()

# 定数の定義
IMAGE_PATH_LEFT = os.path.join(os.path.dirname(__file__), 'assets/image/search_transparent.png')
IMAGE_PATH_RIGHT = os.path.join(os.path.dirname(__file__), 'assets/image/spreadsheet_transparent.png')

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

def create_layout(page):
    """レイアウトを作成する関数"""
    global table, selection_dialog, register_item_id, register_item_name, register_dialog, itemID, register_shop_id

    query_input = ft.TextField(label="検索ワード", width=300)
    dropdown = ft.Dropdown(
        label="検索ページ数",
        value=1,
        options=[ft.dropdown.Option(i) for i in range(1, 6)],
        width=150,
        autofocus=False,
    )
    itemID = ft.TextField(label="商品ID", width=300)
    register_shop_id = ft.TextField(label="店舗ID", width=150)
    search_button = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Text("検索", size=18, color=ft.colors.WHITE),
            width=150,
            height=50,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.INDIGO_500,
            )
        ),
        padding=ft.padding.all(1)
    )
    select_button = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Text("商品ID選択", size=12, color=ft.colors.BLACK),
            width=90,
            height=40,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.WHITE,
                shape={"": ft.RoundedRectangleBorder(radius=0)},
                side=ft.BorderSide(ft.colors.BLACK54),
                padding=ft.padding.all(1)
            )
        ),
        padding=ft.padding.all(1)
    )
    register_button = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Text("商品ID登録", size=12, color=ft.colors.BLACK),
            width=90,
            height=40,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.WHITE,
                shape={"": ft.RoundedRectangleBorder(radius=0)},
                side=ft.BorderSide(ft.colors.BLACK54),
                padding=ft.padding.all(1)
            )
        ),
        padding=ft.padding.all(1)
    )
    note_text = ft.Text("※検索には数分かかることもあります", size=12, color=ft.colors.RED_900)
    progress_bar = ft.ProgressBar(width=300, visible=False)
    result_text = ft.Text()
    result_dialog = ft.AlertDialog(
        title=ft.Text("検索結果", size=15, weight=ft.FontWeight.BOLD),
        content=result_text,
        actions=[ft.TextButton("OK")]
    )

    table = ft.DataTable(
        data_row_color={
            ft.ControlState.SELECTED: ft.colors.INDIGO_100,
            },
        columns=[
        ft.DataColumn(label=ft.Text("店舗ID")),
        ft.DataColumn(label=ft.Text("商品ID")),
        ft.DataColumn(label=ft.Text("商品名"))
        ],
        rows=[]
    )
    register_item_id = ft.TextField(label="商品ID", width=200)
    register_item_name = ft.TextField(label="商品名", width=200)
    register_dialog = ft.AlertDialog(
        title=ft.Text("新しい商品を登録", size=15, weight=ft.FontWeight.BOLD),
        content=ft.Column([
            register_shop_id,
            register_item_id,
            register_item_name
        ]),
        actions=[ft.TextButton("登録")]
    )

    selection_dialog = ft.AlertDialog(
        title=ft.Text("商品ID選択"),
        content=ft.Container(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                controls=[table],
                                alignment=ft.MainAxisAlignment.START,  # 左揃えに設定
                                scroll=ft.ScrollMode.ALWAYS  # 縦横両方のスクロールを許可
                            ),
                        )
                    ],
                    scroll=ft.ScrollMode.ALWAYS  # 縦スクロールは常に有効にする
                ),
            ),
            height=400,
            width=400  # 横スクロールを考慮して幅を広めに設定
        ),
        actions=[ft.TextButton("反映")]
    )

    return query_input, dropdown, itemID, register_shop_id, search_button, select_button, register_button, note_text, progress_bar, result_text, result_dialog, selection_dialog, register_dialog

def add_elements_to_page(page, query_input, dropdown, itemID, register_shop_id, search_button, select_button, register_button, note_text, progress_bar, result_text, result_dialog, selection_dialog, register_dialog):
    """ページに要素を追加する関数"""
    image_left = ft.Image(src=IMAGE_PATH_LEFT, width=150, height=150)
    image_right = ft.Image(src=IMAGE_PATH_RIGHT, width=150, height=150)

    image_container = ft.Row(
        [image_left, image_right],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    input_container = ft.Row(
        [ft.Column([query_input], horizontal_alignment=ft.CrossAxisAlignment.START, spacing=1),
         ft.Column([dropdown], horizontal_alignment=ft.CrossAxisAlignment.START, spacing=1)],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=5
    )

    itemID_text_input_container = ft.Row(
        [itemID, register_shop_id],
        alignment=ft.MainAxisAlignment.CENTER,  # 左揃え
        spacing=5,
    )

    button_container = ft.Container(
        content = ft.Row(
            [select_button, register_button],
            alignment=ft.MainAxisAlignment.CENTER,  # 左揃え
            spacing=5
        ),
        margin=ft.margin.only(right=267)
    )

    page.add(
        ft.Column(
            [
                image_container,
                input_container,
                itemID_text_input_container,
                button_container,
                ft.Column(
                    [
                        search_button,
                        note_text
                    ],
                    spacing=5
                ),
                progress_bar
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )
    page.overlay.append(result_dialog)
    page.overlay.append(selection_dialog)
    page.overlay.append(register_dialog)

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

def update_table(selected_index=None):
    """テーブルを更新する関数"""
    global table, item_ids
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
    global selected_row_index, table, selected_item_id

    selected_row_index = -1
    selected_item_id = item_id  # 選択された商品IDを保持
    for index, row in enumerate(table.rows):
        print(f"Checking row index: {index}, with item_id: {row.cells[0].content.content.value}, row: {row}")  # デバッグ用出力
        if row.cells[0].content.content.value == item_id:
            selected_row_index = index
            break

    if selected_row_index != -1:
        print(f"Selected row found at index {selected_row_index}: {table.rows[selected_row_index]}")
        update_table(selected_row_index)  # 選択された行のインデックスを渡してテーブルを再生成
    else:
        print("選択された行が見つかりませんでした")

def on_row_selected_by_index(index, shop_id, item_id):
    """行が選択されたときの処理（インデックスベース）"""
    global item_ids, selected_item_id, selected_shop_id
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
    query_input, dropdown, itemID, register_shop_id, search_button, select_button, register_button, note_text, progress_bar, result_text, result_dialog, selection_dialog, register_dialog = create_layout(page)

    # ページに要素を追加
    add_elements_to_page(page, query_input, dropdown, itemID, register_shop_id, search_button, select_button, register_button, note_text, progress_bar, result_text, result_dialog, selection_dialog, register_dialog)

    # 商品IDをファイルから読み込む
    item_ids = load_item_ids('item_ids.txt')

    # ページに要素を追加してから、テーブルを更新
    page.update()
    update_table()

    # 検索実行時の処理
    def on_execute(e):
        search_button.content.disabled = True
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
    # テキストフィールドをクリア
        itemID.value = ""
        register_shop_id.value = ""
        page.update()
        update_table()

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
        new_shop_id = register_shop_id.value
        new_item_id = register_item_id.value
        new_item_name = register_item_name.value
        if new_item_id and new_item_name and new_shop_id:  # すべて値があることを確認
            with open('item_ids.txt', 'a', encoding='utf-8') as f:
                f.write(new_shop_id + '|' +  new_item_id + '|' + new_item_name  +'\n')
            item_ids.append((new_shop_id,new_item_id, new_item_name))  # メモリ上のリストにも追加
            register_shop_id.value = ''  # 入力フィールドをクリア
            register_item_id.value = ''  # 入力フィールドをクリア
            register_item_name.value = ''  # 入力フィールドをクリア
            update_table()  # テーブルを更新
            page.update()
        register_dialog.open = False
        page.update()

    # イベントリスナーの設定
    search_button.content.on_click = on_execute
    select_button.content.on_click = on_select
    register_button.content.on_click = on_register
    result_dialog.actions[0].on_click = close_dialog
    selection_dialog.actions[0].on_click = on_reflect
    register_dialog.actions[0].on_click = on_register_new_item

if __name__ == "__main__":
    ft.app(target=main)

    # プログラム終了時にログハンドラを閉じる
    close_logging(logger)
