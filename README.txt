
Usage:
  flashplayer [OPTS] file.swf

OPTS:
  --hide-menubar                  Start without displaying the menubar, and display the inner close-button
  --hide-button                   Start without displaying the inner close-button
  --screenshot-file file.png      Filename pattern for screenshot images (the main window will display and auto exit)
  -j arg                          Set window width
  -k arg                          Set window height
  -X arg -Y arg                   Set window position

Examples:
  flashplayer file.swf
  flashplayer -hide-menubar file.swf
  flashplayer -hide-menubar --hide-button file.swf
  flashplayer -hide-menubar -j500 -k400 file.swf
  flashplayer -hide-menubar -j500 -k400 -X200 -Y300 file.swf

Usage of flash-thumbnailer (whihout displaying the main window):
  flash-thumbnailer [OPTS] --screenshot-file file.png file.swf

License:
  GPL 3.0, https://www.gnu.org/licenses/gpl-3.0.html
