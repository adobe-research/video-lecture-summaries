#!/usr/bin/env python

import os
import datetime
from figure import Figure
import cv2
from nltk.corpus import stopwords
from process_aligned_json import Word

def htmlword(str):
    str = str.replace(">", "&gt")
    str = str.replace("<", "&lt")
    return str

class WriteHtml:
    def __init__(self, filename, title="no title", stylesheet=None, script=False):
        self.filename = os.path.abspath(filename)
        self.filedir = os.path.dirname(self.filename)
        self.htmlfile = open(filename, 'w')
        self.numfigs = 0
        self.htmlfile.write("<html>\n")
        self.htmlfile.write("\t<head>\n")
        self.htmlfile.write("\t<script src=\"http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js\"></script>\n")
        if stylesheet is not None:
            self.htmlfile.write("\t<link href=\"" )
#             stylesheet = os.path.abspath(stylesheet)
#             self.htmlfile.write(os.path.relpath(stylesheet, self.filedir))
            self.htmlfile.write(stylesheet)
            self.htmlfile.write("\" rel=\"stylesheet\" />\n")
        self.htmlfile.write("\t<title>"+title+"</title>\n")
        if not script:
            self.openbody()
        
    def openbody(self):
        self.htmlfile.write("</head>\n")
        self.htmlfile.write("<body>\n")
        
    def closebody(self):
        self.htmlfile.write("\n</body>")
    
    def imagelink(self, filename, width):
        self.htmlfile.write("<a href= \"" + self.relpath(filename) + "\">")
        self.image(filename, width=width)
        self.htmlfile.write("</a>")

    def figure(self, filename, width="", mapname="", idstring="", classstring="", caption=""):
        self.htmlfile.write("<figure>\n")
        self.image(filename, width, mapname, idstring, classstring)
        if caption is not "":
            self.htmlfile.write("<figcaption> " + caption + " </figcaption>\n")
        self.htmlfile.write("</figure>\n")
#         self.breakline()
        self.numfigs += 1

    def image(self, filename, width="", height="", mapname="", idstring="", class_string=""):
        self.htmlfile.write("<img src= \"%s\" width=\"%s\" height=\"%s\" usemap=\"#%s\" id=\"%s\" class=\"%s\">\n" % (self.relpath(filename), width, height, mapname, idstring, class_string))

    def breakline(self):
        self.htmlfile.write("</br>\n")
        
    def opentable(self, border=0):
        self.htmlfile.write("<table border="+str(border)+">\n")
        
    def closetable(self):
        self.htmlfile.write("\n</table>\n")
        
    def opentablerow(self):
        self.htmlfile.write("<tr>")
        
    def closetablerow(self):
        self.htmlfile.write("</tr>\n\n")
        
    def openp(self):
        self.htmlfile.write("<p>")
    
    def closep(self):
        self.htmlfile.write("</p>")
        
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

    def opendiv(self, idstring="", class_string="", width=""):
        self.htmlfile.write("<div id=\"%s\" class=\"%s\" width=\"%s\">\n" % (idstring, class_string, width)) 
        
    def closediv(self):
        self.htmlfile.write("</div>\n")
        
    def openscript(self):
        self.htmlfile.write("<script>\n")
    
    def closescript(self):
        self.htmlfile.write("</script>\n")
        
    def writestring(self, mystring):
        self.htmlfile.write("%s" % mystring)
            
    def closehtml(self):
        self.closebody()
        self.htmlfile.write("\n</html>")
        self.htmlfile.close()
        
    def write_sentence(self, sentence, stopwords = []):
        nref = len(sentence.ref_words)
        for i in range(0, nref):
            word = sentence.ref_words[i]
            id = sentence.list_of_words.index(word)
            name = sentence.ref_names[i]
            nameword = Word(name, "", -1, -1, -1, "")
            nameword.islabel = True
            sentence.list_of_words.insert(id+1, nameword)
        self.write_list_of_words(sentence.list_of_words, stopwords)
    
    def paragraph_list_of_words(self, list_of_words, stopwords=[]):
        self.htmlfile.write("<p>\n")
        self.write_list_of_words(list_of_words, stopwords)
        self.htmlfile.write("\n</p>")
        
    def write_list_of_words(self, list_of_words, stopwords=[]):
        for word in list_of_words:
            if not word.issilent:
                if word.raw_word in stopwords:
                    self.htmlfile.write("<font color=\'red\'>")
                    self.htmlfile.write(htmlword(word.original_word) + " ")
                    self.htmlfile.write("</font>")
                elif word.islabel:
                    self.htmlfile.write("<b>")
                    self.htmlfile.write(htmlword(word.original_word) + " ")
                    self.htmlfile.write("</b>")
                else:    
                    self.htmlfile.write(htmlword(word.original_word) + " ")
                    

        
    
    def pragraph_string(self, mystring):
        self.htmlfile.write("<p>\n")
        self.writestring(mystring)
        self.htmlfile.write("\n</p>\n")
        
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
                self.htmlfile.write(htmlword(word.original_word) + " ")
                self.htmlfile.write("</a>")
            else:
                self.htmlfile.write(htmlword(word.original_word) + " ")            
        self.htmlfile.write("</p>")
    
    def relpath(self, path):
        relpath = os.path.relpath(path, self.filedir)
        return relpath      
    
    def obj_script(self, list_of_objs, figure_idx, lec):
        stc_idx = 0
        nfig = 0
        obj_idx = 0
        for obj_idx in range(0, len(list_of_objs)):
            obj = list_of_objs[obj_idx]
            t = lec.video.fid2ms(obj.end_fid)
            paragraph = []
            while(lec.list_of_stcs[stc_idx][-1].endt < t):
                """get sentence that ends before figure ends"""
                paragraph = paragraph + lec.list_of_stcs[stc_idx]
                stc_idx += 1
                if (stc_idx >= len(lec.list_of_stcs)):
                    break
            self.paragraph_list_of_words(paragraph)
            self.figure(list_of_objs[obj_idx].imgpath, "Figure %i" % figure_idx[nfig])
            nfig += 1    
            
            
    def figure_script_v1(self, list_of_figures, lec):
        stc_id = 0
        figure_id = 0
        for figure_id in range(0, len(list_of_figures)):
            fig = list_of_figures[figure_id]
            figure_startt = lec.video.fid2ms(fig.start_fid)
            paragraph_stc_ids = []
            while(lec.list_of_stcs[stc_id][-1].endt < figure_startt):
                """get sentence that ends before a figure starts"""
                paragraph_stc_ids.append(stc_id)
                stc_id += 1
                if (stc_id >= len(lec.list_of_stcs)):
                    break
            
            self.stcs_with_figure_v1(lec, paragraph_stc_ids)
            """highlight new part of figure"""
            self.figure(fig.highlight_new_objs().imgpath, idstring="fig%i"%(figure_id), caption="Figure %i-%i" % (fig.main_id, fig.sub_id))
        
        paragraph_stc_ids = []
        while(stc_id < len(lec.list_of_stcs)):
            paragraph_stc_ids.append(stc_id)
            stc_id += 1
        if (len(paragraph_stc_ids) > 0):
            self.stcs_with_figure_v1(lec, paragraph_stc_ids)
            
    def stcs_with_figure_v1(self, lec, stc_ids):
        self.writestring("<p>")
        for i in range(0, len(stc_ids)):
            stc_id = stc_ids[i]
            stc = lec.list_of_stcs[stc_id]
            figid = lec.best_fig_ids[stc_id]
            print 'figid =', figid
            if (figid >= 0):
                stc_start_fid = lec.video.ms2fid(stc[0].startt)
                stc_end_fid = lec.video.ms2fid(stc[-1].endt)
                stc_figobj = lec.list_of_figs[figid].highlight_time(stc_start_fid, stc_end_fid)
                figpath = self.relpath(stc_figobj.imgpath)
                self.writestring("<a href=\"#\" ")
                self.writestring("onmouseover=\"document.getElementById(\'fig%i\').src=\'%s'\">" %(figid, figpath))
                self.write_list_of_words(lec.list_of_stcs[stc_id])
                self.writestring("</a>&nbsp;&nbsp;")
            else:
                self.write_list_of_words(lec.list_of_stcs[stc_id])
        self.writestring("</p>")
            
    def figure_script(self, summary):
        stc_id = 0
        figure_id = 0
        list_of_figures = summary.list_of_figures
        lec = summary.lec
        
        for figure_id in range(0, len(list_of_figures)):
            fig = list_of_figures[figure_id]
            figure_startt = lec.video.fid2ms(fig.start_fid)
            figure_endt = lec.video.fid2ms(fig.end_fid)
            paragraph_stc_ids = []
            while(lec.list_of_stcs[stc_id][-1].endt < figure_startt):
                """get sentence that ends before a figure starts"""
                paragraph_stc_ids.append(stc_id)
                stc_id += 1
                if (stc_id >= len(lec.list_of_stcs)):
                    break
            
            self.stcs_with_figure(summary, paragraph_stc_ids)
            """highlight new part of figure"""
            self.figure(fig.newobjpath, idstring="fig%i"%(figure_id), caption="Figure %i(%s)" % (fig.main_id, chr(fig.sub_id + ord('a'))))
        
        paragraph_stc_ids = []
        while(stc_id < len(lec.list_of_stcs)):
            paragraph_stc_ids.append(stc_id)
            stc_id += 1
        if (len(paragraph_stc_ids) > 0):
            self.stcs_with_figure(summary, paragraph_stc_ids)
            
    def stcs_with_figure(self, summary, stc_ids):
        self.writestring("<p>")
        for i in range(0, len(stc_ids)):
            stc_id = stc_ids[i]
            Stc = summary.list_of_Stcs[stc_id]
            figid = summary.stc_fig_ids[stc_id]
            if (figid >= 0 and Stc.visobj is not None):
                stc_figobj = Stc.visobj
                fig_startt = summary.lec.video.fid2ms(stc_figobj.start_fid)
                fig_endt = summary.lec.video.fid2ms(stc_figobj.end_fid)
                mouseon_figpath = self.relpath(stc_figobj.imgpath)
                mouseout_figpath = self.relpath(summary.list_of_figures[figid].newobjpath)
#                 self.writestring("<a href=\"#\" ")
#                 self.writestring("onmouseover=\"document.getElementById(\'fig%i\').src=\'%s'\" " %(figid, mouseon_figpath))
#                 self.writestring("onmouseout=\"document.getElementById(\'fig%i\').src=\'%s'\" >" %(figid, mouseout_figpath))
                self.write_list_of_words(Stc.list_of_words)
#                 self.writestring("(%i ms, %i ms) (%i ms %i ms)" %(Stc.list_of_words[0].startt, Stc.list_of_words[-1].endt, fig_startt, fig_endt))
#                 self.writestring("</a>&nbsp;&nbsp;")
            else:
                self.write_list_of_words(Stc.list_of_words)
#                 self.writestring("(%i ms, %i ms) " %(Stc.list_of_words[0].startt, Stc.list_of_words[-1].endt))
        self.writestring("</p>")

            

                        
        
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