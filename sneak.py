#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import irc
import HTMLParser
import time
import re
from urllib import urlopen, quote
from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class titlefinder(HTMLParser):
    #self.start_title=0
    #self.title = ''
    #self.stop_title=0    
    def __init__(self):        
        HTMLParser.__init__(self) # http://stackoverflow.com/a/9698750
        self.start_title=0
        self.title = ''
        self.stop_title=0
        
    def get_title(self):
        return self.title
    def handle_starttag(self, tag, attrs):
        if tag == 'title': self.start_title = 1
    def handle_endtag(self, tag):
        if tag == 'title': self.stop_title = 1
    def handle_data(self, data):
        if (self.start_title and not self.stop_title):
            self.title += data

def handle_url(url, chan):
    response = urlopen(str(url))
    rep_code = response.code    #response code    
    if rep_code == 200:
        # Was a great succes!
        # zoek title
        html = unicode(response.read(), 'utf-8') # thanks to <MinceR> from #Corsair on OFTC
        find_title = titlefinder()
        find_title.feed(html)
        title =  find_title.get_title()
        MyConn.send_string("PRIVMSG %s :%s" % (chan, title))
            
def handle_raw(line):
    print line

# Define event listeners.
def handle_state(newstate):
    if newstate==4:
        MyConn.send_string("JOIN %s" % channel)

def handle_parsed(prefix, command, params):
    if command=="PRIVMSG":
        channel = params[0]
        line = params[1]
        if channel == "sneak" and line == "!stop" and prefix.split('!')[0] == "Sir_Ragnarok":
            sys.exit() # exit on command
        
        if channel == 'sneak': channel = prefix.split('!')[0]
        # find all urls
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
        for url in urls:
            handle_url(url, channel)

# Connect as usual.
MyIRC=irc.IRC_Object( )
MyConn=MyIRC.new_connection( )
MyConn.nick="sneak"
MyConn.ident="snpeak"
MyConn.server=("irc.chat.be", 6667)
MyConn.realname="Title Anouncer"
channel="#chathere"
quit_reason="Bye Bye was a fun time."

# Before starting the main loop, add the event listeners.
MyConn.events['state'].add_listener(handle_state)
MyConn.events['raw'].add_listener(handle_raw)
MyConn.events['parsed'].add_listener(handle_parsed)

while 1:
    MyIRC.main_loop()
