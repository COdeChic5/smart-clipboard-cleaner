# 🧠 Smart Clipboard Cleaner

A smart Python tool that **cleans and formats messy text** — whether it’s copied to your clipboard, stored in a file, or pasted directly into the terminal.  
It removes unwanted spaces, fancy quotes, emojis, UTM links, and fixes punctuation for multiple languages.


## 🚀 Features
- 🧹 Cleans up messy clipboard or text file content
- ✨ Replaces fancy quotes (‘ ’ “ ”) with normal ones
- 🌍 Optional *language punctuation* normalization (¿ → ?, ¡ → !, etc.)
- 🔗 Removes UTM tracking parameters from URLs
- 🧠 Works in three modes — clipboard, file, or direct text input
- 🧾 Optional summary report of changes made
- 🎨 Colored terminal output (auto-disables if not supported)


## ⚙️ Installation

1. **Clone or download** this repository:
   ```bash
   git clone https://github.com/COdeChic5/smart-clipboard-cleaner.git
   cd smart-clipboard-cleaner

Install dependencies:
pip install pyperclip colorama


How to Run

You can use this tool in three ways:
1. Clipboard Mode

Automatically clean whatever text is currently copied in your clipboard.

python clip_cleaner.py --clipboard


After running, the cleaned text is copied back to your clipboard.

Example:

python clip_cleaner.py --clipboard --summary


💡 Add --summary to see what was changed.

📄 2. File Mode

Clean the contents of a .txt file and create a new one with the prefix cleaned_.

python clip_cleaner.py --file example.txt


Output:

cleaned_example.txt


You can also combine options:

python clip_cleaner.py --file notes.txt --language --summary


This applies language-specific punctuation fixes and shows a summary of edits.

💬 3. Interactive (stdin) Mode

Paste or type text directly into the terminal.

python clip_cleaner.py


Then paste your messy text, press Enter twice, and see the cleaned result.

⚡ Optional Arguments
Flag	Description
--clipboard, -c	Clean text directly from your clipboard
--file <path>, -f	Clean a specific text file
--language, -l	Enable multilingual punctuation fixes
--summary	Show detailed summary of changes made
--no-color	Disable colored output for plain terminals
🧩 Example Usages

Clean clipboard and show summary:

python clip_cleaner.py -c --summary


Clean file with language punctuation enabled:

python clip_cleaner.py -f essay.txt -l


Paste text manually:

python clip_cleaner.py

🧑‍💻 Author

COdeChic5

Crafted with ❤️ using Python.