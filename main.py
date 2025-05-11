import tkinter as tk
from gui import GameControllerGUI  # gui.py から GameControllerGUI クラスをインポート


def main():
    root = tk.Tk()
    gui = GameControllerGUI(root)
    root.mainloop()
    # mainloopが終了した後に実行されるが、通常はgui.on_closingでsys.exit()が呼ばれるため
    # ここに到達することは稀（ウィンドウが正常に閉じられた場合）。
    print("Game Controller GUI finished.")


if __name__ == "__main__":
    main()
