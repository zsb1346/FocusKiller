import tkinter as tk
from tkinter import ttk, messagebox
import win32gui
import win32process
import psutil
import keyboard
import threading
import time

class FocusKiller:
    def __init__(self, root):
        self.root = root
        self.root.title("焦点窗口一键杀死工具")
        self.root.geometry("450x250")
        self.root.resizable(False, False)

        self.target_pid = None
        self.target_title = ""
        self.hotkey = ""

        tk.Label(root, text="设置一键杀死快捷键（如：F1、Q、X、0）", font=("微软雅黑", 10)).pack(pady=8)
        self.entry_hk = ttk.Entry(root, font=("微软雅黑", 12), width=10)
        self.entry_hk.pack(pady=2)

        ttk.Button(root, text="保存快捷键", command=self.save_hotkey).pack(pady=5)

        tk.Label(root, text="------------------------------------", fg="gray").pack()

        self.label_info = tk.Label(root, text="当前未选择窗口\n请点击任意窗口以捕获焦点", font=("微软雅黑", 10))
        self.label_info.pack(pady=12)

        threading.Thread(target=self.capture_foreground_window_loop, daemon=True).start()

    def save_hotkey(self):
        key = self.entry_hk.get().strip()
        if not key:
            messagebox.showwarning("提示", "请输入快捷键")
            return

        self.hotkey = key
        keyboard.unhook_all()
        keyboard.add_hotkey(self.hotkey, self.kill_target_process)
        messagebox.showinfo("成功", f"快捷键已设置为：【{key}】")

    def get_window_pid(self, hwnd):
        try:
            tid, pid = win32process.GetWindowThreadProcessId(hwnd)
            return pid
        except:
            return None

    def get_window_title(self, hwnd):
        try:
            return win32gui.GetWindowText(hwnd)
        except:
            return ""

    # 修复后的鼠标窗口捕获（无报错版）
    def capture_foreground_window_loop(self):
        last_hwnd = 0
        while True:
            time.sleep(0.2)
            hwnd = win32gui.GetForegroundWindow()
            if hwnd != last_hwnd:
                last_hwnd = hwnd
                pid = self.get_window_pid(hwnd)
                title = self.get_window_title(hwnd)
                if pid and title and title.strip() != self.root.title():
                    self.target_pid = pid
                    self.target_title = title
                    self.label_info.config(
                        text=f"✅ 已捕获窗口：\n标题：{title[:35]}\nPID：{pid}"
                    )

    def kill_target_process(self):
        if not self.target_pid:
            messagebox.showwarning("提示", "尚未捕获任何窗口")
            return

        try:
            p = psutil.Process(self.target_pid)
            p.kill()
            self.label_info.config(text=f"❌ 已杀死：{self.target_title[:20]}")
            self.target_pid = None
        except Exception as e:
            messagebox.showerror("错误", f"失败：{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FocusKiller(root)
    root.mainloop()
