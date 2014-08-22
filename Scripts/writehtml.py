#!/usr/bin/env python

import os
import datetime

class WriteHtml:
    def __init__(self, filename, title="no title"):
        self.filename = os.path.abspath(filename)
        self.htmlfile = open(filename, 'w')
        self.htmlfile.write("<html>\n")
        self.htmlfile.write("<head>\n")
        self.htmlfile.write("<link href=\"" )
        self.htmlfile.write(self.relpath("C:/Users/vshin/Desktop/video-lecture-summaries/Mainpage/mystyle.css"))
        self.htmlfile.write("\" rel=\"stylesheet\" />\n")
        self.htmlfile.write("<title>"+title+"</title>\n")
        self.htmlfile.write("</head>\n")
        
    def openbody(self):
        self.htmlfile.write("<body>\n")
        
    def closebody(self):
        self.htmlfile.write("\n</body>")
    
    def imagelink(self, filename, width):
        self.htmlfile.write("<a href=\"%s\"><img src=\"%s\" height = %s></a>" % (filename, filename, width))

    def breakline(self):
        self.htmlfile.write("</br>")
        
    def opentable(self, border=0):
        self.htmlfile.write("<table border="+str(border)+">\n")
        
    def closetable(self):
        self.htmlfile.write("\n</table>")
        
    def opentablerow(self):
        self.htmlfile.write("<tr>")
        
    def closetablerow(self):
        self.htmlfile.write("</tr>\n\n")
        
    def opentablecell(self):
        self.htmlfile.write("<td>")
        
    def cellstring(self, mystring):
        self.opentablecell()
        self.writestring(mystring)
        self.closetablecell()
        
    def cellimagelink(self, filename, width):
        self.opentablecell()
        self.imagelink(filename, width)
        self.closetablecell()    
        
    def closetablecell(self):        
        self.htmlfile.write("</td>")
        
    def writestring(self, mystring):
        self.htmlfile.write("%s" % mystring)
            
    def closehtml(self):
        self.htmlfile.write("\n</html>")
        self.htmlfile.close()
    
    def paragraph(self, list_of_words):
        self.htmlfile.write("<p>")
        for word in list_of_words:
            self.htmlfile.write(word + " ")
        self.htmlfile.write("</p>")
        
    def highlighted_script(self, list_of_words):
        self.htmlfile.write("<p>")
        for word in list_of_words:
            if word.issilent:
                continue
            elif word.highlight_path != None:
                self.htmlfile.write("<a href=\"#\">" + word.original_word + " <img src = \"" + self.relpath(word.highlight_path) + "\">")                
                self.htmlfile.write("</a>")
            else:
                self.htmlfile.write(word.original_word + " ")            
        self.htmlfile.write("</p>")
    
    def relpath(self, path):
        relpath = os.path.relpath(path, __file__)
        return relpath      
    
    
    def lectureseg(self, lecseg, debug=False):
        self.htmlfile.write("<div>\n")
        self.htmlfile.write("<table><tr>")
        self.htmlfile.write("<td><img src=" + self.relpath(lecseg.keyframe.frame_path)+" /></td>\n")        
        self.htmlfile.write("<td>")
        self.htmlfile.write("<h1>" + lecseg.title + "</h1>\n")
        self.highlighted_script(lecseg.list_of_words)
        if (debug):
            self.htmlfile.write("<p class=\"debug\">")
            self.htmlfile.write("start time:" + str(datetime.timedelta(milliseconds=lecseg.startt)) + "<br>")
            self.htmlfile.write("end time: "  + str(datetime.timedelta(milliseconds= lecseg.endt)) +"<br>")
            self.htmlfile.write("num sentences: " + str(lecseg.num_stcs()) +"<br>" )            
            self.htmlfile.write("num words: " + str(len(lecseg.list_of_words)) +"<br>" )
            self.htmlfile.write("num nonsilent words: " + str(lecseg.num_nonsilent_words()) +"<br>" )
            self.htmlfile.write("keyframe new visual:" + str(lecseg.keyframe.new_visual()) +"<br>" )            
            self.htmlfile.write("</p>")
        self.htmlfile.write("</td></tr></table>")
        self.htmlfile.write("</div>")