# ゲームコントローラーからのコマンド受信ポート (新設)
GAME_COMMAND_LISTEN_PORT = 50011  # << 新しいポート >>


# ゲームコントローラーがコマンドを送信する相手 (main.py が動いているPCのIP)
# 通常は LISTEN_IP が "0.0.0.0" の場合、送信先は "127.0.0.1" (localhost) でOK
# main.py が別のPCで動く場合は、そのPCのIPアドレスを指定
GAME_COMMAND_TARGET_IP = "192.168.50.86"  # << main.py が動くPCのIPに変更が必要な場合あり >>


# ボール配置のデフォルト目標位置 (cm)
BALL_PLACEMENT_TARGET_X = 0
BALL_PLACEMENT_TARGET_Y = 0

ENABLE_YELLOW_ROBOT = True
ENABLE_BLUE_ROBOT = True
