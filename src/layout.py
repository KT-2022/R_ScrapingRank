import flet as ft
import os

# 現在のスクリプトファイルのディレクトリを取得
current_dir = os.path.dirname(__file__)

# プロジェクトルートから見た画像ファイルのパスを設定
IMAGE_PATH_LEFT = os.path.join(current_dir, '..', 'assets', 'image', 'search_transparent.png')
IMAGE_PATH_RIGHT = os.path.join(current_dir, '..', 'assets', 'image', 'spreadsheet_transparent.png')

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
        actions=[ft.TextButton("削除") , ft.TextButton("反映")]  # 削除ボタンを追加
    )

    # 必要な変数のリストをすべて返すように更新
    return query_input, dropdown, itemID, register_shop_id, search_button, select_button, register_button, note_text, progress_bar, result_text, result_dialog, selection_dialog, register_dialog, table, register_item_id, register_item_name

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
        content=ft.Row(
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
