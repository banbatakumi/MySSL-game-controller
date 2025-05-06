import threading  # GUIをフリーズさせないためにUDP送信を別スレッドで行う場合に使用
import config
import json
import socket
from tkinter import ttk  # ttk を使用してボタンなどの見栄えを良くすることも可能
import tkinter as tk


class GameControllerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Robot Game Controller")
        master.geometry("600x400")  # ウィンドウの初期サイズを調整

        # レイアウト設定 (グリッド)
        # ウィンドウサイズ変更時にグリッドの伸縮を設定
        self.master.columnconfigure(0, weight=1)  # 0列目を伸縮可能にする
        self.master.columnconfigure(1, weight=1)  # 1列目も伸縮可能にする
        # 行方向の伸縮も必要に応じて設定
        self.master.rowconfigure(1, weight=1)  # ゲームコントロールフレーム
        self.master.rowconfigure(2, weight=1)  # ボール配置フレーム
        self.master.rowconfigure(3, weight=0)  # ステータスラベル (伸縮不要)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target_ip = config.GAME_COMMAND_TARGET_IP
        self.target_port = config.GAME_COMMAND_LISTEN_PORT

        # UI要素の配置 (Gridを使用)
        current_row = 0

        # ターゲット情報ラベル
        tk.Label(master, text=f"Sending commands to: {self.target_ip}:{self.target_port}").grid(
            row=current_row, column=0, columnspan=2, pady=5)
        current_row += 1

        # ロボット選択機能は削除

        # ゲームコントロールボタンフレーム (全体コマンド)
        game_control_frame = tk.LabelFrame(
            master, text="Game Control (All Robots)")
        game_control_frame.grid(
            row=current_row, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")  # nsewで上下左右に伸縮
        game_control_frame.columnconfigure(0, weight=1)
        game_control_frame.columnconfigure(1, weight=1)
        game_control_frame.columnconfigure(2, weight=1)
        current_row += 1

        # 各ボタンがフレーム内で伸縮するように rowconfigure を設定
        game_control_frame.rowconfigure(0, weight=1)

        self.start_button = tk.Button(
            # width, height は sticky="nsew" に任せる
            game_control_frame, text="GAME START", command=self.send_start_command)
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.stop_button = tk.Button(
            # width, height は sticky="nsew" に任せる
            game_control_frame, text="STOP GAME", command=self.send_stop_command)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.emergency_stop_button = tk.Button(game_control_frame, text="EMERGENCY STOP",
                                               # width, height は sticky="nsew" に任せる
                                               command=self.send_emergency_stop_command, bg="red", fg="white")
        self.emergency_stop_button.grid(
            row=0, column=2, padx=5, pady=5, sticky="nsew")

        # ボール配置フレーム (全体コマンドまたはシステムコマンドとして扱う)
        place_ball_frame = tk.LabelFrame(
            master, text="Ball Placement")  # "Selected Robot" を削除
        place_ball_frame.grid(row=current_row, column=0, columnspan=2,
                              padx=10, pady=5, sticky="nsew")  # nsewで上下左右に伸縮
        place_ball_frame.columnconfigure(0, weight=0)  # Labelは伸縮させない
        place_ball_frame.columnconfigure(1, weight=1)  # Entryを伸縮可能に
        place_ball_frame.columnconfigure(2, weight=1)  # Entryを伸縮可能に
        place_ball_frame.columnconfigure(3, weight=1)  # Buttonを伸縮可能に

        # 各要素がフレーム内で伸縮するように rowconfigure を設定
        place_ball_frame.rowconfigure(0, weight=1)
        place_ball_frame.rowconfigure(1, weight=1)

        tk.Label(place_ball_frame, text=f"Default: ({config.BALL_PLACEMENT_TARGET_X},{config.BALL_PLACEMENT_TARGET_Y})").grid(
            row=0, column=0, columnspan=2, padx=5, pady=2, sticky="w")  # 左寄せ
        self.place_ball_button = tk.Button(
            # width は sticky="ew" に任せる
            place_ball_frame, text="PLACE (Default)", command=self.send_place_ball_command_default)
        self.place_ball_button.grid(
            row=0, column=2, columnspan=2, padx=5, pady=2, sticky="ew")

        tk.Label(place_ball_frame, text="Custom (X, Y):").grid(
            row=1, column=0, padx=5, pady=2, sticky="w")  # 左寄せ
        self.x_entry = tk.Entry(place_ball_frame)  # width は sticky="ew" に任せる
        self.x_entry.insert(0, "0")  # デフォルト値
        self.x_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.y_entry = tk.Entry(place_ball_frame)  # width は sticky="ew" に任せる
        self.y_entry.insert(0, "0")  # デフォルト値
        self.y_entry.grid(row=1, column=2, padx=5, pady=2, sticky="ew")
        self.place_ball_custom_button = tk.Button(
            # width は sticky="ew" に任せる
            place_ball_frame, text="PLACE (Custom)", command=self.send_place_ball_command_custom)
        self.place_ball_custom_button.grid(
            row=1, column=3, padx=5, pady=2, sticky="ew")
        current_row += 1

        # モード切り替えボタンフレームは削除

        # ステータスラベル
        self.status_label = tk.Label(
            master, text="", anchor="w")  # anchor="w" で左寄せ
        self.status_label.grid(row=current_row, column=0, columnspan=2,
                               padx=10, pady=5, sticky="ew")  # ewで左右に伸縮
        # ステータスラベルの行は伸縮させないため weight=0 のまま

    def send_udp(self, data):
        """UDP経由でJSONデータを送信する"""
        try:
            json_data = json.dumps(data)
            byte_data = json_data.encode('utf-8')
            # UDP送信はGUIスレッドをブロックしないため、直接呼び出しでOK。
            # 大量のデータを連続送信する場合はスレッド化を検討。
            self.sock.sendto(byte_data, (self.target_ip, self.target_port))
            print(f"Sent: {data}")
            # コマンドが辞書型で "command" キーを持つか確認
            command_type = data.get('type', 'unknown')
            command_name = data.get('command', 'unknown')
            status_text = f"Sent command: type='{command_type}', command='{command_name}'"

            # place_ball の場合は座標も表示
            if command_name == 'place_ball':
                x = data.get('x', '?')
                y = data.get('y', '?')
                status_text += f" (x={x}, y={y})"

            self.status_label.config(
                text=status_text, fg="green")
        except socket.error as e:
            print(f"Failed to send command: {e}")
            self.status_label.config(text=f"Send failed: {e}", fg="red")
        except TypeError as e:
            print(f"Error encoding data: {e}")
            self.status_label.config(text=f"Encoding error: {e}", fg="red")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.status_label.config(text=f"Error: {e}", fg="red")

    # ロボット選択関連メソッドは削除

    # --- 全体コマンド ---

    def send_start_command(self):
        """GAME START コマンドを送信 (全ロボット対象)"""
        # 全体コマンドなので robot_color は含めない
        command = {"type": "game_command", "command": "start"}
        self.send_udp(command)

    def send_stop_command(self):
        """STOP GAME コマンドを送信 (全ロボット対象)"""
        # 全体コマンドなので robot_color は含めない
        command = {"type": "game_command", "command": "stop"}
        self.send_udp(command)

    def send_emergency_stop_command(self):
        """EMERGENCY STOP コマンドを送信 (全ロボット対象)"""
        # 全体コマンドなので robot_color は含めない
        command = {"type": "game_command", "command": "emergency_stop"}
        self.send_udp(command)

    # --- ボール配置コマンド (全体またはシステム対象として扱う) ---

    def send_place_ball_command_default(self):
        """PLACE BALL コマンドを送信 (デフォルト位置)"""
        # ロボット指定は削除
        command = {"type": "game_command", "command": "place_ball",
                   "x": config.BALL_PLACEMENT_TARGET_X,
                   "y": config.BALL_PLACEMENT_TARGET_Y}  # robot_color を削除
        self.send_udp(command)

    def send_place_ball_command_custom(self):
        """PLACE BALL コマンドを送信 (カスタム位置)"""
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            # ロボット指定は削除
            command = {"type": "game_command", "command": "place_ball",
                       "x": x, "y": y}  # robot_color を削除
            self.send_udp(command)
        except ValueError:
            self.status_label.config(
                text="Invalid X, Y input. Please enter numbers.", fg="red")
        except Exception as e:
            self.status_label.config(
                text=f"Error processing input: {e}", fg="red")

    # モード切り替えコマンド関連メソッドは削除


def main():
    root = tk.Tk()
    gui = GameControllerGUI(root)
    root.mainloop()
    print("Game Controller GUI closed.")
    # ソケットを閉じる
    if hasattr(gui, 'sock') and gui.sock:
        gui.sock.close()
        print("Socket closed.")


if __name__ == "__main__":
    main()
