#!/usr/bin/env python


class WriteHtml:
    def __init__(self, filename):
        self.filename = filename
        self.htmlfile = open(filename, 'w')
        self.htmlfile.write("<html>\n\t<head>\n\t\t<title>Title</title>\n\t</head>\n")
        
    def openbody(self):
        self.htmlfile.write("<body>\n")
        
    def closebody(self):
        self.htmlfile.write("\n</body>")
    
    def imagelink(self, filename, width):
        self.htmlfile.write("<a href=\"%s\"><img src=\"%s\" width = %s></a>" % (filename, filename, width))

    def breakline(self):
        self.htmlfile.write("</br>")
        
    def opentable(self):
        self.htmlfile.write("<table>\n")
        
    def closetable(self):
        self.htmlfile.write("\n</table>")
        
    def opentablerow(self):
        self.htmlfile.write("<tr>")
        
    def closetablerow(self):
        self.htmlfile.write("</tr>\n")
        
    def opentablecell(self):
        self.htmlfile.write("<td>")
        
    def closetablecell(self):        
        self.htmlfile.write("</td>")
        
    def writestring(self, mystring):
        self.htmlfile.write("%s" % mystring)
            
    def closehtml(self):
        self.htmlfile.write("\n</html>")
        self.htmlfile.close()
        
