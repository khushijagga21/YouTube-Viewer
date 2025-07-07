import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import time
import requests
import undetected_chromedriver as uc

# Check if a proxy works with YouTube
def is_proxy_working(proxy):
    try:
        response = requests.get("https://www.youtube.com", proxies={
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }, timeout=10)
        return response.status_code == 200
    except:
        return False

# Function to watch the video using a specific proxy
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
        time.sleep(45)  # Simulate watching the video
        driver.quit()
    except Exception as e:
        print(f"[X] Failed with proxy {proxy} — {e}")

# GUI Application class
class YouTubeViewBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Viewer Bot")
        self.root.geometry("600x420")
        self.root.configure(bg="#ffffff")

        self.url = tk.StringVar()
        self.proxy_file_path = ""
        self.loop_minutes = tk.StringVar(value="0")  # default to no loop

        # UI Elements
        tk.Label(root, text="🎥 Enter YouTube Video URL", bg="#ffffff", font=("Arial", 12)).pack(pady=(20, 5))
        tk.Entry(root, textvariable=self.url, width=65, font=("Arial", 11)).pack(pady=5)

        tk.Button(root, text="📂 Select Proxy File", command=self.select_proxy_file, width=20, bg="#e0e0e0").pack(pady=15)

        loop_frame = tk.Frame(root, bg="#ffffff")
        loop_frame.pack(pady=5)
        tk.Label(loop_frame, text="🔁 Loop every (minutes):", bg="#ffffff").pack(side=tk.LEFT, padx=5)
        tk.Entry(loop_frame, textvariable=self.loop_minutes, width=5).pack(side=tk.LEFT)

        tk.Button(root, text="🚀 Start Bot", command=self.start_bot_thread, width=20, bg="#4caf50", fg="white").pack(pady=10)

        self.status_label = tk.Label(root, text="", bg="#ffffff", font=("Arial", 10), fg="green")
        self.status_label.pack(pady=10)

    # Select proxy file from file dialog
    def select_proxy_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.proxy_file_path = file_path
            messagebox.showinfo("File Selected", f"Using proxies from:\n{file_path}")

    # Run bot in background thread
    def start_bot_thread(self):
        t = Thread(target=self.looping_bot)
        t.start()

    # Run one cycle of bot
    def start_bot(self):
        try:
            with open(self.proxy_file_path, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Error", f"Could not read proxies:\n{e}")
            return

        success, fail = 0, 0

        for proxy in proxies:
            if is_proxy_working(proxy):
                print(f"[✓] Proxy working: {proxy}")
                Thread(target=watch_video_with_proxy, args=(self.url.get().strip(), proxy)).start()
                success += 1
            else:
                print(f"[X] Skipping dead proxy: {proxy}")
                fail += 1

        self.root.after(0, lambda: self.status_label.config(
    text=f"✅ Started {success} views, ❌ Skipped {fail} dead proxies."
))


    # Loop bot with delay
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

# Start GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeViewBotUI(root)
    root.mainloop()
