import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import requests
import undetected_chromedriver as uc

# Check proxy validity (retry once)
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

# Watch YouTube video using a working proxy
def watch_video_with_proxy(video_url, proxy):
    options = uc.ChromeOptions()
    options.add_argument(f'--proxy-server=http://{proxy}')
    options.add_argument("--mute-audio")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = uc.Chrome(options=options)
        driver.get(video_url)
        print(f"[✓] Watching with proxy {proxy}")
        time.sleep(45)
        driver.quit()
    except Exception as e:
        print(f"[X] Failed to load video with proxy {proxy} — {e}")

# Main Application UI
class YouTubeViewBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔁 YouTube Viewer Bot")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e2f")

        self.url = tk.StringVar()
        self.proxy_file_path = ""
        self.loop_minutes = tk.StringVar(value="0")

        # Fonts
        heading_font = ("Segoe UI", 16, "bold")
        label_font = ("Segoe UI", 11)
        entry_font = ("Segoe UI", 10)

        # Header
        tk.Label(root, text="🎬 YouTube Viewer Bot", font=heading_font, bg="#1e1e2f", fg="#00ffcc").pack(pady=15)

        # YouTube URL Input
        tk.Label(root, text="Video URL:", font=label_font, bg="#1e1e2f", fg="#ffffff").pack()
        tk.Entry(root, textvariable=self.url, font=entry_font, width=50, bg="#2c2c3c", fg="white", bd=1,
                 insertbackground='white').pack(pady=5)

        # Proxy File Selection
        tk.Button(root, text="📂 Choose Proxy File", command=self.select_proxy_file,
                  font=label_font, bg="#00b894", fg="white", activebackground="#019875",
                  cursor="hand2", width=20).pack(pady=15)

        # Loop Timer
        loop_frame = tk.Frame(root, bg="#1e1e2f")
        loop_frame.pack(pady=5)
        tk.Label(loop_frame, text="Repeat every (minutes):", font=label_font,
                 bg="#1e1e2f", fg="#ffffff").pack(side=tk.LEFT)
        tk.Entry(loop_frame, textvariable=self.loop_minutes, font=entry_font, width=5,
                 bg="#2c2c3c", fg="white", bd=1, insertbackground='white').pack(side=tk.LEFT, padx=5)

        # Start Bot Button
        tk.Button(root, text="🚀 Start Bot", command=self.start_bot_thread,
                  font=label_font, bg="#6c5ce7", fg="white", activebackground="#4834d4",
                  cursor="hand2", width=20).pack(pady=20)

        # Status Label
        self.status_label = tk.Label(root, text="", font=("Segoe UI", 10), bg="#1e1e2f", fg="#00ffcc")
        self.status_label.pack(pady=10)

        # Footer
        tk.Label(root, text="Developed for demo/testing purposes only.", font=("Segoe UI", 8),
                 bg="#1e1e2f", fg="#888").pack(side=tk.BOTTOM, pady=10)

    # Select proxy file
    def select_proxy_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.proxy_file_path = file_path
            messagebox.showinfo("File Selected", f"Using proxies from:\n{file_path}")

    # Start in background thread
    def start_bot_thread(self):
        t = Thread(target=self.looping_bot)
        t.start()

    # Start bot logic with parallel proxy check
    def start_bot(self):
        try:
            with open(self.proxy_file_path, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Error", f"Could not read proxies:\n{e}")
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
            Thread(target=watch_video_with_proxy, args=(self.url.get().strip(), proxy)).start()

    # Loop bot logic
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

# Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeViewBotUI(root)
    root.mainloop()
