import re
import win32clipboard

def get_clipboard_html():
    try:
        win32clipboard.OpenClipboard()
    except Exception:
        return None, False
    try:
        cf_html = win32clipboard.RegisterClipboardFormat("HTML Format")
        if win32clipboard.IsClipboardFormatAvailable(cf_html):
            data = win32clipboard.GetClipboardData(cf_html)
            html_data = data.decode("utf-8", errors="ignore")
            match = re.search(
                r'<!--StartFragment-->(.*?)<!--EndFragment-->',
                html_data, re.IGNORECASE | re.DOTALL
            )
            if match:
                return match.group(1), True
    finally:
        win32clipboard.CloseClipboard()
    return None, False

def set_clipboard_html(html_fragment):
    header = (
        "Version:0.9\r\n"
        "StartHTML:{0:08d}\r\n"
        "EndHTML:{1:08d}\r\n"
        "StartFragment:{2:08d}\r\n"
        "EndFragment:{3:08d}\r\n"
    )
    html_template = (
        "<html>\r\n<body>\r\n"
        "<!--StartFragment-->{fragment}<!--EndFragment-->\r\n"
        "</body>\r\n</html>"
    )

    dummy_header = header.format(0, 0, 0, 0)
    start_html = len(dummy_header)
    html_content = html_template.format(fragment=html_fragment)
    end_html = start_html + len(html_content.encode('utf-8'))
    start_fragment = (start_html + html_content.find("<!--StartFragment-->")
                      + len("<!--StartFragment-->"))
    end_fragment = start_html + html_content.find("<!--EndFragment-->")

    final_header = header.format(start_html, end_html, start_fragment, end_fragment)
    cf_html_data = (final_header + html_content).encode('utf-8')
    plain_text = re.sub(r'<[^>]+>', '', html_fragment)

    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(plain_text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.SetClipboardData(
            win32clipboard.RegisterClipboardFormat("HTML Format"), cf_html_data
        )
    finally:
        win32clipboard.CloseClipboard()