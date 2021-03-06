# PacktPub Downloader

Script to download all your PacktPub books inspired by https://github.com/ozzieperez/packtpub-library-downloader

Since PacktPub restructured their website [packtpub-library-downloader](https://github.com/ozzieperez/packtpub-library-downloader) became obsolete because the downloader used webscraping. So I figured out that now PacktPub uses a REST API. Then I found which endpoint to use for downloading books and made a simple script. Feel free to fork and PR to improve. Packtpub's API isn't documented :'(

## Usage:
    pip install -r requirements.txt
	python main.py -e <email> -p <password> [-d <directory> -b <book file types> -i <book ids> -l -s -v -q]

##### Example: Download books in PDF format
	python main.py -e hello@world.com -p p@ssw0rd -d ~/Desktop/packt -b pdf

## Commandline Options
- *-e*, *--email* = Your login email
- *-p*, *--password* = Your login password
- *-d*, *--directory* = Directory to download into. Default is "media/" in the current directory
- *-b*, *--books* = Assets to download. Options are: *pdf,mobi,epub,code*
- *-i*, *--ids* = Products to download by id, separated by commas (If not specified, all owned products will be downloaded)
- *-n*, *--number* = The number of most recently obtained books to check (This will be ignored when using *-i*)
- *-l*, *--parallel* = Download the books in parallel (implies *-q*)
- *-s*, *--separate* = Create a separate directory for each book
- *-v*, *--verbose* = Show more detailed information
- *-q*, *--quiet* = Don't show information or progress bars

    Please note that *-v* and *-q* override each other; the last argument passed to the script will be used. 

**Book File Types**

- *pdf*: PDF format
- *mobi*: MOBI format
- *epub*: EPUB format
- *code*: Accompanying source code, saved as .zip files

I'm working on Python 3.6.0 
