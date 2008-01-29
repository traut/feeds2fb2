#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# RSS feeds to FB2 converter
#
# Author: Sergey Polzunov (Traut) 
# email: traut<at>ukr.net
# blog: http://out.com.ua/blog
#
# Version 0.4

import xml.sax.handler
import xml.sax.saxutils as saxutils
import feedparser, time, locale, sys, getopt, md5, urllib, base64, re, locale, codecs, os, zipfile

local_lang, local_enc = locale.getdefaultlocale()
if local_enc == None:
    local_lang = 'en_US'
    local_enc = 'UTF8'

logfile_name = "feeds2fb2.log"
timestampfile_name = "feeds2fb2.timestamp"

def usage():
    usage = """
usage: feeds2fb2.py -t FILETYPE [options] FILE_TO_PARSE OUTPUT_NAME
    
  -t FILETYPE\t\t- here filetype is opml (OPML file) or text (simple text file with URLs to RSS feeds one at line)

Optional settings:
\t--title FB2BOOK_TITLE\t- here you can specify the result fb2 book title.
\t--enable-pics\t\t- enables images convertation into fb2-formated embedded images.
\t--book-per-feed\t\t- enables fb2 book per feed mode. Every feed is created as a separate fb2 file.
\t--disable-zip\t\t- disables zip packing of the result fb2 file/files (enabled by default).
\t--get-all-posts\t\t- set this option if you want to get all RSS posts (not just the latest).

  FILE_TO_PARSE\t\t- the name of an input file (opml or simple text file).

  OUTPUT_NAME\t\t1. in "book-per-feed" mode books with feeds are placed into the directory with the name of OUTPUT_NAME.
  \t\t\t   By default OUTPUT_NAME is a current directory.
  \t\t\t2. in default mode it is a name of the result fb2 book file without "fb2" extension"""
    print usage
    sys.exit(2)

class OMPLListHandler(xml.sax.handler.ContentHandler):
	
	def __init__(self):
		self.labels = {}
		self.freefeeds = []
		self.parents = []


	def startElement(self, name, attributes):

		if name == "outline":
			currentlabel = attributes.getValue("title")
			if (not "type" in attributes.getNames()):
				# we're in label tag
				if not currentlabel in self.labels.keys():
					self.labels[currentlabel] = []
				self.parents.append(currentlabel)
			elif len(self.parents) == 0:
				# we're in feed without label
				self.parents.append(currentlabel)
				self.freefeeds.append(attributes.getValue("xmlUrl"))
			else:
				# we're in feed with label
				label = self.parents[0]
				self.parents.append(currentlabel)
				self.labels[label].append(attributes.getValue("xmlUrl"))


	def characters(self, data):
		pass

	def endElement(self, name):
		if name == "outline":
			self.parents.pop()

def cleanPostBody(text):

    offset = 0
    pos = 0
    result_text = ""
    
    buff_open = []
        
    while offset < len(text):
#        tag_opened = re.search("<(?P<tag>[a-zA-Z\-]+)(?P<attr>[^/>]*((\"|')[^>\"]?(\"|'))?[^/>]*)?>", text[offset:])
        tag_opened = re.search("<(?P<tag>[a-zA-Z\-]+)(?P<attr>.*?)>", text[offset:], re.M | re.I | re.S)
#'''<(?P<tag>[a-zA-Z\-])+(?P<attributes>	[^/>]*(("|').*?("|'))?[^/>]*?)>'''"
        tag_closed = re.search("</(?P<tag>[a-zA-Z]+)\s*>", text[offset:], re.M | re.I | re.S)
        
        buff = ""
		
        if tag_opened and tag_closed:
            first_start = min(tag_opened.start(), tag_closed.start())

        if tag_opened and ((not tag_closed) or first_start == tag_opened.start()) :
            start = offset + tag_opened.start()
            pos = offset + tag_opened.end()
            
            tag = tag_opened.group('tag')
            attr = tag_opened.group('attr')

	    if not attr: attr = ""

	    #print tag, attr
			
	    if tag in ["img", "br", "hr"] :
		buff = "<%s%s/>" % (tag, attr)
            elif attr == "/" or attr[-2:] == ' /':
		#print "===== closed tag", tag
                buff = "<%s/>" % tag
	    else:
		buff = "<%s%s>" % (tag, attr)
        	buff_open.append(tag)

        if tag_closed and ((not tag_opened) or first_start == tag_closed.start()) :
            start = offset + tag_closed.start()
            pos = offset + tag_closed.end()
            
            tag = tag_closed.group('tag')
            
            if tag in buff_open:
                buff_open.reverse()
                for i in range(0, buff_open.index(tag) + 1):
                    buff += "</%s>" % buff_open.pop(0)
                buff_open.reverse()
            else:
                buff = ""

	if not tag_closed and not tag_opened:
            start = len(text)
            pos = len(text)
        result_text += text[offset:start] + buff
        offset = pos

    if len(buff_open):
        buff_open.reverse()
        for tag in buff_open:
            result_text += "</%s>" % tag
        
    return result_text



def postToSection(entry):

    #print >> logfile, "DEBUG: Converting post to section."

    post_body_name = ""
    if entry.has_key("title"):
	title = entry["title"].encode('utf8')
    else:
	title = "untitled post".encode('utf8')

    if entry.has_key('content'):
	post_body_name = "content"
	itemblock = entry[post_body_name][0]['value'].encode('utf8')
    elif entry.has_key('summary'):
	post_body_name = "summary"
	itemblock = entry[post_body_name].encode('utf8')
    elif entry.has_key('description'):
	post_body_name = "description"
	itemblock = entry[post_body_name].encode('utf8')
    else:
	return "", {}

    itemblock = cleanPostBody(htmlTagsToFb2Tags(itemblock)) 

    itemblock = "<title><p>%s</p></title><p>%s</p>" % (title, itemblock)

    
    title_hash = md5.new(title).hexdigest()
    images = {}

	
    img_tag_pattern = '<img[^>]*src\s*=\s*("|\')?(?P<url>[^\'">]*)("|\s|\')[^>]*[/]?>'
    if enable_pics:
        while re.search(img_tag_pattern, itemblock, re.M | re.I | re.S) is not None:
	    matchobj = re.search(img_tag_pattern, itemblock, re.M | re.I | re.S)
	    img_url = matchobj.group('url')
            try:
		testing_img_content = urllib.urlopen(img_url).read(3)	# we don't want to leave blank squares as links to non-existed images
		received = 1
	    except IOError:
		# :( cannot connect and get img head for test
		# so we'll believe that this is a good img
		received = 0
	
	    if (received == 1 and testing_img_content[0:3] != "GIF") or received == 0 :
		digest = md5.new(img_url).hexdigest()
		images[digest] = img_url
    		itemblock = itemblock.replace(itemblock[matchobj.start():matchobj.end()], ("<image xlink:href=\"#%s\"/>" % digest))
	    else:
		itemblock = itemblock.replace(itemblock[matchobj.start():matchobj.end()], "[gif image]")
    else:
        img_alttext_pattern = '<img[^>]*?(alt\s*=\s*("|\')?(?P<alt>[^\'">]*)(\'|"|\s)?)[^>]*?[/]?>'
        while re.search(img_alttext_pattern, itemblock, re.M | re.I | re.S) is not None:

	    matchobj = re.search(img_alttext_pattern, itemblock, re.M | re.I | re.S)
            alt = matchobj.group('alt')
	    if alt:
		#print "alt = ", alt
		itemblock = itemblock.replace(itemblock[matchobj.start():matchobj.end()], ("[%s]" % alt))
	    else:
                #print "No alt.",
	    	matchobj = re.search(img_tag_pattern, itemblock, re.M | re.I | re.S)
	    	img_url = matchobj.group('url')
                #print "url =", img_url
		#print matchobj.string
	    	if img_url:
		    itemblock = itemblock.replace(itemblock[matchobj.start():matchobj.end()], ("[%s]" % img_url))
	        else:
		    itemblock = itemblock.replace(itemblock[matchobj.start():matchobj.end()], ("[image]"))

        while re.search(img_tag_pattern, itemblock, re.M | re.I | re.S) is not None:
            matchobj = re.search(img_tag_pattern, itemblock, re.M | re.I | re.S)
            img_url = matchobj.group('url')
            if img_url:
	        itemblock = itemblock.replace(itemblock[matchobj.start():matchobj.end()], ("[%s]" % img_url))
	    else:
	        itemblock = itemblock.replace(itemblock[matchobj.start():matchobj.end()], ("[image]"))

    return itemblock, images


def feedToSection(url):

    print >> logfile, "INFO: Converting feed to section. url =", url

    url = url.rstrip("\n")
    print "\t[", url, "]",
    
    if get_all_posts :
	modified_since = None
    elif not url_last_update.has_key(url):
	modified_since = None
    else :
	modified_since = url_last_update[url]
	
    if not modified_since is None:
	print "\t[since %s]" % time.strftime("%b %d %Y %H:%M:%S", modified_since),
    
    feed = feedparser.parse(url, modified=modified_since)
    if feed.has_key('status') and feed['status'] == 304:
	print " is not modified since last check"
	return None, None, None
    if feed.version == "":
        raise IOError("\tERROR: Cannot connect to the server or unknown feed type at" + url)
    if feed['feed'].has_key('title'):
        feedtitle = feed['feed']['title']
    else :
        feedtitle = "Untitled feed" 
    
    print "\t", feedtitle.encode(sys.stdout.encoding, "ignore")
		
    feedblock = ""
    feed_images = {}
    i = 0
    for entry in feed['entries']:
	if not get_all_posts and not modified_since is None:
	    updated = entry.updated_parsed
	    if updated < modified_since :
		# we assuming that if this post is outdated then next posts are outdated too
		#print "Post is outdated. Breaking out"
		break
	    
	try:
	    post_block, post_images = postToSection(entry)
	except Exception, e:
	    print "ERROR: Error during post processing. Passing by." 
	    print >> logfile, "ERROR: Error with post %d in feed [title = %s, url = %s] %s" % (i, feedtitle, url, e)
	else:
            feedblock += "<section>\n\t" + post_block + "\n</section>\n"
	    for key, value in post_images.items():
		feed_images[key] = value
	i += 1
    print >> logfile, "INFO: %d posts converted" % i
    url_last_update[url] = time.localtime()
    return feedtitle, feedblock, feed_images

def feedsToSections(urls):

    print >> logfile, "INFO: Converting feeds to sections"

    feedsblock = ""
    feeds_images = {}
    i = 0
    for url in urls:
	try:
	    feedtitle, feed, feed_images = feedToSection(url)
	except Exception, e:
	    print
	    print "\t> Error occurred during feed procession. See details in log file"
	    print >> logfile, "ERROR: url =", url, e
	else:
	    if feedtitle is None and feed is None:
		continue
    	    if len(feed) == 0:
		print "\t> Feed is empty. Because of old posts or because of absence of any posts. Passing by"
		print >> logfile, "WARN: Feed is empty. Passing by. url =", url
		continue
	    feedtitle = feedtitle.encode('utf8')
	    feed = unicode(feed, 'utf8').encode('utf8')
    	    feedsblock += "<section>\n\t<title>\n\t\t<p>" + feedtitle + "</p>\n\t</title>\n\t" + feed + "</section>\n"
	    for key, value in feed_images.items():
		feeds_images[key] = value
	i += 1
	
    print >> logfile, "INFO: %d feeds processed in label" % i
		
    return feedsblock, feeds_images

def htmlTagsToFb2Tags(fb2content):
    print >> logfile, "INFO: HTML tags processing. Content to process length =", len(fb2content)
    # hacking around with tags
    # print "Converting HTML tags for feed...",
    
    fb2content = re.sub('<\s*br\s*[/]?>\s*<\s*br\s*[/]?>', '<empty-line/>', fb2content)
    fb2content = re.sub('<\s*br\s*[/]?>', '<empty-line/>', fb2content)
    
    codetag = re.search("<code[^>]*>(?P<code>.*?)</code>", fb2content, re.M | re.I | re.S)
    if codetag :
	code = codetag.group('code')
	code = code.replace('>', '&gt;')
	code = code.replace('<', '&lt;')
	fb2content = fb2content[:codetag.start()] + "<code>" + code + "</code>" + fb2content[codetag.end():]
    
    #fb2content = re.sub('<a(?P<attrs>.*?)>', '<url\g<attrs>>', fb2content) 
    #fb2content = re.sub('</a>', '</url>', fb2content) 
    
    #fb2content = re.sub("<[/]?(code|span|div|b|i|em|strong)[^>]*>", "", fb2content)
    #fb2content = re.sub("<(ol|ul|li|span|b|i|em)[^>]*>", "<p>", fb2content)
    #fb2content = re.sub("</(ol|ul|li|span|b|i|em)>", "</p>", fb2content)

    fb2content = fb2content.replace("&rarr;", "--")
    fb2content = fb2content.replace("&larr;", "--")
    fb2content = fb2content.replace("&mdash;", "-")

    fb2content = fb2content.replace("&quot;", "\"")
    fb2content = fb2content.replace("&nbsp;", " ")
    #fb2content = fb2content.replace("&lt;", "[")
    #fb2content = fb2content.replace("&gt;", "]")	
    fb2content = fb2content.replace("&laquo;", "\"")	
    fb2content = fb2content.replace("&raquo;", "\"")
    fb2content = fb2content.replace("<blockquote>", "<cite><p>")
    fb2content = fb2content.replace("</blockquote>", "</p></cite>")
    fb2content = fb2content.replace("&", "&amp;")
    # print "done"
    return fb2content
    
def imagesToSections(hash_to_url_dic):

    print >> logfile, "INFO: Converting images to sections. URLs to get/convert:", len(hash_to_url_dic)

    content = ""
    for digest, url in hash_to_url_dic.items():
	print "Getting image from", url,
	try:
	    testing_img_content = urllib.urlopen(url).read(3)	# reading 4 first bytes
	    if testing_img_content[0:3] != "GIF":
		img_lines_content = urllib.urlopen(url).readlines()
	    else:
		print "WARN: image skipped because it is in GIF format. FB2 doesn't support GIF"
		print >> logfile, "WARN: GIF image. url =", url
		continue
	except IOError:
	    print "\tERROR: cannot get image content"
	    print >> logfile, "ERROR: cannot get image content at url", url
	else:
	    print
    	    img_content = "".join(img_lines_content)
	    binaryblock = '<binary id="%s">' % digest	    
	    binaryblock += base64.b64encode("".join(img_content))
    	    binaryblock += '</binary>'
	    content += binaryblock
    return content

fb2_header_template="""<?xml version="1.0" encoding="UTF-8"?>
	<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:xlink="http://www.w3.org/1999/xlink">
		<stylesheet xmlns="" type="text/css">
			body {
			    font-family : Verdana, Geneva, Arial, Helvetica, sans-serif;
			}
			p {
			    margin : 0.5em 0 0 0.3em;
			    padding : 0.2em;
			    text-align:justify;
			}
			code {
			    font-family : Courier, Verdana;
			}
			url {
			    text-decoration : underline;
			    font-style: italic;
			}
		</stylesheet>
		<description>
			<title-info>
				<genre>rss_feeds</genre>
				<book-title>%s</book-title>
				<lang>ru</lang>
			</title-info>
		</description>
		<body>"""
fb2_footer = "</body></FictionBook>"

def write_book_file(dirname, filetitle, content, zip_enabled = 1):
    """ Writing book content to file - plain fb2 or zipped fb2"""
    print >> logfile, "INFO: saving book [title = %s" % filetitle,
    filetitle = re.sub('[/\\><~:%*]', '-', filetitle)
    filetitle = filetitle.replace('"', '')
    print >> logfile, ", sanitized = %s]" % filetitle

    filetitle = "%s.%s" % (filetitle, "fb2")
    fullfilename = os.path.join(dirname, filetitle)
    
    if not os.path.exists(dirname):
	print >> logfile, "WARN: target directory %s doesn't exist. creating" % dirname
	try:
	    os.mkdir(dirname)
	except OSError:
	    print >> logfile, "ERROR: cannot create target dir %s ! We'll use current dir as target" % dirname
	    dirname = "."

    filetitle = filetitle.encode(local_enc, "ignore")
    
    if zip_enabled:
        arch = zipfile.ZipFile(fullfilename + ".zip", 'w', zipfile.ZIP_DEFLATED)
	#zinfo = zipfile.ZipInfo(filetitle, time.localtime()[:6])
	arch.writestr(filetitle, content)
	arch.close()
    else:
	file = open(fullfilename, "w")
	file.writelines(content)
	file.close()
    print >> logfile, "INFO: book file saved as %s" % fullfilename

if __name__ == '__main__':
    print "RSS feeds to fb2 converter"
    print
  
    if len(sys.argv) < 2: usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:", ["title=", "enable-pics", "book-per-feed", "disable-zip", "get-all-posts"])
    except getopt.GetoptError, e:
        print e
        usage()

    if len(opts) == 0 or (len(args) < 2 and not ("--book-per-feed") in [first for first, second in opts]): usage()

    enable_pics = 0			# by default image processing is disabled
    enable_book_per_feed = 0    	# by default all feeds placed in one fb2 book
    enable_zip = 1			# by default GZIPping is enabled
    get_all_posts = 0
    for key, value in opts:
        if key == "-t": filetype = value
        if key == "--title": book_title = value
        if key == "--enable-pics": enable_pics = 1
        if key == "--book-per-feed": enable_book_per_feed = 1
        if key == "--disable-zip": enable_zip = 0
        if key == "--get-all-posts": get_all_posts = 1

    input_file = args[0]

    logfile = codecs.open(logfile_name, "w", "utf-8")

    if not os.path.exists(input_file):
        print "There are no such file: %s" % input_file
        usage()

    if (not filetype in ["opml", "text"]):
        print "Wrong option:", filetype
        usage()

    output_dir_name = "."
    if len(args) > 1:
        if enable_book_per_feed: output_dir_name = args[1]
        else: output_file_name = args[1]

    #
    # Looking if there are any timestamps {
    #
    url_last_update = {}
    if os.path.exists(timestampfile_name):
        timestampfile = open(timestampfile_name)
        for line in timestampfile:
	    line = line.rstrip()
  	    row = re.search('^\$(?P<feedurl>[^\$]*)\$\s*=\s*(?P<timestamp>[^\$]*)', line)
	    if row is None: pass
	    else: url_last_update[row.group('feedurl')] = time.strptime(row.group('timestamp'), "%a %b %d %H:%M:%S %Y")
        timestampfile.close()
    else:
        timestampfile = open(timestampfile_name, "w")
    #
    #

    #
    # Parsing input file (OPML or text)
    #
    if (filetype == "opml"):
        parser = xml.sax.make_parser()
        handler = OMPLListHandler()
	parser.setContentHandler(handler)
	parser.parse(input_file)
    elif (filetype == "text"):
	file = open(input_file)
	urls = file.readlines()
	file.close()
    print >> logfile, "INFO: input data type =", filetype
    #
    #
  
    #
    # Specifying book title (or "RSS feeds [01-01-2007]" or custom from my-title)
    #  
    if not enable_book_per_feed:
        default_book_title = "RSS feeds"
        if not vars().has_key('book_title'):
            book_title = default_book_title + ("[%d-%d-%d]" % (time.localtime()[0], time.localtime()[1], time.localtime()[2]))
        else:
	  print >> logfile, "INFO: using custom book title =", book_title
        fb2content = fb2_header_template % book_title
    else:
        books = {}    
    #
    #

    feeds_images = {}

    if (filetype == "opml"):
        handler.labels["Unlabeled"] = handler.freefeeds
        book_images = {}
        for label, urls in handler.labels.items():
            print "processing label \"%s\"" % label
	    if enable_book_per_feed:
                i = 0
	        for url in urls:
                    try:
		        feedtitle, feedbody, feed_images = feedToSection(url)
		    except Exception, e:
		        print "Error occurred during feed procession. See details in log file"
		        print >> logfile, "ERROR: url =", url, "\n", e
		    else:
		        if feedtitle is None and feedbody is None:
		            continue
    		        if len(feedbody) == 0:
	                    print "\t> Feed is empty. Because of old posts or because of absence of any posts. Passing by"
                	    print >> logfile, "WARN: Feed is empty. Passing by. url =", url
                            continue
                        customised_feed_title = "%s - %s" % (label, feedtitle)
                        feedtitle = feedtitle.encode('utf8')
                        label = label.encode('utf8')
                        feedbody = unicode(feedbody, 'utf8').encode('utf8')		
                        books[customised_feed_title] = (fb2_header_template % feedtitle) + feedbody
                        feeds_images[customised_feed_title] = feed_images
                    i += 1
	        print >> logfile, "INFO: %d feeds processed" % i
            else:
                feedsblock, label_images = feedsToSections(urls)
                label = label.encode('utf8')
                feedsblock = unicode(feedsblock, 'utf8').encode('utf8')
                fb2content += "<section><title><p>%s</p></title>%s</section>" % (label, feedsblock)
                book_images = dict(label_images.items())
                #for key, value in label_images.items():
                #    book_images[key] = value
	    
    elif (filetype == "text"):
        if enable_book_per_feed:
            for url in urls:
	        try:
		    feedtitle, feed, feed_images = feedToSection(url)
	        except Exception, e:
		    print "Error occurred during feed procession. See details in log file"
		    print >> logfile, "ERROR: url =", url, "\n", e
	        else:
		    if feedtitle is None and feed is None:
		        continue
    		    if len(feed) == 0:
		        print "\t> Feed is empty. Because of old posts or because of absence of any posts. Passing by"
		        print >> logfile, "WARN: Feed is empty. Passing by. url =", url
		        continue
		    feedtitle_encoded = feedtitle.encode('utf8')
		    feed = unicode(feed, 'utf8').encode('utf8')
		    books[feedtitle] = (fb2_header_template % feedtitle_encoded) + feed
		    feeds_images[feedtitle] = feed_images
        else:
	    feedsblock, book_images = feedsToSections(urls)
            fb2content += feedsblock

#    if not enable_book_per_feed:
#        fb2content = htmlTagsToFb2Tags(fb2content)
#    else:
#        for book_title in books.keys():
#            books[book_title] = htmlTagsToFb2Tags(books[book_title])


    if not enable_book_per_feed:
        fb2content = unicode(fb2content, 'utf8').encode('utf8')
        if enable_pics:    
    	    fb2content += imagesToSections(book_images)
        fb2content += fb2_footer
    elif enable_book_per_feed:
        for book_title, book in books.items():
	    if enable_pics:
	        books[book_title] += imagesToSections(feeds_images[book_title])
	    books[book_title] = unicode(books[book_title], 'utf8').encode('utf8')
	    books[book_title] += fb2_footer

    if enable_book_per_feed:
        for book_title, book in books.items():
	    try:
	        write_book_file(output_dir_name, book_title, book, enable_zip)
	    except Exception, e:
	        print "ERROR: Error when writing file"
	        print >> logfile, "ERROR: Error when writing to file\n", e
	    else:
	        print >> logfile, "INFO: File %s created." % book_title
    else:
        try:
	    write_book_file(output_dir_name, output_file_name, fb2content, enable_zip)
        except Exception, e:
            print "ERROR: Error when writing file"
            print >> logfile, "ERROR: Error when writing to file\n", e
        else:
            print >> logfile, "INFO: File %s created." % output_file_name

    
    timestampfile = open(timestampfile_name, "w")
    for url, timestamp in url_last_update.items():
        timestampfile.write("$%s$ = %s\n" % (url, time.strftime("%a %b %d %H:%M:%S %Y", timestamp)))
    timestampfile.close()

    print >> logfile, "Script finished its work"
    logfile.close()

    print "Done"
