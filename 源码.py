import os
import sys
import time
import configparser
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
import winreg
from datetime import datetime, timedelta

APP_NAME = "ShutdownAssistant"
CONFIG_FILE = os.path.join(os.getenv('APPDATA'), APP_NAME, 'config.ini')

def is_admin():
    """检查管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin():
    """请求管理员权限"""
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

class ShutdownAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("下班助手 V2.0")
        self.config = configparser.ConfigParser()
        self.load_config()

        self.create_ui()
        self.check_auto_start()
        self.schedule_next_shutdown()

    def create_ui(self):
        """创建界面"""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 时间输入
        ttk.Label(main_frame, text="关机时间 (HH:MM)").grid(row=0, column=0)
        self.time_entry = ttk.Entry(main_frame)
        self.time_entry.grid(row=0, column=1)
        self.time_entry.insert(0, self.config.get('DEFAULT', 'scheduled_time', fallback='18:00'))

        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="立即关机", command=self.shutdown_now).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="定时关机", command=self.schedule_shutdown).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="取消关机", command=self.cancel_shutdown).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="安全蓝屏", command=self.bsod).grid(row=0, column=3, padx=5)

        # 设置区域
        self.auto_start_var = tk.BooleanVar(value=self.config.getboolean('DEFAULT', 'auto_start', fallback=False))
        ttk.Checkbutton(main_frame, text="开机启动", variable=self.auto_start_var,
                       command=self.toggle_auto_start).grid(row=2, column=0, pady=5)

        self.repeat_var = tk.BooleanVar(value=self.config.getboolean('DEFAULT', 'repeat', fallback=True))
        ttk.Checkbutton(main_frame, text="每日重复", variable=self.repeat_var).grid(row=2, column=1, pady=5)

    def schedule_shutdown(self):
        """设置定时关机"""
        shutdown_time = self.time_entry.get()
        try:
            datetime.strptime(shutdown_time, "%H:%M")
        except ValueError:
            messagebox.showerror("错误", "时间格式错误，请使用HH:MM格式")
            return

        now = datetime.now()
        target = datetime.strptime(shutdown_time, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day)
        
        if target < now:
            target += timedelta(days=1)

        delta = (target - now).total_seconds()
        os.system(f'shutdown -s -t {int(delta)}')
        self.save_config()
        messagebox.showinfo("成功", f"已设置{shutdown_time}关机")

    def cancel_shutdown(self):
        """取消关机计划"""
        os.system('shutdown -a')
        messagebox.showinfo("成功", "已取消关机计划")

    def shutdown_now(self):
        """立即关机"""
        if messagebox.askyesno("确认", "确定要立即关机吗？"):
            os.system('shutdown -s -t 0')

    def bsod(self):
        """安全蓝屏功能"""
        if messagebox.askyesno("警告", "这将导致系统蓝屏，确定继续吗？"):
            try:
                # 安全触发蓝屏的方法
                ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
                ctypes.windll.ntdll.NtRaiseHardError(0xDEADDEAD, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
            except Exception as e:
                messagebox.showerror("错误", f"蓝屏失败: {str(e)}")

    def toggle_auto_start(self):
        """切换开机启动"""
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
            if self.auto_start_var.get():
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, sys.executable)
            else:
                winreg.DeleteValue(key, APP_NAME)
            winreg.CloseKey(key)
        except WindowsError:
            messagebox.showerror("错误", "需要管理员权限修改启动项")

    def check_auto_start(self):
        """检查开机启动状态"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Run")
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            self.auto_start_var.set(True)
            winreg.CloseKey(key)
        except FileNotFoundError:
            self.auto_start_var.set(False)

    def save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        self.config['DEFAULT'] = {
            'scheduled_time': self.time_entry.get(),
            'auto_start': str(self.auto_start_var.get()),
            'repeat': str(self.repeat_var.get())
        }
        with open(CONFIG_FILE, 'w') as f:
            self.config.write(f)

    def load_config(self):
        """加载配置"""
        self.config.read(CONFIG_FILE)

    def schedule_next_shutdown(self):
        """自动设置下一次关机"""
        if self.config.getboolean('DEFAULT', 'repeat', fallback=False):
            shutdown_time = self.config.get('DEFAULT', 'scheduled_time', fallback='18:00')
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, shutdown_time)
            self.schedule_shutdown()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    if not is_admin():
        request_admin()
    app = ShutdownAssistant()
    app.run()