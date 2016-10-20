Depends:
  sudo apt-get install python-gtk2 python-webkit
  sudo apt-get install libflashplugin #(or flashplugin-nonfree)
Depends for flash-thumbnailer:
  sudo apt-get install xvfb

Usage:
  flashplayer [OPTS] file.swf
  Or:
  flashplayer.py [OPTS] file.swf

OPTS:
  --hide-menubar                      Start without displaying the menubar
                                      and display the inner close-button
  --window-type <toplevel/popup>      Set main window type, toplevel or popup
  --hide-button                       Hide the inner close-button
  --screenshot-file file.png          Filename pattern for screenshot images
                                      the main window will display and auto exit
  -j arg                              Set window width
  -k arg                              Set window height
  -X arg -Y arg                       Set window position

Examples:
  flashplayer file.swf
  flashplayer --hide-menubar file.swf
  flashplayer --hide-menubar --hide-button file.swf
  flashplayer --hide-menubar -j500 -k400 file.swf
  flashplayer --window-type=popup -j500 -k400 -X200 -Y300 file.swf

Usage of flash-thumbnailer:
  flash-thumbnailer [OPTS] --screenshot-file file.png file.swf

Compile (Optional):
  sudo apt-get install make gcc cython python-dev
  cd flashplayer-pygtk
  make

License:
  GPL 3.0, https://www.gnu.org/licenses/gpl-3.0.html
