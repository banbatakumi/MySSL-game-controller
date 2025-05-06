import tkinter as tk
from tkinter import ttk  # ttk を使うとモダンなウィジェットが使える
import socket
import json
import config
import threading  # GUIをフリーズさせないためにUDP送信を別スレッドで行う場合に使用
import sys  # 終了処理のため


class GameControllerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Robot Game Controller")
        master.geometry("500x600")  # ウィンドウの初期サイズ設定

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target_ip = config.GAME_COMMAND_TARGET_IP
        self.target_port = config.GAME_COMMAND_LISTEN_PORT

        # ウィンドウサイズ変更時の挙動を設定
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)  # メインフレームがウィンドウ全体に広がるように

        # メインフレーム
        main_frame = ttk.Frame(master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(
            tk.N, tk.S, tk.E, tk.W))  # ウィンドウに張り付くように配置

        # メインフレーム内のグリッド設定 (列方向の中央寄せと拡張)
        main_frame.columnconfigure(0, weight=1)
        # main_frame.rowconfigure(tk.ALL, weight=0) # 各行のweightは個別に設定する

        # --- 通信情報表示 ---
        ttk.Label(main_frame, text=f"Sending commands to: {self.target_ip}:{self.target_port}").grid(
            row=0, column=0, pady=(0, 10), sticky=tk.W)
        main_frame.rowconfigure(0, weight=0)  # 固定サイズ

        # --- ゲームコントロールボタン ---
        game_control_frame = ttk.LabelFrame(
            main_frame, text="Game Control (All Robots)", padding="10")
        game_control_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        game_control_frame.columnconfigure(0, weight=1)  # ボタンが横いっぱいに広がるように
        main_frame.rowconfigure(2, weight=0)  # 固定サイズ

        # 緊急停止ボタン
        # スタイルの定義 (緊急停止ボタンを赤くするなど)
        style = ttk.Style()
        style.configure("Emergency.TButton", foreground="red",
                        font=('TkDefaultFont', 12, 'bold'))
        self.emergency_stop_button = ttk.Button(
            game_control_frame, text="EMERGENCY STOP", command=self.send_emergency_stop_command, style="Emergency.TButton")
        self.emergency_stop_button.grid(
            row=0, column=0, pady=5, sticky=(tk.W, tk.E))

        # ゲームスタートボタン
        self.start_game_button = ttk.Button(
            game_control_frame, text="START GAME", command=self.send_start_game_command)
        self.start_game_button.grid(
            row=1, column=0, pady=5, sticky=(tk.W, tk.E))

        self.stop_game_button = ttk.Button(
            game_control_frame, text="STOP GAME", command=self.send_stop_game_command)
        self.stop_game_button.grid(
            row=2, column=0, pady=5, sticky=(tk.W, tk.E))

        # --- ロボット選択 ---
        robot_select_frame = ttk.LabelFrame(
            main_frame, text="Select Robot", padding="10")
        robot_select_frame.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        robot_select_frame.columnconfigure(0, weight=1)  # 列を均等に分割
        robot_select_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=0)  # 固定サイズ

        # ラジオボタンの変数
        self.selected_robot = tk.StringVar()
        # 初期選択を設定 (有効なロボットがあればそれをデフォルトにする)
        initial_selection = "none"
        if config.ENABLE_YELLOW_ROBOT:
            initial_selection = "yellow"
        elif config.ENABLE_BLUE_ROBOT:  # Yellowが無効でBlueが有効な場合
            initial_selection = "blue"
        self.selected_robot.set(initial_selection)

        # Yellow ロボット選択ラジオボタン
        self.yellow_radio = ttk.Radiobutton(
            robot_select_frame, text="Yellow Robot", variable=self.selected_robot, value="yellow")
        self.yellow_radio.grid(row=0, column=0, sticky=tk.W, padx=5)
        if not config.ENABLE_YELLOW_ROBOT:
            self.yellow_radio.config(state=tk.DISABLED)  # 無効なら選択不可に

        # Blue ロボット選択ラジオボタン
        self.blue_radio = ttk.Radiobutton(
            robot_select_frame, text="Blue Robot", variable=self.selected_robot, value="blue")
        self.blue_radio.grid(row=0, column=1, sticky=tk.W, padx=5)
        if not config.ENABLE_BLUE_ROBOT:
            self.blue_radio.config(state=tk.DISABLED)  # 無効なら選択不可に

        # --- ボール配置コマンド ---
        placement_frame = ttk.LabelFrame(
            main_frame, text="Ball Placement (Selected Robot)", padding="10")
        placement_frame.grid(row=4, column=0, pady=5, sticky=(tk.W, tk.E))
        placement_frame.columnconfigure(0, weight=0)  # ラベルは固定サイズ
        placement_frame.columnconfigure(1, weight=1)  # 入力欄が広がる
        placement_frame.columnconfigure(2, weight=0)  # ラベルは固定サイズ
        placement_frame.columnconfigure(3, weight=1)  # 入力欄が広がる
        placement_frame.columnconfigure(4, weight=1)  # ボタンが広がる
        main_frame.rowconfigure(4, weight=0)  # 固定サイズ

        ttk.Label(placement_frame, text="X:").grid(
            row=0, column=0, sticky=tk.W, padx=(5, 0))
        self.x_entry = ttk.Entry(placement_frame)
        self.x_entry.insert(0, str(config.BALL_PLACEMENT_TARGET_X))  # デフォルト値
        self.x_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        ttk.Label(placement_frame, text="Y:").grid(
            row=0, column=2, sticky=tk.W, padx=(5, 0))
        self.y_entry = ttk.Entry(placement_frame)
        self.y_entry.insert(0, str(config.BALL_PLACEMENT_TARGET_Y))  # デフォルト値
        self.y_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5)

        self.place_ball_custom_button = ttk.Button(
            placement_frame, text="PLACE BALL", command=self.send_place_ball_command_custom)
        self.place_ball_custom_button.grid(
            row=0, column=4, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5)

        # --- ステータス表示 ---
        self.status_label = ttk.Label(main_frame, text="", anchor=tk.CENTER)
        self.status_label.grid(row=5, column=0, pady=10, sticky=(tk.W, tk.E))
        # 最後の行（ステータスラベル）がウィンドウサイズ変更時に拡張されるように設定
        main_frame.rowconfigure(5, weight=1)

        # ウィンドウクローズ時の処理を設定
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """ウィンドウが閉じられそうになった時の処理"""
        print("Closing Game Controller GUI.")
        # ソケットを閉じる
        if self.sock:
            self.sock.close()
        self.master.destroy()
        # GUIを閉じても main.py は動き続ける。
        # main.py も終了させたい場合は、main.py に終了トリガーを送るか、
        # あるいは GUI を閉じるのではなく main.py を停止させる運用にする。
        # この例では GUI アプリケーションだけを閉じる。
        # sys.exit() はプロセス全体を終了させてしまうので、GUIだけなら不要だが、
        # 念のため残しておくとプロセスゾンビを防ぐことがある。
        # GUIを閉じても main.py を終了させたくない場合は sys.exit() は削除。

    def send_udp(self, data):
        """UDP経由でJSONデータを送信する"""
        # GUIスレッドをブロックしないように、送信処理を別スレッドで行う
        threading.Thread(target=self._send_udp_threaded,
                         args=(data,), daemon=True).start()

    def _send_udp_threaded(self, data):
        """UDP送信処理本体 (別スレッドで実行される)"""
        try:
            json_data = json.dumps(data)
            byte_data = json_data.encode('utf-8')
            self.sock.sendto(byte_data, (self.target_ip, self.target_port))
            print(f"Sent: {data}")
            # GUIの更新はGUIスレッドで行う必要がある
            # .after(ms, callback) を使う
            command_text = data.get('command', 'Unknown')
            target_text = data.get('robot_color', 'All')
            status_msg = f"Sent {command_text} ({target_text})"
            if command_text == "place_ball":
                status_msg += f" to ({data.get('x')}, {data.get('y')})"

            self.master.after(0, self.update_status_label, status_msg, "green")
        except socket.error as e:
            print(f"Failed to send command: {e}")
            self.master.after(0, self.update_status_label,
                              f"Send failed: {e}", "red")
        except ValueError as e:  # JSON dumps error
            print(f"Error encoding data: {e}")
            self.master.after(0, self.update_status_label,
                              f"Encoding error: {e}", "red")
        except Exception as e:  # その他の予期せぬエラー
            print(f"An unexpected error occurred during send: {e}")
            self.master.after(0, self.update_status_label,
                              f"Unexpected error: {e}", "red")

    def update_status_label(self, text, color):
        """ステータスラベルを更新する (GUIスレッドから呼ばれる)"""
        self.status_label.config(text=text, foreground=color)

    def get_selected_robot_color(self):
        """選択されているロボットの色を取得する"""
        selected_color = self.selected_robot.get()
        if selected_color == "none" or (selected_color == "yellow" and not config.ENABLE_YELLOW_ROBOT) or (selected_color == "blue" and not config.ENABLE_BLUE_ROBOT):
            # print("Warning: No valid robot selected.") # ログが煩雑になるのでコメントアウト
            self.update_status_label(
                "Error: No valid robot selected.", "orange")
            return None  # 有効なロボットが選択されていない場合
        return selected_color

    def send_emergency_stop_command(self):
        """EMERGENCY STOP コマンドを送信 (全ロボット対象)"""
        # target_robot_color は含めない (main.py で全ロボットにbroadcastするため)
        command = {"type": "game_command", "command": "emergency_stop"}
        self.send_udp(command)
        # ステータス更新は send_udp の中のスレッドで行われる

    def send_start_game_command(self):
        """START GAME コマンドを送信 (全ロボット対象)"""
        # target_robot_color は含めない (main.py で全ロボットにbroadcastするため)
        command = {"type": "game_command", "command": "start_game"}
        self.send_udp(command)
        # ステータス更新は send_udp の中のスレッドで行われる

    def send_stop_game_command(self):
        """STOP GAME コマンドを送信 (全ロボット対象)"""
        # target_robot_color は含めない (main.py で全ロボットにbroadcastするため)
        command = {"type": "game_command", "command": "stop_game"}
        self.send_udp(command)
        # ステータス更新は send_udp の中のスレッドで行われる

    def send_place_ball_command_custom(self):
        """選択されているロボットに PLACE BALL コマンドを送信 (カスタム位置)"""
        robot_color = self.get_selected_robot_color()
        if not robot_color:
            # get_selected_robot_color 内でステータス表示される
            return

        try:
            # テキストボックスから数値を取得
            x_str = self.x_entry.get()
            y_str = self.y_entry.get()

            # 空文字列チェックを追加
            if not x_str or not y_str:
                self.update_status_label("X or Y input is empty.", "red")
                return

            x = float(x_str)
            y = float(y_str)

            command = {"type": "game_command", "command": "place_ball",
                       "x": x, "y": y,
                       "robot_color": robot_color}  # 選択されたロボット色を使用
            self.send_udp(command)
            # ステータス更新は send_udp の中のスレッドで行われる
        except ValueError:
            self.update_status_label(
                "Invalid X, Y input (not a number).", "red")
        except Exception as e:
            self.update_status_label(
                f"An error occurred processing placement: {e}", "red")


def main():
    root = tk.Tk()
    gui = GameControllerGUI(root)
    root.mainloop()
    # root.mainloop() が終了したらここまで来る
    print("Game Controller GUI finished.")


if __name__ == "__main__":
    main()
