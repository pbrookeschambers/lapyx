from bs4 import BeautifulSoup
import os
from pathlib import Path
import re
import time

import progressbar


def get_all_files(path):
    if isinstance(path, str):
        path = Path(path)
    # recursively get all html files
    files = []
    # for root, dirs, filenames in os.walk(path):
    #     root = Path(root)
    #     for f in filenames:
    #         f = Path(f)
    #         if f.suffix == '.html':
    #             # if the file was modified within the last 30 seconds, add it
    #             if (root / f).stat().st_mtime > time.time() - 30:
    #                 files.append(root / f)

    for path_obj in path.rglob('*.html'):
        if path_obj.stat().st_mtime > time.time() - 30:
            files.append(path_obj)

    return files

def replace_titles_with_links(file, root_path):
    global quiet
    if isinstance(file, str):
        file = Path(file)
    with open(file, "r") as f:
        soup = BeautifulSoup(f, 'html.parser')
    # find any spans with classes "sig-name descname"
    # get the span inside the span
    # get its text
    # parse the text as a link with parse_link
    # replace the text with an a tag with the link and original text
    i = 0
    for span in soup.find_all('span', class_='sig-name descname'):
        # get the span inside the span
        inner_span = span.find('span')
        # get the text
        text = inner_span.text
        # parse the text as a link
        try:
            url, external = parse_link(text, file.parent)
        except FileNotFoundError:
            # print the error, print the original span, and continue
            print(f"Could not find file for link {text}")
            print(span)
            continue
        # if the url and the file are the same, continue
        url = str(url).strip()
        fname = str(file.name).strip()
        if url == fname or url.endswith(fname):
            continue
        i += 1
        # replace the text with an a tag
        a = soup.new_tag('a', href=url)
        if external:
            a['target'] = '_blank'
        a.string = text
        inner_span.replace_with(a)
    if i > 0 and not quiet:
        print(f"Found {i} class or function link{'s' if i > 1 else ''} in file {file}")
        # Write the new html to the file
        with open(file, 'w') as f:
            f.write(str(soup))

def replace_codelinks(file, root_path):
    global quiet
    # using BeautifulSoup, find any span tags with class "codelink"
    # Replace them with a tags, contents of which is preformatted inline code
    # code.docutils.literal.notranslate
    if isinstance(file, str):
        file = Path(file)
    with open(file, 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
    i = 0
    for span in soup.find_all('span', class_='codelink'):
        i +=1
        # Span contents will be of the form "Content <url>"
        # We want to extract the url and the content
        span_text = span.text
        content = re.sub(r'\<(.*?)\>', '', span_text).strip()
        # check if a url is present
        if '<' in span_text:
            url = re.search(r'\<(.*?)\>', span_text).group(1)
            url, external = parse_link(url, root_path)
        else:
            url, external = parse_link(content, root_path)
        

        url = str(url).strip()
        fname = str(file.name).strip()
        if url == fname or url.endswith(fname):
            # set the inner html of the a tag to a code tag with the content and classes "docutils literal notranslate"
            new_code = soup.new_tag('code', **{'class': 'docutils literal notranslate'})
            new_code.string = content
            span.replace_with(new_code)
            continue
        # Create a new a tag, and replace the span with it
        a = soup.new_tag('a', href=url)
        # if it's external, add target="_blank"
        if external:
            a['target'] = '_blank'
        # set the inner html of the a tag to a code tag with the content and classes "docutils literal notranslate"
        new_code = soup.new_tag('code', **{'class': 'docutils literal notranslate'})
        new_code.string = content
        a.append(new_code)
        span.replace_with(a)
        # print(span_text)
        # print(a)

    if i > 0 and not quiet:
        print(f"Found {i} codelink{'s' if i > 1 else ''} in file {file}")
        # Write the new html to the file
        with open(file, 'w') as f:
            f.write(str(soup))

def parse_link(link, root_path):
    # link could be a file, file and header, header, or a python module, class or function.
    # If a file, return the file. Could be a relative path, just check for .html extension
    # If a file and header, return the file and the header - check for #, check for .html extension
    # If a header, we won't know.
    # If a python module, class or function
    #   Convert to file path, add .html, check for existence
    #   If it exists, return the file
    #   If it doesn't exist, return None

    if isinstance(root_path, str):
        root_path = Path(root_path)

    external = False
    if link.endswith('.html'):
        return link, external
    # if it's a valid url already, return it
    if link.startswith('http'):
        return link, True
    elif '#' in link:
        file, header = link.split('#')
        if file.endswith('.html'):
            return link, external
        else:
            # We don't know what the file is, so we can't do anything
            return "", external
    else:
        if link.endswith("()"):
            # it's a function, so file name will not have brackets
            link = link[:-2]
        if "." not in link:
            # traverse the directory structure recursively to find the file, adding .html extension
            # if it exists, return the file as relative from root_path
            # if it doesn't exist, return None
            for path in root_path.glob('**/*.html'):
                if path.stem == link:
                    # return the path relative to the root_path
                    return path.relative_to(root_path), external

            raise FileNotFoundError(f"Could not find file for link {link}")
        return link.replace('.', '/') + '.html', external

def main():
    # check for ../../_build
    if os.path.isdir('../../_build'):
        root_path = '../../_build'
    else:
        root_path = '../build/html'

    files = get_all_files(root_path)
    if len(files) == 0:
        print("No files with recent changes found.")
        return
    for file in progressbar.progressbar(files, redirect_stdout=True):
        replace_codelinks(file, root_path)
        replace_titles_with_links(file, root_path)


if __name__ == '__main__':
    global quiet
    quiet = False
    # check for `-q` or --quiet` in the command line arguments
    import sys
    if '-q' in sys.argv or '--quiet' in sys.argv:
        quiet = True
    main()
