# -*- coding: utf-8 -*-
#!/usr/bin/python

from __future__ import print_function
import os
import sys
import glob
import math
import getopt
import requests
import time
from tqdm import tqdm, trange
from config import BASE_URL, PRODUCTS_ENDPOINT, URL_BOOK_TYPES_ENDPOINT, URL_BOOK_ENDPOINT
from user import User


#TODO: I should do a function that his only purpose is to request and return data

def book_request(user, offset=0, limit=10, verbose=False):
    data = []
    url = BASE_URL + PRODUCTS_ENDPOINT.format(offset=offset, limit=limit)
    if verbose:
        print(url)
    r = requests.get(url, headers=user.get_header())

    data += r.json().get('data', [])

    return url, r, data

def get_books(user, offset=0, limit=10, is_verbose=False, is_quiet=False):
    '''
        Request all your books, return json with info of all your books
        Params
        ...
        header : str
        offset : int
        limit : int
            how many book wanna get by request
    '''
    # TODO: given x time jwt expired and should refresh the header, user.refresh_header()

    tries = 0

    url, r, data = book_request(user, offset, limit)

    while tries <=5:
        try:
            print(f'You have {str(r.json()["count"])} books')
            print("Getting list of books...")

            if not is_quiet:
                pages_list = trange(r.json()['count'] // limit, unit='Pages')
            else:
                pages_list = range(r.json()['count'] // limit)
            for i in pages_list:
                offset += limit
                data += book_request(user, offset, limit, is_verbose)[2]
            return data

        except KeyError:
            tries += 1
            user.refresh_header()
            print("There was an error retrieving your data.")
            print("Retrying...")
            url, r, data = book_request(user, offset, limit)

    print("An error has occurred!")
    print("Here is the information:")
    print("Url is", url, "\n\nRetrieved data is", r.json())
    print("Exiting now")
    raise SystemExit

def get_book_info(user, book_id, format='pdf', retrieve_types=False, tries=0):
    '''
        Return url of the book or list with file types of a book
    '''
    if retrieve_types:
        url = BASE_URL + URL_BOOK_TYPES_ENDPOINT.format(book_id=book_id)
    else:
        url = BASE_URL + URL_BOOK_ENDPOINT.format(book_id=book_id, format=format)

    r = requests.get(url, headers=user.get_header())

    if r.status_code == 200: # success
        return r.json().get('data', '')

    elif tries <= 5:
        if r.status_code == 401: # jwt expired 
            user.refresh_header() # refresh token 

        elif r.status_code // 100 == 5:
            tries += 1
            print("There has been a server error, retrying in 5 seconds...")
            time.sleep(5)

        get_book_info(user, book_id, format, retrieve_types, tries)  # call recursive 

    print('ERROR (please copy and paste in the issue)')
    print(r.json())
    print(r.status_code)

    if retrieve_types:
        return ''
    else:
        return []


# TODO: i'd like that this functions be async and download faster
def download_book(filename, url):
    '''
        Download your book
    '''
    print('Starting to download ' + filename)

    with open(filename, 'wb') as f:
        r = requests.get(url, stream=True)
        total = r.headers.get('content-length')
        if total is None:
            f.write(response.content)
        else:
            total = int(total)
            # TODO: read more about tqdm
            for chunk in tqdm(r.iter_content(chunk_size=1024), total=math.ceil(total//1024), unit='KB', unit_scale=True):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            print('Finished ' + filename)


def make_zip(filename):
    if filename[-4:] == 'code':
        os.replace(filename, filename[:-4] + 'zip')


def move_current_files(root, book):
    sub_dir = f'{root}/{book}'
    does_dir_exist(sub_dir)
    for f in glob.iglob(sub_dir + '.*'):
        try:
            os.rename(f, f'{sub_dir}/{book}' + f[f.index('.'):])
        except OSError:
            os.rename(f, f'{sub_dir}/{book}' + '_1' + f[f.index('.'):])
        except ValueError as e:
            print(e)
            print('Skipping')


def does_dir_exist(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            print(e)
            sys.exit(2)


def main(argv):
    # thanks to https://github.com/ozzieperez/packtpub-library-downloader/blob/master/downloader.py
    email = None
    password = None
    root_directory = 'media'
    book_file_types = ['pdf', 'mobi', 'epub', 'code']
    separate = None
    verbose = None
    quiet = None
    errorMessage = 'Usage: main.py -e <email> -p <password> [-d <directory> -b <book file types> -s -v -q]'

    # get the command line arguments/options
    try:
        opts, args = getopt.getopt(
            argv, 'e:p:d:b:svq', ['email=', 'pass=', 'directory=', 'books=', 'separate', 'verbose', 'quiet'])
    except getopt.GetoptError:
        print(errorMessage)
        sys.exit(2)

    # hold the values of the command line options
    for opt, arg in opts:
        if opt in ('-e', '--email'):
            email = arg
        elif opt in ('-p', '--pass'):
            password = arg
        elif opt in ('-d', '--directory'):
            root_directory = os.path.expanduser(
                arg) if '~' in arg else os.path.abspath(arg)
        elif opt in ('-b', '--books'):
            book_file_types = arg.split(',')
        elif opt in ('-s', '--separate'):
            separate = True
        elif opt in ('-v', '--verbose'):
            verbose = True
        elif opt in ('-q', '--quiet'):
            quiet = True

    if verbose and quiet:
        print("Verbose and quiet cannot be used together.")
        sys.exit(2)

    # do we have the minimum required info?
    if not email or not password:
        print(errorMessage)
        sys.exit(2)

    # check if not exists dir and create
    does_dir_exist(root_directory)

    # create user with his properly header
    user = User(email, password)

    # get all your books
    books = get_books(user, is_verbose=verbose, is_quiet=quiet)
    print('Downloading books...')
    if not quiet:
        books_iter = tqdm(books, unit='Book')
    else:
        books_iter = books
    for book in books_iter:
        # get the different file type of current book
        file_types = get_book_info(user, book['productId'], retrieve_types=True)
        for file_type in file_types:
            if file_type in book_file_types:  # check if the file type entered is available by the current book
                book_name = book['productName'].replace(' ', '_').replace('.', '_').replace(':', '_').replace('/','')
                if separate:
                    filename = f'{root_directory}/{book_name}/{book_name}.{file_type}'
                    move_current_files(root_directory, book_name)
                else:
                    filename = f'{root_directory}/{book_name}.{file_type}'
                # get url of the book to download
                url = get_book_info(user, book['productId'], format=file_type)
                if url == "":
                    tqdm.write(f'There was an error retrieving {filename}. Skipping...')
                elif not os.path.exists(filename) and not os.path.exists(filename.replace('.code', '.zip')):
                    download_book(filename, url)
                    make_zip(filename)
                else:
                    if verbose:
                        tqdm.write(f'{filename} already exists, skipping.')


if __name__ == '__main__':
    main(sys.argv[1:])
