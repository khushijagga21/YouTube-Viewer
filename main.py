import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

PASSWORD = "123"
successful_views = 0

# Password UI
def show_password_prompt():
    pw_root = tk.Tk()
    pw_root.title("🔐 Enter Password")
    pw_root.geometry("300x150")
    pw_root.configure(bg="#1e1e2f")

    tk.Label(pw_root, text="🔒 Access Restricted", font=("Segoe UI", 13, "bold"), bg="#1e1e2f", fg="#00ffcc").pack(pady=10)
    tk.Label(pw_root, text="Enter Password:", bg="#1e1e2f", fg="white").pack()

    password_var = tk.StringVar()
    entry = tk.Entry(pw_root, textvariable=password_var, show="*", width=25, bg="#2c2c3c", fg="white")
    entry.pack(pady=5)
    entry.focus()

    def check_password():
        if password_var.get() == PASSWORD:
            pw_root.destroy()
            launch_app()
        else:
            messagebox.showerror("Access Denied", "Incorrect password!")

    tk.Button(pw_root, text="Submit", command=check_password, bg="#6c5ce7", fg="white").pack(pady=10)
    pw_root.mainloop()

def launch_app():
    root = tk.Tk()
    app = YouTubeViewBotUI(root)
    root.mainloop()

class YouTubeViewBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 Auto feed x")
        self.root.geometry("600x560")
        self.root.configure(bg="#1e1e2f")

        self.url = tk.StringVar()
        self.proxy_file_path = ""
        self.loop_minutes = tk.StringVar(value="0")
        self.min_watch = tk.StringVar(value="35")
        self.max_watch = tk.StringVar(value="60")

        tk.Label(root, text="🎥 Auto feed x", font=("Segoe UI", 16, "bold"), bg="#1e1e2f", fg="#00ffcc").pack(pady=15)
        tk.Label(root, text="Enter YouTube URL:", font=("Segoe UI", 11), bg="#1e1e2f", fg="white").pack()
        tk.Entry(root, textvariable=self.url, font=("Segoe UI", 10), width=50, bg="#2c2c3c", fg="white").pack(pady=5)

        tk.Button(root, text="📂 Choose Proxy File", command=self.select_proxy_file, font=("Segoe UI", 11), bg="#00b894", fg="white").pack(pady=10)

        frame = tk.Frame(root, bg="#1e1e2f")
        frame.pack()
        tk.Label(frame, text="Repeat every (min):", font=("Segoe UI", 11), bg="#1e1e2f", fg="white").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=self.loop_minutes, font=("Segoe UI", 10), width=5, bg="#2c2c3c", fg="white").pack(side=tk.LEFT, padx=5)

        tk.Label(root, text="Watch time range (sec):", font=("Segoe UI", 11), bg="#1e1e2f", fg="white").pack(pady=(10, 0))
        watch_frame = tk.Frame(root, bg="#1e1e2f")
        watch_frame.pack()
        tk.Entry(watch_frame, textvariable=self.min_watch, width=5).pack(side=tk.LEFT)
        tk.Label(watch_frame, text="to", bg="#1e1e2f", fg="white").pack(side=tk.LEFT)
        tk.Entry(watch_frame, textvariable=self.max_watch, width=5).pack(side=tk.LEFT)

        tk.Button(root, text="🚀 Start Bot", command=self.start_bot_thread, font=("Segoe UI", 11), bg="#6c5ce7", fg="white").pack(pady=15)

        self.status_label = tk.Label(root, text="", font=("Segoe UI", 10), bg="#1e1e2f", fg="#00ffcc")
        self.status_label.pack()

        self.views_label = tk.Label(root, text="👁️ Views Simulated: 0", font=("Segoe UI", 10, "bold"), bg="#1e1e2f", fg="#fd79a8")
        self.views_label.pack(pady=5)

        self.proxy_result_label = tk.Label(root, text="", font=("Segoe UI", 9), bg="#1e1e2f", fg="#ffeaa7")
        self.proxy_result_label.pack(pady=5)

    def select_proxy_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.proxy_file_path = file_path
            messagebox.showinfo("File Selected", f"Using proxies from:\n{file_path}")

    def start_bot_thread(self):
        url = self.url.get().strip()
        proxy_file = self.proxy_file_path
        try:
            loop_delay = int(self.loop_minutes.get())
        except:
            messagebox.showerror("Error", "Loop interval must be a number.")
            return

        if not url or not proxy_file:
            messagebox.showerror("Error", "Enter URL and select proxy file.")
            return

        t = Thread(target=self.looping_bot, args=(url, proxy_file, loop_delay))
        t.start()

    def looping_bot(self, url, proxy_file, loop_delay):
        while True:
            self.start_bot(url, proxy_file)
            if loop_delay <= 0:
                break
            time.sleep(loop_delay * 60)

    def start_bot(self, url, proxy_file_path):
        global successful_views
        try:
            with open(proxy_file_path, 'r') as f:
                proxies = [line.strip() for line in f if line.strip() and not line.lower().startswith("ip")]
        except Exception as e:
            messagebox.showerror("Error", f"Could not read proxies:\n{e}")
            return

        min_watch = int(self.min_watch.get())
        max_watch = int(self.max_watch.get())

        working_proxies = []
        failed_proxies = []
        self.status_label.config(text="⏳ Checking proxies...")

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_proxy = {executor.submit(is_proxy_working, proxy): proxy for proxy in proxies}
            for future in future_to_proxy:
                proxy = future_to_proxy[future]
                try:
                    if future.result():
                        working_proxies.append(proxy)
                    else:
                        failed_proxies.append(proxy)
                except:
                    failed_proxies.append(proxy)

        self.status_label.config(text=f"✅ {len(working_proxies)} proxies working.")
        self.proxy_result_label.config(text=f"🟢 {len(working_proxies)} OK | 🔴 {len(failed_proxies)} Dead")

        for proxy in working_proxies:
            Thread(target=self.watch_and_count, args=(url, proxy, min_watch, max_watch)).start()

    def watch_and_count(self, url, proxy, min_watch, max_watch):
        global successful_views
        if watch_video_with_proxy(url, proxy, min_watch, max_watch):
            successful_views += 1
            self.views_label.config(text=f"👁️ Views Simulated: {successful_views}")

def is_proxy_working(proxy):
    try:
        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        options.add_argument(f'--proxy-server=http://{proxy}')
        driver = uc.Chrome(options=options)
        driver.get("https://www.google.com")
        time.sleep(2)
        driver.quit()
        return True
    except:
        return False

def watch_video_with_proxy(url, proxy, min_watch, max_watch):
    try:
        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        options.add_argument(f'--proxy-server=http://{proxy}')
        driver = uc.Chrome(options=options)

        driver.get(url)
        time.sleep(2)

        # Handle cookie banner if exists
        try:
            consent_btn = driver.find_element(By.XPATH, '//button[contains(text(),"I agree") or contains(text(),"Accept all")]')
            consent_btn.click()
            time.sleep(1)
        except:
            pass

        driver.execute_script("""
            const video = document.querySelector('video');
            if (video) {
                video.muted = true;
                video.play();
            }
        """)

        driver.execute_script("window.scrollBy(0, 500);")
        actions = ActionChains(driver)
        actions.move_by_offset(random.randint(50, 300), random.randint(50, 300)).perform()

        time.sleep(random.randint(min_watch, max_watch))
        driver.quit()
        return True
    except Exception as e:
        print(f"[!] Failed with {proxy}: {e}")
        return False

if __name__ == "__main__":
    show_password_prompt()
