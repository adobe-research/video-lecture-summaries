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
        self.htmlfile.write(self.relpath("mystyle.css"))
        self.htmlfile.write("\" rel=\"stylesheet\" />\n")
        self.htmlfile.write("<title>"+title+"</title>\n")
        self.htmlfile.write("</head>\n")
        self.openbody()
        
    def openbody(self):
        self.htmlfile.write("<body>\n")
        
    def closebody(self):
        self.htmlfile.write("\n</body>")
    
    def imagelink(self, filename, width):
        self.htmlfile.write("<a href= \"" + self.relpath(filename) + "\">")
        self.htmlfile.write("<img src=\"" + self.relpath(filename) + "\" max-width =" + width + ">")
        self.htmlfile.write("</a>")

    def image(self, filename, width="", mapname=""):
        self.htmlfile.write("<img src= \"%s\" max-width=\"%s\" usemap=\"#%s\" >\n" % (self.relpath(filename), width, mapname))
        
    def breakline(self):
        self.htmlfile.write("</br>")
        
    def opentable(self, border=0):
        self.htmlfile.write("<table border="+str(border)+">\n")
        
    def closetable(self):
        self.htmlfile.write("\n</table>\n")
        
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
        self.htmlfile.write("</td>\n")

    def opendiv(self, idstring="", class_string=""):
        self.htmlfile.write("<div id=\"%s\" class=\"%s\">" % (idstring, class_string)) 
        
    def closediv(self):
        self.htmlfile.write("</div>\n")
        
    def writestring(self, mystring):
        self.htmlfile.write("%s" % mystring)
            
    def closehtml(self):
        self.closebody()
        self.htmlfile.write("\n</html>")
        self.htmlfile.close()
    
    def paragraph(self, list_of_words):
        self.htmlfile.write("<p>")
        for word in list_of_words:
            if not word.issilent:
                self.htmlfile.write(word.original_word + " ")
        self.htmlfile.write("</p>")
        
    def map(self, mapname, list_of_areas, list_item_names):
        self.htmlfile.write("<map name = \"%s\">\n" % mapname)
        area_id = 0
        for area in list_of_areas:
            item_name = list_item_names[area_id]
            self.htmlfile.write("<area shape = \"rect\" coords= \"%i, %i, %i, %i\" item=\"%s\" href=\"#\" \>\n" % (area[0], area[1], area[2], area[3], item_name))
            area_id += 1
        self.htmlfile.write("</map>\n")
        
        
    def highlighted_script(self, list_of_words):
        self.htmlfile.write("<p>")
        for word in list_of_words:
            if word.issilent:
                continue
            elif word.highlight_path != None:
                #self.htmlfile.write("<a  class=\"highlight\" href=\"#\"  onmouseover=\"document.getElementById(''mainpic').src='"+ self.relpath(word.highlight_path) + "'\"")
                #self.htmlfile.write(" onmouseout=\"document.getElementById('mainpic').src='mainpic.png'\">")
                self.htmlfile.write("<a class=\"highlight\" href=\"#\"> <img src = " + word.highlight_path + "  >")
                self.htmlfile.write(word.original_word + " ")
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
            self.htmlfile.write("keyframe new visual:" + str(lecseg.keyframe.new_visual_score()) +"<br>" )            
            self.htmlfile.write("</p>")
        self.htmlfile.write("</td></tr></table>")
        self.htmlfile.write("</div>")