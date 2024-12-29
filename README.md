# YouTube Video Downloader

A desktop application built with Python and CustomTkinter that allows users to download YouTube videos in high quality.

## Features

- User-friendly GUI interface
- Download progress indicator
- High-quality video and audio download
- Automatic file organization in downloads folder
- Error handling with user feedback
- MP4 output format

## Prerequisites

Before running this application, make sure you have the following installed:

- Python 3.7 or higher
- FFmpeg
- Required Python packages

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/youtube-downloader.git
cd youtube-downloader
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
- macOS (using Homebrew):
  ```bash
  brew install ffmpeg
  ```
- Windows: Download from [FFmpeg official website](https://ffmpeg.org/download.html)
- Linux:
  ```bash
  sudo apt install ffmpeg
  ```

## Usage

1. Run the application:
```bash
python main.py
```

2. Paste a YouTube URL into the input field
3. Click "Download" button
4. The video will be saved to the `downloads` folder

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.