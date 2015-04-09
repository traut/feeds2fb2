
```
feeds2fb2.py -t FILETYPE [options] FILE_TO_PARSE OUTPUT_NAME

  -t FILETYPE           - here filetype is opml (OPML file) or text (simple text file with URLs to RSS feeds one at line)

  Optional settings:
         --title FB2BOOK_TITLE   - here you can specify the result fb2 book title.
         --enable-pics           - enables images convertation into fb2-formated embedded images.
         --book-per-feed         - enables fb2 book per feed mode. Every feed is created as a separate fb2 file.
         --disable-zip           - disables zip packing of the result fb2 file/files (enabled by default).
         --get-all-posts         - set this option if you want to get all RSS posts (not just the latest).

  FILE_TO_PARSE         - the name of an input file (opml or simple text file).

  OUTPUT_NAME           1. in "book-per-feed" mode books with feeds are placed into the directory with the name of OUTPUT_NAME.
                           By default OUTPUT_NAME is a current directory.
                        2. in default mode it is a name of the result fb2 book file without "fb2" extension
```

## Examples ##

**example 0**. Converting simple text file with 1 url inside. Result file name is "result.fb2"
```
    traut@traut-laptop:~/_workspace/_devel/python/feeds2fb2$ ./feeds2fb2.py -t text ./text-example.txt result.fb2
        [ http://googlerussiablog.blogspot.com/atom.xml ]      Google Russia
    Converting HTML tags for feed... done
    Done
```

**example 1**. Converting OPML file in book-per-feed mode. There are no labels/tags in OPML file
```
    traut@traut-laptop:~/_workspace/_devel/python/feeds2fb2$ ./feeds2fb2.py -t opml --book-per-feed ./opml-example.xml
    processing label "Unlabeled"
        [ http://www.the-ebook.org/e107/e107_files/backend/news.xml ]   The-eBook Russia
        [ http://out.com.ua/blog/feed/ ]        Thoughts Thru Oxygen
        [ http://2read.ru/feed/ ]       Blog "Tech book"
        [ http://www.habrahabr.ru/rss/main/ ]   Habrahabr
    Converting HTML tags for feed... done
    Converting HTML tags for feed... done
    Converting HTML tags for feed... done
    Converting HTML tags for feed... done
    Done
```

**example 2**. Converting text file with URLs inside info fb2 book with images titled "My Feeds"
```
    traut@traut-laptop:~/_workspace/_devel/python/feeds2fb2$ ./feeds2fb2.py -t text --enable-pics --title="My Feeds" ./text-example2.txt result.fb2
        [ http://bash.org.ru/rss ]      Bash.Org.Ru
        [ http://googlerussiablog.blogspot.com/atom.xml ]       Google Russia
        [ http://www.the-ebook.org/e107/e107_files/backend/news.xml ]   The-eBook Russia
    Converting HTML tags for feed... done
    Getting image from http://www.the-ebook.org/files/ifb2lrfsmallos1.png
    Getting image from http://bp1.blogger.com/_r6mLyAa9wE0/Rg_yCaIHPOI/AAAAAAAAAAk/FdjlItZqSwU/s320/71410563_ed1502fcaf_m.jpg
    Getting image from http://www.google.ru/ig/modules/eyes-thm.png
    Getting image from http://lh3.google.com/image/aldanur/RjMHtt2ubmE/AAAAAAAAHkg/ZLANKz8LsNE/s160-c/Google.jpg
    Getting image from http://images2.photomania.com/230558/1/radB0709.jpg  ERROR: cannot get image content
    Getting image from http://www.google.ru/ig/cache/6e/e9/6ee956913425c59002ec526bdf62f9dc-thm.png
    ...
    Done
```