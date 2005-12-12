"""
   Progress bar (TTY version)

   Written by BroytMann, Jan 1997. Copyright (C) 1997 PhiloSoft Design
"""


import sys, os, string

import time

class ttyProgressBar:
   """
      Simple progress indicator - displays bar "graph" using standard tty
      commands - Space, Backspace, etc. This method is compatible with
      (almost) all UNIX consoles and DOS box.

      Example:

         ====------  42%

      This displays "bar" (width 10 char) for 42%

      Certainly, to use it nicely, do not write anything on screen
      (to stdout or stderr), while using it (or use erase()/redraw() procs).
      Erase or delete it after using.
   """

   left_c = '#'     # Chars for "graphics"
   right_c = '_'
   space_c = ' '    # Space
   back_c = chr(8)  # Backspace
   progress_chars = ('|', '/', '-', '\\') 
                                                                      # 1 space + 3 chars for "100" + 1 for "%"
   def __init__(self, min, max, out = sys.stderr, width1 = 10, width2 = 1+3+1, do_progress=1):
      self.min = min
      self.current = min
      self.max = max - min
      self.do_progress = do_progress

      self.width1 = width1
      if self.do_progress:
      	width2 += 2
      self.width2 = width2
      self.out = out

      self.redraw()


   def __del__(self):
      self.erase()


   def display(self, current):
	"""
	 Draw current value on indicator.
	 Optimized to draw as little as possible.
	"""

	self.current = current
	current = current - self.min
	lng = (current*self.width1) / self.max

	if current >= self.max:
		percent = 100
	else:
		percent = (current*100) / self.max

	flush = 0

	if self.lng <> lng:
		self.lng =  lng
		self.out.write(ttyProgressBar.back_c*(self.width1+self.width2))
		self.out.write(ttyProgressBar.left_c*lng)
		self.out.write(ttyProgressBar.right_c*(self.width1-lng) + ttyProgressBar.space_c)
		flush = 1
		self.percent = -1	 # force a percentage redraw

	elif self.percent <> percent:
		self.out.write(ttyProgressBar.back_c*(self.width2-1))
		flush = 1
	
	elif self.do_progress is not None:
		self.out.write(ttyProgressBar.back_c*2)
		flush = 1


	if self.percent <> percent:
		self.percent =  percent
		self.out.write("%3d%%" % percent)
		# self.out.write(string.rjust(`percent`, 3) + '%')
		flush = 1

	if self.do_progress is not None:
		self.out.write(" " + self.progress_chars[self.do_progress])
		self.do_progress = (self.do_progress + 1) % len(self.progress_chars)

	if flush:
		self.out.flush()

	self.visible = 1


   def erase(self):
      if self.visible: # Prevent erase() to be called twice - explicitly and from __del__()
         self.out.write(ttyProgressBar.back_c*(self.width1+self.width2))
         self.out.write(ttyProgressBar.space_c*(self.width1+self.width2))
         self.out.write(ttyProgressBar.back_c*(self.width1+self.width2))
         self.out.flush()
         self.visible = 0


   def redraw(self):
      self.lng = -1 # To force self.display draw bar on 1st call
      self.percent = -1

      self.out.write(ttyProgressBar.space_c*(self.width1+self.width2))
      self.display(self.current)


if os.name == 'dos' or os.name == 'nt' : # Use nice chars on DOS screen
   ttyProgressBar.left_c = chr(178)
   ttyProgressBar.right_c = chr(176)
