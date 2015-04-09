# feeds2fb2 is looking for developers #

## Summary ##
Converting RSS feeds (taking from [OPML](http://en.wikipedia.org/wiki/OPML) file or simple text file with list inside) into [fb2](http://en.wikipedia.org/wiki/Fb2) book/books. fb2 books can be easily viewed on LBook V3 (Hanlin V3) reader, etc

feeds2fb2 converter has a few options - images in posts can be enabled/disabled, output file can be zipped or not, etc.


---

### NOTE: ###
feeds2fb2 is not in development now because I don't (as it's owner) have time for it.

if you want to commit fixes I would be glad to add you as a commiter for feeds2fb2 svn repo.
If you need some specific tuning, you can ping me by emai: [sergey@polzunov.com](mailto:sergey@polzunov.com)


---

## v0.4 ##
  * **Dirty HTML (text with unclosed/unopened tags) sanitization has been added**.
  * **Bug-fixes and hacks**. Due to LBook/Hanling Fb2 plugin restrictions there are no way to present some HTML text blocks in good-looking form in fb2 format for LBook/Hanlin V3. So we are waiting for css-in-book support and special chars/symbols support.

## v0.3 ##
  * **Timestamps are added**. The feed's last update time is saved in config file "feed2fb2.timestamp". Next time you run the script you will get only new posts. You can get all the posts with `--get-all-posts` as well
  * **Output name**. The output parameter's behavior was changed - it is now a result file name by default OR name of the directory where all books will be placed in `--book-per-feed` mode
  * **ZIP archive support added**. By default all result files are zipped

## v0.2 ##
  * **Images in posts**. By default images in posts are disabled so if you want to convert images from \<img\> from your feeds to fb2 book you should set the `--enable-pics` flag
  * **Book-per-feed mode**. It is an optional mode. Every book title consist of a label (if input data is an OPML file with labels) and a feed title. You can enable this mode with the `--book-per-feed` flag
  * **.sh and .bat scripts** for easy Google Reader OPML to FB2 book convertation are added

## v0.1 ##
  * **2 types of input data**. OPML file or a simple text file with feedURL-per-line style
  * **Optional customised book title**. You can specify your custom book title with `--title` flag