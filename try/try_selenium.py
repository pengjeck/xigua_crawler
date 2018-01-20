# coding: utf-8


from selenium import webdriver

w = webdriver.PhantomJS()
w.get('http://m.ixigua.com/?channel=video_new#channel=video_new')
print(w.get_cookies())