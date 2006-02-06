#!/usr/bin/env python

import sys, os
import gnome
import pygtk
pygtk.require('2.0')

import gtk, gtk.glade

APPNAME="DND2TxtApp"
APPVERSION="0.1"

def find_glade(base):
	"""Finds a glade file by searching the sys.path. If we can't find the
	file, returns the current directory
	"""
	for dir in sys.path:
		path = os.path.join(dir, base)
		if os.path.isfile(path):
			return path
	return "."

class DND2TxtApp:
	def __init__(self):
		xml = gtk.glade.XML(find_glade('dnd-out.glade'))
		xml.signal_autoconnect(self)
		self.drop_widget = xml.get_widget('dropoff_text_widget')
		self.drop_buffer = self.drop_widget.get_buffer()
		self.drop_text = ""
		#self.drop_widget.drag_dest_set(gtk.DEST_DEFAULT_ALL, [], gtk.gdk.ACTION_COPY)
		#self.drop_widget.drag_dest_add_text_targets()
		#self.drop_widget.drag_dest_add_uri_targets()

	def on_button1_clicked(self, button):
		print self.drop_text
		sys.stdout.flush()

	def gtk_main_quit(self, *args):
		gtk.main_quit()
	on_quit1_activate = gtk_main_quit

	
	def on_drag_data_received(self, widget, dragctx, x_loc, y_loc, selection, info, timestamp):
		self.drop_text = selection.get_text().rstrip('\n\r')
		self.drop_buffer.set_text(self.drop_text)
		print self.drop_text
		sys.stdout.flush()
		
		#print "drag_data_received: dir", selection, dir(selection)
		#print "drag_data_received: data", selection.data
		#print "drag_data_received: type", selection.type
		#  'copy', 'data', 'format', 'get_pixbuf', 'get_targets', 'get_text', 'get_uris', 'selection', 'set', 'set_pixbuf', 'set_text', 'set_uris', 'target', 'tree_get_row_drag_data', 'tree_set_row_drag_data', 'type'


if __name__ == '__main__':
        prog = gnome.init(APPNAME, APPVERSION)
	# gnome.gnome_program_init
	test = DND2TxtApp()
	gtk.main()
