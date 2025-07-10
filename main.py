import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import pickle
import os
import webview
import requests
import random
import undetected_chromedriver as uc

COOKIE_FILE = 'instagram_cookies.pkl'
MASTER_PASSWORD = "letmein123"  # Fixed login password


def is_proxy_working(proxy):
    def test(url):
        try:
            response = requests.get(url, proxies={
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }, timeout=10)
            return response.status_code == 200
        except:
            return False
    return test("https://www.youtube.com") or test("https://api.ipify.org")


def watch_video_with_proxy(video_url, proxy, min_watch=30, max_watch=60):
    options = uc.ChromeOptions()
    options.add_argument(f'--proxy-server=http://{proxy}')
    options.add_argument("--mute-audio")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    try:
        driver = uc.Chrome(options=options)
        driver.get(video_url)
        duration = random.randint(min_watch, max_watch)
        print(f"⏱️ Watching video for {duration} seconds using proxy {proxy}")
        time.sleep(duration)
        driver.quit()
    except Exception as e:
        print(f"[X] Failed to load video with proxy {proxy} — {e}")


def save_instagram_cookies():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    driver.get("https://www.instagram.com/accounts/login/")
    messagebox.showinfo("Login Required", "Please log in to Instagram manually and then close the browser tab.")
    while True:
        time.sleep(2)
        if "instagram.com" in driver.current_url and not driver.current_url.startswith("https://www.instagram.com/accounts/login"):
            break
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, 'wb') as f:
        pickle.dump(cookies, f)
    driver.quit()
    messagebox.showinfo("Success", "Instagram login session saved.")


def play_instagram_reel(reel_url):
    if not os.path.exists(COOKIE_FILE):
        messagebox.showerror("Login Required", "Please login to Instagram first.")
        return

    def load_with_cookies(window):
        window.load_url(reel_url)

    webview.create_window("Instagram Reel", url="about:blank", width=800, height=600, on_top=True)
    window = webview.windows[0]
    webview.start(load_with_cookies, window)


def open_instagram_viewer():
    ig_window = tk.Toplevel()
    ig_window.title("Instagram Viewer")
    ig_window.geometry("500x300")
    ig_window.configure(bg="#121212")

    url_var = tk.StringVar()
    tk.Label(ig_window, text="Enter Instagram Reel URL:", font=("Segoe UI", 12), bg="#121212", fg="#00ffff").pack(pady=10)
    tk.Entry(ig_window, textvariable=url_var, font=("Segoe UI", 10), width=50, bg="#1e1e1e", fg="white", insertbackground='white').pack(pady=5)

    def login_once():
        Thread(target=save_instagram_cookies).start()

    def play_reel():
        url = url_var.get().strip()
        if not url.startswith("https://www.instagram.com/reel/"):
            messagebox.showerror("Invalid URL", "Please enter a valid Instagram Reel URL.")
            return
        play_instagram_reel(url)

    tk.Button(ig_window, text="▶ Play Reel", command=play_reel, font=("Segoe UI", 10), bg="#00cec9", fg="white", width=20).pack(pady=10)
    tk.Button(ig_window, text="🔐 Login (once)", command=login_once, font=("Segoe UI", 10), bg="#0984e3", fg="white", width=20).pack(pady=5)
    tk.Button(ig_window, text="Close", command=ig_window.destroy, font=("Segoe UI", 10)).pack(pady=5)


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

        heading_font = ("Segoe UI", 16, "bold")
        label_font = ("Segoe UI", 11)
        entry_font = ("Segoe UI", 10)

        tk.Label(root, text="🎥 Auto feed x", font=heading_font, bg="#1e1e2f", fg="#00ffcc").pack(pady=15)
        tk.Label(root, text="Video URL:", font=label_font, bg="#1e1e2f", fg="#ffffff").pack()
        tk.Entry(root, textvariable=self.url, font=entry_font, width=50, bg="#2c2c3c", fg="white", bd=1, insertbackground='white').pack(pady=5)

        tk.Label(root, text="Enter Keywords (optional):", font=label_font, bg="#1e1e2f", fg="white").pack()
        tk.Entry(root, textvariable=self.keywords, font=entry_font, width=50, bg="#2c2c3c", fg="white", bd=1, insertbackground='white').pack(pady=5)
        self.display_keywords = tk.Label(root, text="", font=("Segoe UI", 10), bg="#1e1e2f", fg="#00ffcc")
        self.display_keywords.pack(pady=(0, 10))

        def update_keyword_label(*args):
            val = self.keywords.get()
            self.display_keywords.config(text=f"📌 Keywords: {val}" if val else "")

        self.keywords.trace_add("write", update_keyword_label)

        tk.Button(root, text="📂 Choose Proxy File", command=self.select_proxy_file, font=label_font, bg="#00b894", fg="white", width=20).pack(pady=10)

        loop_frame = tk.Frame(root, bg="#1e1e2f")
        loop_frame.pack(pady=5)
        tk.Label(loop_frame, text="Repeat every (min):", font=label_font, bg="#1e1e2f", fg="#ffffff").pack(side=tk.LEFT)
        tk.Entry(loop_frame, textvariable=self.loop_minutes, font=entry_font, width=5, bg="#2c2c3c", fg="white", bd=1, insertbackground='white').pack(side=tk.LEFT, padx=5)

        watch_frame = tk.Frame(root, bg="#1e1e2f")
        watch_frame.pack(pady=5)
        tk.Label(watch_frame, text="Watch time range (sec):", font=label_font, bg="#1e1e2f", fg="#ffffff").pack(side=tk.LEFT)
        tk.Entry(watch_frame, textvariable=self.min_watch, font=entry_font, width=5, bg="#2c2c3c", fg="white", bd=1, insertbackground='white').pack(side=tk.LEFT, padx=3)
        tk.Label(watch_frame, text="to", font=label_font, bg="#1e1e2f", fg="white").pack(side=tk.LEFT)
        tk.Entry(watch_frame, textvariable=self.max_watch, font=entry_font, width=5, bg="#2c2c3c", fg="white", bd=1, insertbackground='white').pack(side=tk.LEFT, padx=3)

        tk.Button(root, text="🚀 Start Bot", command=self.start_bot_thread, font=label_font, bg="#6c5ce7", fg="white", width=20).pack(pady=10)
        tk.Button(root, text="📸 Instagram Viewer", command=open_instagram_viewer, font=("Segoe UI", 10), bg="#d63031", fg="white", width=25).pack(pady=5)
        tk.Button(root, text="📀 Save Keywords", command=self.save_keywords, font=label_font, bg="#e17055", fg="white", width=20).pack(pady=5)

        self.status_label = tk.Label(root, text="", font=("Segoe UI", 10), bg="#1e1e2f", fg="#00ffcc")
        self.status_label.pack(pady=10)
        tk.Label(root, text="Developed for demo/testing purposes only.", font=("Segoe UI", 8), bg="#1e1e2f", fg="#888").pack(side=tk.BOTTOM, pady=10)

    def select_proxy_file(self):
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
            print(f"[⏳] Waiting {loop_delay} minutes before next round...")
            time.sleep(loop_delay * 60)

    def save_keywords(self):
        keywords = self.keywords.get().strip()
        if not keywords:
            messagebox.showerror("Empty", "Please enter keywords first.")
            return
        try:
            with open("keywords_reels_bot.txt", "w") as f:
                f.write(keywords)
            messagebox.showinfo("Saved", "Keywords saved to keywords_reels_bot.txt")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save keywords: {e}")


def show_login_window():
    login = tk.Tk()
    login.title("Login Required")
    login.geometry("300x180")
    login.configure(bg="#1e1e2f")

    tk.Label(login, text="🔐 Enter Password:", bg="#1e1e2f", fg="white", font=("Segoe UI", 11)).pack(pady=20)
    password_var = tk.StringVar()
    tk.Entry(login, textvariable=password_var, show="*", width=25, font=("Segoe UI", 10), bg="#2c2c3c", fg="white", bd=1).pack()

    def check_password():
        if password_var.get() == MASTER_PASSWORD:
            login.destroy()
            root = tk.Tk()
            app = YouTubeViewBotUI(root)
            root.mainloop()
        else:
            messagebox.showerror("Access Denied", "Incorrect password!")

    tk.Button(login, text="Login", command=check_password, bg="#6c5ce7", fg="white", width=15).pack(pady=15)

    login.mainloop()


if __name__ == "__main__":
    show_login_window()
