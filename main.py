import os
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter
import yt_dlp
import threading
from functools import partial


class YoutubeDownloader:
    def __init__(self):
        # System Settings
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        # Frame
        self.app = customtkinter.CTk()
        self.app.geometry("720x480")
        self.app.title("YouTube Downloader")

        # Adding UI Elements
        self.title_label = customtkinter.CTkLabel(self.app, text="Insert a YouTube URL")
        self.title_label.pack(padx=10, pady=10)

        # Link Input
        self.url_var = tk.StringVar()
        self.link_entry = customtkinter.CTkEntry(
            self.app, width=350, height=40, textvariable=self.url_var
        )
        self.link_entry.pack(padx=10, pady=10)

        # Fix macOS keyboard shortcuts for the URL entry field
        # Cmd+A → select all text
        self.link_entry.bind("<Command-a>", self._select_all_entry)
        self.link_entry.bind("<Command-A>", self._select_all_entry)
        # Cmd+V → paste replacing any selected text
        self.link_entry.bind("<Command-v>", self._paste_replace_entry)
        self.link_entry.bind("<Command-V>", self._paste_replace_entry)

        # Download Folder Selection
        self.folder_frame = customtkinter.CTkFrame(self.app)
        self.folder_frame.pack(padx=10, pady=10, fill="x")
        
        self.folder_label = customtkinter.CTkLabel(self.folder_frame, text="Download Folder:")
        self.folder_label.pack(side="left", padx=10, pady=10)
        
        self.download_path = tk.StringVar(value=os.path.join(os.getcwd(), "downloads"))
        self.folder_path_label = customtkinter.CTkLabel(
            self.folder_frame, 
            text=self.download_path.get(),
            wraplength=300
        )
        self.folder_path_label.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        self.browse_button = customtkinter.CTkButton(
            self.folder_frame, 
            text="Browse", 
            command=self.browse_folder,
            width=80
        )
        self.browse_button.pack(side="right", padx=10, pady=10)

        # Cookie Source Selection
        self.cookie_frame = customtkinter.CTkFrame(self.app)
        self.cookie_frame.pack(padx=10, pady=(5, 0), fill="x")

        self.cookie_label = customtkinter.CTkLabel(self.cookie_frame, text="Cookies (for bot bypass):")
        self.cookie_label.pack(side="left", padx=10, pady=8)

        self.cookie_var = tk.StringVar(value="None")
        self.cookie_menu = customtkinter.CTkOptionMenu(
            self.cookie_frame,
            values=["None", "chrome", "firefox", "safari", "edge", "brave", "chromium", "opera"],
            variable=self.cookie_var,
            width=120
        )
        self.cookie_menu.pack(side="left", padx=5, pady=8)

        self.cookie_file_button = customtkinter.CTkButton(
            self.cookie_frame,
            text="Use cookies.txt",
            command=self.browse_cookie_file,
            width=120
        )
        self.cookie_file_button.pack(side="right", padx=10, pady=8)

        self.cookie_file_path = tk.StringVar(value="")

        # Auto-detect cookies file in project directory
        self._autodetect_cookie_file()

        # Quality Selection
        self.quality_label = customtkinter.CTkLabel(self.app, text="Select Quality:")
        self.quality_label.pack(padx=10, pady=(10, 5))
        
        self.quality_var = tk.StringVar(value="4K (2160p)")
        self.quality_menu = customtkinter.CTkOptionMenu(
            self.app, 
            values=["4K (2160p)", "1440p", "1080p", "720p", "480p", "360p", "best_available", "h264_best", "h264_1080p", "h264_720p", "audio_only"],
            variable=self.quality_var
        )
        self.quality_menu.pack(padx=10, pady=5)

        # Progress Label
        self.progress_label = customtkinter.CTkLabel(self.app, text="")
        self.progress_label.pack(padx=10, pady=10)

        # Progress Bar
        self.progress_bar = customtkinter.CTkProgressBar(self.app, width=300)
        self.progress_bar.pack(padx=10, pady=5)
        self.progress_bar.set(0)

        # Download Button
        self.download_button = customtkinter.CTkButton(
            self.app, text="Download", command=self.start_download_thread
        )
        self.download_button.pack(padx=10, pady=10)

        # Status Label
        self.status_label = customtkinter.CTkLabel(self.app, text="Ready to download")
        self.status_label.pack(padx=10, pady=5)

    def _select_all_entry(self, event=None):
        """Handle Cmd+A to select all text in the URL entry."""
        # Access the internal tkinter entry widget
        entry_widget = self.link_entry._entry if hasattr(self.link_entry, '_entry') else self.link_entry
        entry_widget.select_range(0, tk.END)
        entry_widget.icursor(tk.END)
        return "break"  # Prevent default handler

    def _paste_replace_entry(self, event=None):
        """Handle Cmd+V to paste, replacing any selected text."""
        entry_widget = self.link_entry._entry if hasattr(self.link_entry, '_entry') else self.link_entry
        try:
            clipboard_text = self.app.clipboard_get()
        except tk.TclError:
            return "break"  # Nothing on clipboard

        # Check if there's a selection
        try:
            sel_start = entry_widget.index(tk.SEL_FIRST)
            sel_end = entry_widget.index(tk.SEL_LAST)
            # Delete the selected text, then insert clipboard content
            entry_widget.delete(sel_start, sel_end)
            entry_widget.insert(sel_start, clipboard_text)
        except tk.TclError:
            # No selection — just insert at cursor position
            entry_widget.insert(tk.INSERT, clipboard_text)

        return "break"  # Prevent default handler (which would double-paste)

    def _autodetect_cookie_file(self):
        """Auto-detect a cookies.txt file in the project directory."""
        import glob
        script_dir = os.path.dirname(os.path.abspath(__file__))
        patterns = ["*cookies*.txt", "*cookie*.txt"]
        for pattern in patterns:
            matches = glob.glob(os.path.join(script_dir, pattern))
            if matches:
                cookie_file = matches[0]
                self.cookie_file_path.set(cookie_file)
                self.cookie_var.set("None")
                short = os.path.basename(cookie_file)
                display = f"...{short[-22:]}" if len(short) > 22 else short
                self.cookie_file_button.configure(text=display)
                break

    def browse_cookie_file(self):
        """Open file browser to select a cookies.txt file."""
        file_selected = filedialog.askopenfilename(
            title="Select cookies.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_selected:
            self.cookie_file_path.set(file_selected)
            self.cookie_var.set("None")  # Clear browser selection
            self.cookie_file_button.configure(text=f"...{file_selected[-20:]}")

    def browse_folder(self):
        """Open folder browser dialog to select download folder."""
        folder_selected = filedialog.askdirectory(
            title="Select Download Folder",
            initialdir=self.download_path.get()
        )
        if folder_selected:  # If user didn't cancel
            self.download_path.set(folder_selected)
            # Update the display label with truncated path if too long
            display_path = folder_selected
            if len(display_path) > 40:
                display_path = "..." + display_path[-37:]
            self.folder_path_label.configure(text=display_path)
            
            # Ensure the selected folder exists
            os.makedirs(folder_selected, exist_ok=True)

    def show_message_threadsafe(self, message_type, title, message):
        """Thread-safe method to show messages."""
        self.app.after(0, partial(self._show_message, message_type, title, message))
    
    def _show_message(self, message_type, title, message):
        """Show message in main thread."""
        if message_type == "info":
            messagebox.showinfo(title, message)
        elif message_type == "error":
            messagebox.showerror(title, message)
    
    def update_ui_threadsafe(self, updates):
        """Thread-safe method to update UI elements."""
        self.app.after(0, partial(self._update_ui, updates))
    
    def _update_ui(self, updates):
        """Update UI elements in main thread."""
        for element, properties in updates.items():
            if element == "progress_bar":
                if "value" in properties:
                    self.progress_bar.set(properties["value"])
            elif element == "progress_label":
                if "text" in properties:
                    self.progress_label.configure(text=properties["text"])
            elif element == "status_label":
                if "text" in properties:
                    self.status_label.configure(text=properties["text"])
            elif element == "download_button":
                if "state" in properties:
                    self.download_button.configure(state=properties["state"])
            elif element == "url_var":
                if "value" in properties:
                    self.url_var.set(properties["value"])
    def progress_hook(self, d):
        """Handle progress updates for the download."""
        if d['status'] == 'downloading':
            if 'downloaded_bytes' in d and 'total_bytes' in d and d['total_bytes'] is not None:
                progress = d['downloaded_bytes'] / d['total_bytes']
                percentage = progress * 100
                self.update_ui_threadsafe({
                    "progress_bar": {"value": progress},
                    "progress_label": {"text": f"Downloading: {percentage:.1f}%"}
                })
            elif 'downloaded_bytes' in d and 'total_bytes_estimate' in d and d['total_bytes_estimate'] is not None:
                progress = d['downloaded_bytes'] / d['total_bytes_estimate']
                percentage = progress * 100
                self.update_ui_threadsafe({
                    "progress_bar": {"value": progress},
                    "progress_label": {"text": f"Downloading: {percentage:.1f}%"}
                })
            elif '_percent_str' in d:
                # Fallback for when byte information isn't available
                percent_str = d['_percent_str'].strip('%')
                try:
                    percentage = float(percent_str)
                    self.update_ui_threadsafe({
                        "progress_bar": {"value": percentage / 100},
                        "progress_label": {"text": f"Downloading: {percentage:.1f}%"}
                    })
                except ValueError:
                    pass
        elif d['status'] == 'finished':
            self.update_ui_threadsafe({
                "progress_bar": {"value": 1.0},
                "progress_label": {"text": "Processing..."}
            })

    def get_format_selector(self, quality):
        """Get the appropriate format selector based on quality choice with fallbacks."""
        format_selectors = {
            "4K (2160p)": "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best[height<=2160]/best",
            "1440p": "bestvideo[height<=1440]+bestaudio/best[height<=1440]/best[height<=1440]/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best[height<=1080]/best", 
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]/best[height<=720]/best",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]/best[height<=480]/best", 
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]/best[height<=360]/best",
            "best_available": "bestvideo+bestaudio/best",
            "h264_best": "bestvideo[vcodec*=avc1]+bestaudio/bestvideo[vcodec^=avc1]+bestaudio/best[vcodec*=avc1]/best",
            "h264_1080p": "bestvideo[vcodec*=avc1][height<=1080]+bestaudio/bestvideo[vcodec^=avc1][height<=1080]+bestaudio/best[vcodec*=avc1][height<=1080]/best[height<=1080]",
            "h264_720p": "bestvideo[vcodec*=avc1][height<=720]+bestaudio/bestvideo[vcodec^=avc1][height<=720]+bestaudio/best[vcodec*=avc1][height<=720]/best[height<=720]",
            "audio_only": "bestaudio/best[acodec!=none]/best"
        }
        return format_selectors.get(quality, "bestvideo+bestaudio/best")

    def start_download_thread(self):
        """Start download in a separate thread to prevent GUI freezing."""
        download_thread = threading.Thread(target=self.start_download)
        download_thread.daemon = True
        download_thread.start()

    def start_download(self):
        """Start the YouTube video download."""
        yt_link = self.url_var.get().strip()
        if not yt_link:
            self.show_message_threadsafe("error", "Error", "Please enter a YouTube URL")
            return

        # --- FIX STARTS HERE ---
        # Get the selected download folder from the StringVar
        download_folder = self.download_path.get()
        
        # Ensure the selected downloads directory exists
        os.makedirs(download_folder, exist_ok=True)
        # --- FIX ENDS HERE ---

        # Get selected quality
        selected_quality = self.quality_var.get()
        format_selector = self.get_format_selector(selected_quality)

        # Configure output template based on quality
        if selected_quality == "audio_only":
            outtmpl = os.path.join(download_folder, '%(title)s.%(ext)s')
        elif selected_quality.startswith("h264_"):
            outtmpl = os.path.join(download_folder, '%(title)s_%(height)sp_h264.%(ext)s')
        else:
            outtmpl = os.path.join(download_folder, '%(title)s_%(height)sp.%(ext)s')

        ydl_opts = {
            'format': format_selector,
            'outtmpl': outtmpl,
            'progress_hooks': [self.progress_hook],
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'no_warnings': False,
            # Add options to handle signature extraction issues
            'extractor_retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            # Force IPv4 to avoid potential networking issues
            'force_ipv4': True,
            # Additional options for high quality downloads
            'ignoreerrors': False,
            'prefer_ffmpeg': True,
        }

        # Apply cookie settings to bypass bot detection
        cookie_file = self.cookie_file_path.get()
        cookie_browser = self.cookie_var.get()
        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file
        elif cookie_browser != "None":
            ydl_opts['cookiesfrombrowser'] = (cookie_browser,)

        # Add merge format for video downloads
        if selected_quality != "audio_only":
            ydl_opts['merge_output_format'] = 'mp4'
        
        # Disable the download button during download
        self.update_ui_threadsafe({
            "download_button": {"state": "disabled"},
            "progress_label": {"text": "Starting download..."},
            "status_label": {"text": "Initializing..."},
            "progress_bar": {"value": 0}
        })

        try:
            self.update_ui_threadsafe({
                "status_label": {"text": "Extracting video information..."}
            })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First, extract video info to validate the URL
                info = ydl.extract_info(yt_link, download=False)
                video_title = info.get('title', 'Unknown')
                self.update_ui_threadsafe({
                    "status_label": {"text": f"Downloading: {video_title}"}
                })
                
                # Now download the video
                ydl.download([yt_link])
            
            self.update_ui_threadsafe({
                "progress_bar": {"value": 1.0},
                "progress_label": {"text": "Download completed!"},
                "status_label": {"text": "Ready to download"}
            })
            
            # Different success message for H.264 downloads
            if selected_quality.startswith("h264_"):
                self.show_message_threadsafe("info", "Success", f"'{video_title}' downloaded successfully in H.264 format (Premiere Pro compatible)!")
            else:
                self.show_message_threadsafe("info", "Success", f"'{video_title}' downloaded successfully!")
            
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            # Simplified error message for better readability
            if "Requested format is not available" in error_msg:
                if selected_quality.startswith("h264_"):
                    self.show_message_threadsafe("error", "Error", f"H.264 format at '{selected_quality}' quality is not available for this video. Try 'h264_best' or a different H.264 option.")
                else:
                    self.show_message_threadsafe("error", "Error", f"The requested quality '{selected_quality}' is not available for this video. Please try a different quality.")
            else:
                self.show_message_threadsafe("error", "Error", f"Download error: {error_msg}")

            self.update_ui_threadsafe({
                "status_label": {"text": "Download failed"}
            })
                
        except Exception as e:
            self.show_message_threadsafe("error", "Error", f"An unexpected error occurred: {str(e)}")
            self.update_ui_threadsafe({
                "status_label": {"text": "Download failed"}
            })
            
        finally:
            # Re-enable the download button and reset progress
            self.update_ui_threadsafe({
                "download_button": {"state": "normal"},
                "progress_bar": {"value": 0},
                "progress_label": {"text": ""}
            })

    def run(self):
        """Run the main application loop."""
        self.app.mainloop()


if __name__ == "__main__":
    app = YoutubeDownloader()
    app.run()