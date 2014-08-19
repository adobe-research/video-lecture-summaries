#!/usr/bin/env python

class WriteHtml:
    def __init__(self, filename, title="no title"):
        self.filename = filename
        self.htmlfile = open(filename, 'w')
        self.htmlfile.write("<html>\n")
        self.htmlfile.write("<head>\n")
        self.htmlfile.write("<link href=\"C:/Users/vshin/Desktop/video-lecture-summaries/Mainpage/mystyle.css\" rel=\"stylesheet\" />\n")
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
        self.htmlfile.write("</tr>\n")
        
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
                self.htmlfile.write("<a href=" + word.highlight_path + ">")
                self.htmlfile.write(word.original_word + " ")
                self.htmlfile.write("</a>")
            else:
                self.htmlfile.write(word.original_word + " ")            
        self.htmlfile.write("</p>")            
    
    def lectureseg(self, lecseg):
        self.htmlfile.write("<div>\n")
        self.htmlfile.write("<img src=" + lecseg.keyframe.frame_path+" />\n")
        self.htmlfile.write("<h1>" + lecseg.title + "</h1>\n")
        words = []
        for word in lecseg.list_of_words:
            if not word.issilent:
                words.append(word.original_word)
        self.paragraph(words)
        self.htmlfile.write("</div>")