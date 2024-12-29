import tkinter
import customtkinter
import yt_dlp
from tkinter import messagebox
import os

class YoutubeDownloader:
    def __init__(self):
        # System Settings
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        # Frame
        self.app = customtkinter.CTk()
        self.app.geometry("720x480")
        self.app.title("Youtube Downloader")

        # Adding UI elements
        self.title = customtkinter.CTkLabel(self.app, text="Insert a YouTube URL")
        self.title.pack(padx=10, pady=10)

        # Link input
        self.url_var = tkinter.StringVar()
        self.link = customtkinter.CTkEntry(self.app, width=350, height=40, textvariable=self.url_var)
        self.link.pack()

        # Progress label
        self.progress_label = customtkinter.CTkLabel(self.app, text="")
        self.progress_label.pack(padx=10, pady=10)

        # Download button
        self.download_button = customtkinter.CTkButton(self.app, text="Download", command=self.startDownload)
        self.download_button.pack(padx=10, pady=10)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Update progress label with download progress
            if 'downloaded_bytes' in d and 'total_bytes' in d:
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress_label.configure(text=f"Downloading: {progress:.1f}%")
            elif 'downloaded_bytes' in d and 'total_bytes_estimate' in d:
                progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                self.progress_label.configure(text=f"Downloading: {progress:.1f}%")
        elif d['status'] == 'finished':
            self.progress_label.configure(text="Download completed!")

    def startDownload(self):
        try:
            ytLink = self.url_var.get()
            if not ytLink:
                messagebox.showerror("Error", "Please enter a YouTube URL")
                return

            # Create downloads directory if it doesn't exist
            if not os.path.exists("downloads"):
                os.makedirs("downloads")

            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'progress_hooks': [self.progress_hook],
                'merge_output_format': 'mp4',
            }

            self.download_button.configure(state="disabled")
            self.progress_label.configure(text="Starting download...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([ytLink])

            messagebox.showinfo("Success", "Download completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.download_button.configure(state="normal")
            self.url_var.set("")  # Clear the input field

    def run(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = YoutubeDownloader()
    app.run()