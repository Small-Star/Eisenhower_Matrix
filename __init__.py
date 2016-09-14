#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
#from gtk._gtk import STATE_NORMAL
print pygtk._get_available_versions()
#pygtk.require("2.0")
from gi.repository import Gtk

import json
import datetime
import os
import sys

from settings import *

class EM_GUI:

    def __init__(self):
        self.gladefile = "em_gui.glade" 
        self.glade = Gtk.Builder()
        self.glade.add_from_file(self.gladefile)
        self.glade.connect_signals(self)
        
        self.datafile = DATAFILE
        self.intentions = self.read_from_file(self.datafile)
        self.rows_selected = []
        
        self.fcd_menu = ''
     
        self.lb_q1 = self.glade.get_object("lb_q1")
        self.lb_q2 = self.glade.get_object("lb_q2")
        self.lb_q3 = self.glade.get_object("lb_q3")
        self.lb_q4 = self.glade.get_object("lb_q4")
        
        self.mi_vct = self.glade.get_object("mi_view_completed")
        self.mi_alpha_order = self.glade.get_object("mi_alpha_order")
        print self.mi_alpha_order.get_active()
        #VIEW_COMPLETED =  self.mi_vct.get_active()
                
        self.dlg_add_item = self.glade.get_object("dlg_add_item")
        self.dlg_te_intention = self.glade.get_object("dlg_te_intention")        
        self.dlg_cb_important = self.glade.get_object("dlg_cb_important") 
        self.dlg_te_urgent = self.glade.get_object("dlg_te_urgent") 
        self.fcd = self.glade.get_object("fcd") 
        self.fcd_te = self.glade.get_object("fcd_te")
        
        '''Intentions:
            i[0] = (datetime) Date Created
            i[1] = (bool) Importance
            i[2] = (int) Urgency
            i[3] = (str) Name
            i[4] = (float) Completed Percentage
        '''
        def row_sort(row_1, row_2, data, notify_destroy):
            if self.mi_alpha_order.get_active() == False:
                return row_1.important < row_2.important
            else:
                return row_1.label > row_2.label
        
        for l in [self.lb_q1,self.lb_q2,self.lb_q3,self.lb_q4]:
            l.set_selection_mode(Gtk.SelectionMode.NONE)        
            l.set_sort_func(row_sort, None, False)
        
        self.populate_lbs()
             
    def populate_lbs(self):
        #Clear existing list
        for l in [self.lb_q1,self.lb_q2,self.lb_q3,self.lb_q4]:
            for r in l:
                l.remove(r)
        
        for i in self.intentions:
            if i[4] == 100.0 and self.mi_vct.get_active() == False:
                #Skip intentions marked complete if toggle is active
                continue
            row = Gtk.ListBoxRow()
            row.label = i[3]
            row.important = i[2]
            vbox = Gtk.VBox()
            hbox = Gtk.HBox()
            vbox.pack_start(hbox,False,False,0)
            vbox.set_homogeneous(False)

            cb = Gtk.CheckButton()
            cb.connect("toggled", self.row_cb_toggled)
            cb.label = i[3]
            #hbox.add(cb)
            
            pb = Gtk.ProgressBar()
            pb.set_fraction(i[4]/100)
            hb2 = Gtk.HBox()
            vbox.pack_start(hb2,False,False,5)
            
            spb = Gtk.SpinButton()
            spb.set_adjustment(Gtk.Adjustment(i[4], 0, 100, 5, 0, 0))
            spb.set_numeric(True)
            spb.label = i[3]
            spb.connect("value_changed", self.spb_vc)
            
            hb2.pack_start(spb,False,False,1)
            hb2.pack_start(pb,True,True,10)
            
            
            lb = Gtk.Label(label=str(i[2]) + "     " + i[3], xalign=0.0)
            hbox.pack_start(cb,False,False,5)
            hbox.pack_start(lb,False,False,5)
            #hbox.add(Gtk.Label(label=str(i[2]) + "   " + i[3], xalign=0.0))
            vbspace = Gtk.VBox()
            vbspace.set_spacing(2)
            vbspace.add(Gtk.VBox())
            vbspace.add(vbox)
            vbspace.add(Gtk.VBox())
            row.add(vbspace)
            if i[2] >= 5 and i[1] == True:
                self.lb_q1.add(row)
            if i[2] < 5 and i[1] == True:
                self.lb_q2.add(row)
            if i[2] >= 5 and i[1] == False:
                self.lb_q3.add(row)
            if i[2] < 5 and i[1] == False:
                self.lb_q4.add(row)
        self.glade.get_object("window_main").show_all()
        
    def menu_file_open(self, menuitem, data=None):
        self.fcd.show()
        self.fcd_menu = 'FO'
        response = self.fcd.run()
        print response
 
    def menu_file_new(self, menuitem, data=None):
        self.fcd.show()
        self.fcd_menu = 'FN'
        response = self.fcd.run()
        print response       

    def menu_file_save(self, menuitem, data=None):
         self.write_to_file(items=self.intentions,filename=self.datafile)
        
    def menu_file_saveas(self, menuitem, data=None):
        self.fcd.show()
        self.fcd_menu = 'FSA'
        response = self.fcd.run()
        print response   
                    
    def fcd_btn_ok(self, menuitem, data=None):
        print self.fcd_te.get_text()
        self.datafile = self.fcd_te.get_text()
        #TODO: Validation
        
        if self.fcd_menu == 'FN':
            self.datafile = self.fcd.get_current_folder() + '/' + self.fcd_te.get_text()
            print "creating new file " + self.datafile
            self.write_to_file(items=[],filename=self.datafile)

        if self.fcd_menu == 'FSA':
            self.datafile = self.fcd.get_current_folder() + '/' + self.fcd_te.get_text()
            print "creating new file " + self.datafile
            self.write_to_file(items=self.intentions,filename=self.datafile)
                            
        self.intentions = self.read_from_file(self.datafile)
        self.populate_lbs()
        self.fcd.hide()
        return self.fcd_te.get_text()
    
    def fcd_btn_cancel(self, menuitem, data=None):
        self.fcd.hide()
        print "fcd quit"
                   
    def fcd_fa(self, menuitem, data=None):
        self.fcd_te.set_text(self.fcd.get_filename())
    
    def row_cb_toggled(self, object, data=None):
        if object.get_active() == True:
            print object.label
            self.rows_selected.append(object.label)
        else:
            print "non"
            if object.label in self.rows_selected:
                self.rows_selected.remove(object.label)
                
        #print self.rows_selected
        
    def spb_vc(self, object, data=None):
        print object.get_value()

        for i in self.intentions:
            if object.label == i[3]:
                i[4] = object.get_value()

        self.write_to_file(items=self.intentions,filename=self.datafile)
        self.populate_lbs()       
    
    def window_destroy(self, object, data=None):
        Gtk.main_quit()
        
    def menu_quit(self, object, data=None):
        print "menu quit"
        Gtk.main_quit()
        
    def dlg_quit(self, object, data=None):
        self.dlg_add_item.destroy()
        print "dlg quit"

    def mi_view_completed_toggle(self, object, data=None):
        print "menu vc toggled"
        #self.view_completed = object.get_active()
        #print self.mi_vct.get_active()
        self.populate_lbs() 
        
    def mi_alpha_order_toggle(self, object, data=None):
        print "menu alpha order toggled"
        self.populate_lbs() 
                
    def menu_add_item(self, object, data=None):
        print "menu add"
        #self.dlg_add_item = self.glade.get_object("dlg_add_item") 
        self.response = self.dlg_add_item.run()
        self.dlg_add_item.hide()
                
    def menu_comp_item(self, object, data=None):
        print "menu comp"
        print self.rows_selected
        
        for row in self.rows_selected:
            for i in self.intentions:
                if row == i[3]:
                    i[4] = 100.0
        self.write_to_file(items=self.intentions,filename=self.datafile)
        self.populate_lbs()       
        #print self.lb_q1.get_selector()
        
    def menu_del_item(self, object, data=None):
        print "menu del"
        print self.rows_selected
        
        for row in self.rows_selected:
            for i in self.intentions:
                if row == i[3]:
                    self.intentions.remove(i)
                    
        self.rows_selected = []
        self.write_to_file(items=self.intentions,filename=self.datafile)
        self.populate_lbs()       
        
    def add_intention(self, object, data=None):
        if self.dlg_te_intention.get_text() == '' or self.dlg_te_urgent.get_text() == '':# or int(self.dlg_te_urgent.get_text()) > 9 or int(self.dlg_te_urgent.get_text()) < 1:
            #input is not OK
            print "Error: Input is not correct"
            self.dlg_quit(self,None)

        else:
            print self.dlg_te_intention.get_text()
            print self.dlg_cb_important.get_active()
            print self.dlg_te_urgent.get_text()
            new_intention = [str(datetime.date.today()),self.dlg_cb_important.get_active(),int(self.dlg_te_urgent.get_text()),self.dlg_te_intention.get_text(),False]
            self.intentions.append(new_intention)
            self.write_to_file(items=self.intentions,filename=self.datafile)
            self.populate_lbs()
                
    def read_from_file(self,filename=DATAFILE):
        print type(filename)
        print "reading from " + filename
        try:
            with open(filename, 'r') as infile:
                t = json.load(infile)
                print len(t)
                return t
        except IOError:
            print "Error: Input file error"
                    
    def write_to_file(self,items,filename=DATAFILE):
        print "writing to " + filename
        try:
            with open(filename, 'w') as outfile:
                json.dump(items, outfile)
        except IOError:
            print "Error: Output file error"
                
class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, data):
        super(Gtk.ListBoxRow, self).__init__()
        self.data = data
        self.add(Gtk.Label(data))
        
if __name__ == "__main__":
    try:
        inst = EM_GUI()
        Gtk.main()
    except KeyboardInterrupt:
        pass