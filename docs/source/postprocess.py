from bs4 import BeautifulSoup
import os
import re
import time

import progressbar


def get_all_files(path):
    # recursively get all html files
    files = []
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
            if f.endswith('.html'):
                # if the file was modified within the last 30 seconds, add it
                if os.path.getmtime(os.path.join(root, f)) > time.time() - 30:
                    files.append(os.path.join(root, f))
    return files

def replace_codelinks(file, root_path):
    # using BeautifulSoup, find any span tags with class "codelink"
    # Replace them with a tags, contents of which is preformatted inline code
    # code.docutils.literal.notranslate
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

    if i > 0:
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
            for root, dirs, files in os.walk(root_path):
                for f in files:
                    if f == link + '.html':
                        # return path relative from root_path
                        return os.path.relpath(os.path.join(root, f), root_path), external
            return ""
        return link.replace('.', '/') + '.html', external

def main():
    # check for ../_build
    if os.path.isdir('../_build'):
        root_path = '../_build/html'
    else:
        root_path = '../build/html'
    files = get_all_files(root_path)
    for file in progressbar.progressbar(files, redirect_stdout=True):
        replace_codelinks(file, root_path)

if __name__ == '__main__':
    main()
