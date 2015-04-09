# feeds2fb2


## Summary
feeds2fb2 converts RSS feeds (extracted from [OPML](http://en.wikipedia.org/wiki/OPML) file or simple text file with list inside) into [FB2](http://en.wikipedia.org/wiki/Fb2) book or books.
FB2 books can be easily viewed on e-book readers: PocketBook, LBook V3 (Hanlin V3), etc.

feeds2fb2 converter has a few options - images in posts can be enabled/disabled, output file can be zipped or not, etc.


## Note
feeds2fb2 is not in development anymore because I don't have time for it.

if you want to commit fixes, please do a pull request.
If you need some specific tuning, you can ping me by emai: [sergey@polzunov.com](mailto:sergey@polzunov.com)

## Usage

### Summary

```
$ feeds2fb2.py -t FILETYPE [options] FILE_TO_PARSE OUTPUT_NAME

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

### Examples

*example 0*. Converting simple text file with 1 url inside. Result file name is "result.fb2"
```
$ ./feeds2fb2.py -t text ./text-example.txt result.fb2
    [ http://googlerussiablog.blogspot.com/atom.xml ]      Google Russia
Converting HTML tags for feed... done
Done
```

*example 1*. Converting OPML file in book-per-feed mode. There are no labels/tags in OPML file
```
$ ./feeds2fb2.py -t opml --book-per-feed ./opml-example.xml
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

*example 2*. Converting text file with URLs inside info fb2 book with images titled "My Feeds"
```
$ ./feeds2fb2.py -t text --enable-pics --title="My Feeds" ./text-example2.txt result.fb2
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


Changes
-------
v0.4
  * *Dirty HTML (text with unclosed/unopened tags) sanitization has been added*.
  * *Bug-fixes and hacks*. Due to LBook/Hanling Fb2 plugin restrictions there are no way to present some HTML text blocks in good-looking form in fb2 format for LBook/Hanlin V3. So we are waiting for css-in-book support and special chars/symbols support.

v0.3
  * *Timestamps are added*. The feed's last update time is saved in config file "feed2fb2.timestamp". Next time you run the script you will get only new posts. You can get all the posts with `--get-all-posts` as well
  * *Output name*. The output parameter's behavior was changed - it is now a result file name by default OR name of the directory where all books will be placed in `--book-per-feed` mode
  * *ZIP archive support added*. By default all result files are zipped

v0.2
  * *Images in posts*. By default images in posts are disabled so if you want to convert images from \<img\> from your feeds to fb2 book you should set the `--enable-pics` flag
  * *Book-per-feed mode*. It is an optional mode. Every book title consist of a label (if input data is an OPML file with labels) and a feed title. You can enable this mode with the `--book-per-feed` flag
  * *.sh and .bat scripts* for easy Google Reader OPML to FB2 book convertation are added

v0.1
  * *2 types of input data*. OPML file or a simple text file with feedURL-per-line style
  * *Optional customised book title*. You can specify your custom book title with `--title` flag
