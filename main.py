import tkinter as tk
from tkinter import messagebox
from threading import Thread

import os
import pickle
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

COOKIE_FILE = 'instagram_cookies.pkl'

# ------------------ Your Main Application UI ------------------

class YouTubeViewBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 Auto feed x")
        self.root.geometry("600x650")
        self.root.configure(bg="#1e1e2f")

        self.url = tk.StringVar()
        self.keywords = tk.StringVar()
        self.proxy_file_path = ""
        self.loop_minutes = tk.StringVar(value="0")
        self.min_watch = tk.StringVar(value="30")
        self.max_watch = tk.StringVar(value="60")

        
        
        tk.Label(root, text="🎥 Auto feed x", font=("Segoe UI", 16, "bold"), bg="#1e1e2f", fg="#00ffcc").pack(pady=15)
        tk.Label(root, text="Enter URL:", font=("Segoe UI", 11), bg="#1e1e2f", fg="white").pack()
        tk.Entry(root, textvariable=self.url, font=("Segoe UI", 10), width=50, bg="#2c2c3c", fg="white", bd=1, insertbackground='white').pack(pady=5)

        tk.Label(root, text="Enter Keywords (optional):", font=("Segoe UI", 11), bg="#1e1e2f", fg="white").pack()
        tk.Entry(root, textvariable=self.keywords, font=("Segoe UI", 10), width=50, bg="#2c2c3c", fg="white", bd=1, insertbackground='white').pack(pady=5)

        self.display_keywords = tk.Label(root, text="", font=("Segoe UI", 10), bg="#1e1e2f", fg="#00ffcc")
        self.display_keywords.pack(pady=(0, 10))

        def update_keyword_label(*args):
            val = self.keywords.get()
            self.display_keywords.config(text=f"📌 Keywords: {val}" if val else "")

        self.keywords.trace_add("write", update_keyword_label)

        tk.Button(root, text="📂 Choose Proxy File", command=self.select_proxy_file, font=("Segoe UI", 11), bg="#00b894", fg="white", width=20).pack(pady=10)

        loop_frame = tk.Frame(root, bg="#1e1e2f")
        loop_frame.pack(pady=5)
        tk.Label(loop_frame, text="Repeat every (min):", font=("Segoe UI", 11), bg="#1e1e2f", fg="#ffffff").pack(side=tk.LEFT)
        tk.Entry(loop_frame, textvariable=self.loop_minutes, font=("Segoe UI", 10), width=5, bg="#2c2c3c", fg="white", bd=1, insertbackground='white').pack(side=tk.LEFT, padx=5)

        watch_frame = tk.Frame(root, bg="#1e1e2f")
        watch_frame.pack(pady=5)
        tk.Label(watch_frame, text="Watch time range (sec):", font=("Segoe UI", 11), bg="#1e1e2f", fg="#ffffff").pack(side=tk.LEFT)
        tk.Entry(watch_frame, textvariable=self.min_watch, font=("Segoe UI", 10), width=5, bg="#2c2c3c", fg="white", bd=1, insertbackground='white').pack(side=tk.LEFT, padx=3)
        tk.Label(watch_frame, text="to", font=("Segoe UI", 11), bg="#1e1e2f", fg="white").pack(side=tk.LEFT)
        tk.Entry(watch_frame, textvariable=self.max_watch, font=("Segoe UI", 10), width=5, bg="#2c2c3c", fg="white", bd=1, insertbackground='white').pack(side=tk.LEFT, padx=3)

        tk.Button(root, text="🚀 Start Bot", command=self.start_bot_thread, font=("Segoe UI", 11), bg="#6c5ce7", fg="white", width=20).pack(pady=10)
        tk.Button(root, text="📸 Instagram Viewer", command=self.open_instagram_viewer, font=("Segoe UI", 10), bg="#d63031", fg="white", width=25).pack(pady=5)

        self.status_label = tk.Label(root, text="", font=("Segoe UI", 10), bg="#1e1e2f", fg="#00ffcc")
        self.status_label.pack(pady=10)

        tk.Label(root, text="Developed for demo/testing purposes only.", font=("Segoe UI", 8), bg="#1e1e2f", fg="#888").pack(side=tk.BOTTOM, pady=10)

    def select_proxy_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.proxy_file_path = file_path
            messagebox.showinfo("File Selected", f"Using proxies from:\n{file_path}")

    def start_bot_thread(self):
        t = Thread(target=self.looping_bot)
        t.start()

    def start_bot(self):
        try:
            with open(self.proxy_file_path, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Error", f"Could not read proxies:\n{e}")
            return

        try:
            min_watch = int(self.min_watch.get())
            max_watch = int(self.max_watch.get())
        except:
            messagebox.showerror("Error", "Invalid watch time range.")
            return

        success, fail = 0, 0
        working_proxies = []
        self.status_label.config(text="⏳ Checking proxies...")

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_proxy = {executor.submit(is_proxy_working, proxy): proxy for proxy in proxies}
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    if future.result():
                        working_proxies.append(proxy)
                        print(f"[✓] Proxy working: {proxy}")
                        success += 1
                    else:
                        print(f"[X] Dead proxy: {proxy}")
                        fail += 1
                except Exception as e:
                    print(f"[!] Error checking proxy {proxy}: {e}")
                    fail += 1

        self.status_label.config(text=f"✅ {success} working | ❌ {fail} dead proxies.")
        for proxy in working_proxies:
            Thread(target=watch_video_with_proxy, args=(self.url.get().strip(), proxy, min_watch, max_watch)).start()

    def looping_bot(self):
        if not self.url.get().strip():
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        if not self.proxy_file_path:
            messagebox.showerror("Error", "Please select a proxy file.")
            return

        try:
            loop_delay = int(self.loop_minutes.get())
        except:
            messagebox.showerror("Error", "Loop interval must be a number.")
            return

        while True:
            self.start_bot()
            if loop_delay <= 0:
                break
            time.sleep(loop_delay * 60)

    def open_instagram_viewer(self):
        def login_once():
            Thread(target=save_instagram_cookies).start()

        def play_reel():
            url = url_var.get().strip()
            if not url.startswith("https://www.instagram.com/reel/"):
                messagebox.showerror("Invalid URL", "Please enter a valid Instagram Reel URL.")
                return
            play_instagram_reel(url)

        ig_window = tk.Toplevel()
        ig_window.title("Instagram Viewer")
        ig_window.geometry("500x300")
        ig_window.configure(bg="#121212")

        url_var = tk.StringVar()
        tk.Label(ig_window, text="Enter Instagram Reel URL:", font=("Segoe UI", 12), bg="#121212", fg="#00ffff").pack(pady=10)
        tk.Entry(ig_window, textvariable=url_var, font=("Segoe UI", 10), width=50, bg="#1e1e1e", fg="white", insertbackground='white').pack(pady=5)

        tk.Button(ig_window, text="▶ Play Reel", command=play_reel, font=("Segoe UI", 10), bg="#00cec9", fg="white", width=20).pack(pady=10)
        tk.Button(ig_window, text="🔐 Login (once)", command=login_once, font=("Segoe UI", 10), bg="#0984e3", fg="white", width=20).pack(pady=5)
        tk.Button(ig_window, text="Close", command=ig_window.destroy, font=("Segoe UI", 10)).pack(pady=5)

# ------------------ Password Login Window ------------------

def show_login_window():
    login_win = tk.Tk()
    login_win.title("🔒 Secure Login")
    login_win.geometry("400x220")
    login_win.configure(bg="black")

    tk.Label(login_win, text="🔐 Secure Login", font=("Segoe UI", 16, "bold"), fg="white", bg="black").pack(pady=10)

    tk.Label(login_win, text="Enter Password:", font=("Segoe UI", 12), fg="white", bg="black").pack()
    password_var = tk.StringVar()
    tk.Entry(login_win, textvariable=password_var, show="*", width=30).pack(pady=10)

    def verify_password():
        if password_var.get() == "123":  # fixed password
            login_win.destroy()
            open_main_app()
        else:
            messagebox.showerror("Access Denied", "Incorrect Password!")

    tk.Button(login_win, text="Login", command=verify_password, width=20).pack(pady=5)

    login_win.mainloop()

# ------------------ Run App After Login ------------------

def open_main_app():
    root = tk.Tk()
    app = YouTubeViewBotUI(root)
    root.mainloop()

# ------------------ Start ------------------

if __name__ == "__main__":
    show_login_window()
