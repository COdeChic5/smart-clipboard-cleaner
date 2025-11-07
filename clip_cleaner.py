#!/usr/bin/env python3
import re
import argparse
import sys
from pathlib import Path

# optional imports (handle if not installed)
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except Exception:
    PYPERCLIP_AVAILABLE = False

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
    COLOR_AVAILABLE = True
except Exception:
    COLOR_AVAILABLE = False
    # fallback simple names so code doesn't crash
    class Fore:
        RED = ""
        GREEN = ""
        YELLOW = ""
        CYAN = ""
    class Style:
        BRIGHT = ""
        RESET_ALL = ""


# Cleaning helpers

# language punctuation map (add more as you want)
LANG_PUNCT_MAP = {
    "¿": "?", "¡": "!", "«": '"', "»": '"', "—": "-", "–": "-", "…": "...",
}

FANCY_DOUBLE = ['“', '”']
FANCY_SINGLE = ['‘', '’']

UTM_PATTERN = re.compile(r'\?utm_[^\s\n]+')   # find ?utm_... until whitespace/newline
MULTISPACE_PATTERN = re.compile(r'\s+')

def clean_text(text: str, language_mode: bool = False, summary: dict | None = None) -> str:
    """
    Clean text with optional language-mode replacements.
    summary: optional dict to collect counts of replacements.
    """
    if summary is None:
        summary = {}

    # count fancy quotes before replacing
    double_count = sum(text.count(ch) for ch in FANCY_DOUBLE)
    single_count = sum(text.count(ch) for ch in FANCY_SINGLE)
    summary['fancy_double_before'] = double_count
    summary['fancy_single_before'] = single_count

    # replace fancy quotes
    for ch in FANCY_DOUBLE:
        text = text.replace(ch, '"')
    for ch in FANCY_SINGLE:
        text = text.replace(ch, "'")

    # language mode: replace punctuation map
    if language_mode:
        replaced = 0
        for src, dst in LANG_PUNCT_MAP.items():
            if src in text:
                count = text.count(src)
                replaced += count
                text = text.replace(src, dst)
        summary['lang_punct_replaced'] = replaced

    # remove multiple spaces/tabs/newlines -> single space, but preserve intentional newlines: 
    # Here we replace consecutive spaces/tabs with a single space, and collapse spaces around newlines
    # First normalize newlines to single \n, then collapse other whitespace:
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # replace sequences of whitespace (excluding single newline) with a single space
    # To keep paragraphs, we convert all runs of whitespace that are not double-newline into single spaces.
    # Simpler approach for this project: collapse any whitespace to single space, then re-insert single newlines for readability.
    text = MULTISPACE_PATTERN.sub(' ', text).strip()
    # optionally: keep single newlines by replacing ' . ' to '\n' if necessary - skipping to keep simple

    # find and remove UTM tracking params and count how many removed
    utm_matches = UTM_PATTERN.findall(text)
    summary['utm_removed_count'] = len(utm_matches)
    text = UTM_PATTERN.sub('', text)

    # final cleanup: collapse any accidental double spaces caused by removals
    text = MULTISPACE_PATTERN.sub(' ', text).strip()

    summary['final_length'] = len(text)
    return text

# ----------------------
# CLI and flow
# ----------------------
def printc(msg: str, color: str = ""):
    if COLOR_AVAILABLE and color:
        print(color + msg + Style.RESET_ALL)
    else:
        print(msg)

def process_clipboard(language_mode: bool, show_summary: bool):
    if not PYPERCLIP_AVAILABLE:
        printc("pyperclip not installed or unavailable. Clipboard mode won't work.", Fore.RED)
        return
    raw = pyperclip.paste()
    if not raw:
        printc("Clipboard is empty.", Fore.YELLOW)
        return
    summary = {}
    cleaned = clean_text(raw, language_mode=language_mode, summary=summary)
    pyperclip.copy(cleaned)
    printc("Clipboard cleaned and copied back to clipboard.", Fore.GREEN)
    if show_summary:
        show_summary_info(summary, raw, cleaned)

def process_file(path: Path, language_mode: bool, show_summary: bool):
    if not path.exists():
        printc(f"File not found: {path}", Fore.RED)
        return
    raw = path.read_text(encoding='utf-8')
    summary = {}
    cleaned = clean_text(raw, language_mode=language_mode, summary=summary)
    out_path = path.parent / f"cleaned_{path.name}"
    out_path.write_text(cleaned, encoding='utf-8')
    printc(f"Cleaned file written: {out_path}", Fore.GREEN)
    if show_summary:
        show_summary_info(summary, raw, cleaned)

def process_stdin(language_mode: bool, show_summary: bool):
    printc("Paste your text. Press Enter twice on an empty line (or Ctrl+D/Ctrl+Z) to end:", Fore.CYAN)
    lines = []
    try:
        while True:
            line = sys.stdin.readline()
            if not line:  # EOF
                break
            if line.strip() == "":
                break
            lines.append(line.rstrip("\n"))
    except KeyboardInterrupt:
        pass
    raw = "\n".join(lines)
    if not raw:
        printc("No input received.", Fore.YELLOW)
        return
    summary = {}
    cleaned = clean_text(raw, language_mode=language_mode, summary=summary)
    printc("\n--- Cleaned Output ---\n", Fore.CYAN)
    print(cleaned)
    if show_summary:
        show_summary_info(summary, raw, cleaned)

def show_summary_info(summary: dict, raw: str, cleaned: str):
    printc("\n--- Summary ---", Fore.CYAN)
    # fancy quotes removed
    dd = summary.get('fancy_double_before', 0)
    ds = summary.get('fancy_single_before', 0)
    utm = summary.get('utm_removed_count', 0)
    lang = summary.get('lang_punct_replaced', 0)
    printc(f"Fancy double quotes replaced: {dd}", Fore.YELLOW)
    printc(f"Fancy single quotes replaced: {ds}", Fore.YELLOW)
    printc(f"UTM tracking parts removed: {utm}", Fore.YELLOW)
    if 'lang_punct_replaced' in summary:
        printc(f"Language punctuation replacements: {lang}", Fore.YELLOW)
    printc(f"Original length: {len(raw)}", Fore.CYAN)
    printc(f"Cleaned length: {len(cleaned)}", Fore.CYAN)

def build_arg_parser():
    p = argparse.ArgumentParser(description="Smart Clipboard & File Cleaner")
    g = p.add_mutually_exclusive_group()
    g.add_argument('--clipboard', '-c', action='store_true', help="Read from clipboard and copy cleaned text back")
    g.add_argument('--file', '-f', type=str, help="Path to a .txt file to clean (output: cleaned_<filename>)")
    # default is stdin if neither clipboard nor file specified
    p.add_argument('--language', '-l', action='store_true', help="Apply language punctuation replacements (¿ ¡ « » etc.)")
    p.add_argument('--no-color', action='store_true', help="Disable color output")
    p.add_argument('--summary', action='store_true', help="Show a summary of what was changed")
    return p

def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    global COLOR_AVAILABLE
    if args.no_color:
        COLOR_AVAILABLE = False

    if args.clipboard:
        process_clipboard(language_mode=args.language, show_summary=args.summary)
        return

    if args.file:
        p = Path(args.file)
        process_file(p, language_mode=args.language, show_summary=args.summary)
        return

    # default: stdin interactive mode
    process_stdin(language_mode=args.language, show_summary=args.summary)

if __name__ == "__main__":
    main()
