#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

# author: nanpuyue <nanpuyue@gmail.com>, https://blog.nanpuyue.com
# license: GPL 3.0, https://www.gnu.org/licenses/gpl-3.0.html
# thanks: Kai Lautaportti, https://pypi.python.org/pypi/hexagonit.swfheader/1.2

import pygtk; pygtk.require('2.0')
import gtk, webkit, urllib, sys, getopt, os.path, zlib, struct

try:
	opts,args = getopt.getopt(sys.argv[1:], "X:Y:j:k:", ["hide-menubar", "hide-button", "window-type=", "screenshot-file="])
except getopt.GetoptError:
	print("getopt error!")
	sys.exit(1)

def swfheader(input):
	header = {}
	need_close = False

	if hasattr(input, 'read'):
		input.seek(0)
	else:
		input = open(input, 'rb')
		need_close = True

	def read_ui8(c):
		return struct.unpack('<B', c)[0]
	def read_ui16(c):
		return struct.unpack('<H', c)[0]
	def read_ui32(c):
		return struct.unpack('<I', c)[0]

	signature = ''.join(struct.unpack('<3c', input.read(3)))
	if signature not in ('FWS', 'CWS'):
		raise ValueError('Invalid SWF signature: %s' % signature)

	header['compressed'] = signature.startswith('C')
	header['version'] = read_ui8(input.read(1))
	header['size'] = read_ui32(input.read(4))

	buffer = input.read(header['size'])
	if header['compressed']:
		buffer = zlib.decompress(buffer)
	nbits = read_ui8(buffer[0]) >> 3
	current_byte, buffer = read_ui8(buffer[0]), buffer[1:]
	bit_cursor = 5

	for item in 'xmin', 'xmax', 'ymin', 'ymax':
		value = 0
		for value_bit in range(nbits - 1, -1, -1):
			if (current_byte << bit_cursor) & 0x80:
				value |= 1 << value_bit
			bit_cursor += 1

			if bit_cursor > 7:
				current_byte, buffer = read_ui8(buffer[0]), buffer[1:]
				bit_cursor = 0
		header[item] = value / 20

	header['width'] = header['xmax'] - header['xmin']
	header['height'] = header['ymax'] - header['ymin']

	if need_close:
		input.close()
	return header


def main_window(type, title, width, height):
	if type == 'toplevel':
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	elif type == 'popup':
		window = gtk.Window(gtk.WINDOW_POPUP)

	window.set_position(gtk.WIN_POS_CENTER)
	window.connect('destroy', lambda x: gtk.main_quit())
	window.set_size_request(width, height)
	window.set_resizable(True)

	if title == False:
		window.set_decorated(False)
	else:
		window.set_title(title)

	return window


def script_action(webview, frame, request, action, ignore):
	base_uri = frame.get_uri()
	request_uri = request.get_uri()
	if base_uri and request_uri:
		base_uri = base_uri.split('#')
		request_uri = request_uri.split('#')
		if request_uri[0] == base_uri[0]:
			window = webview.parent
			if request_uri[1] == 'fullscreen':
				window.fullscreen()
			elif request_uri[1] == 'unfullscreen':
				window.unfullscreen()

	return False


def create_webview():
	webview = webkit.WebView()
	webview.connect('close-web-view', lambda x: gtk.main_quit())
	webview.connect("navigation-policy-decision-requested", script_action)
	settings = webview.get_settings()
	settings.set_property('enable-plugins', True)
	settings.set_property('enable-scripts', True)
	return webview


def move_center(window, width, height):
	screen_width = gtk.gdk.screen_width()
	screen_height = gtk.gdk.screen_height()

	if screen_width < width or screen_height < height:
		window.maximize()
	else:
		new_x = (screen_width - width)/2
		new_y = (screen_height - height)/2
		window.move(new_x, new_y)


def display_html(window, args):
	webview = create_webview()
	webview.load_string(args['html'], 'text/html', 'UTF-8', args['base'])

	window.set_title(args['title'])
	window.set_size_request(args['width']/2, args['height']/2)
	window.resize(args['width'], args['height'])
	move_center(window, args['width'], args['height'])
	window.add(webview)
	window.show_all()


def play(args):
	window = main_window(args.get('window-type', 'toplevel'), args['title'], args['width']/2, args['height']/2)
	window.resize(args['width'], args['height'])

	webview = create_webview()
	webview.load_string(args['html'], 'text/html', 'UTF-8', args['base'])

	if 'x' in args and 'y' in args:
		window.move(args['x'], args['y'])

	window.add(webview)
	window.show_all()

	if 'screenshot-file' in args:
		import gobject
		gobject.timeout_add(1500, save_screenshot, window, args['screenshot-file'])


def on_open_clicked(widget, window, box):
	dialog=gtk.FileChooserDialog(title="选择 Flash 文件", action=gtk.FILE_CHOOSER_ACTION_OPEN,
		buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
	swf_filter=gtk.FileFilter()
	swf_filter.set_name("Flash 文件(*.swf)")
	swf_filter.add_pattern("*.[Ss][Ww][Ff]")
	dialog.add_filter(swf_filter)
	response = dialog.run()

	if response == gtk.RESPONSE_OK:
		filename = dialog.get_filename()
		dialog.destroy()
		window.remove(box)
		play_args = pre_play(filename)
		display_html(window, play_args)

	dialog.destroy()


def open_file():
	window = main_window('toplevel', 'Flash Player', 550, 400)
	vbox = gtk.VBox()
	hbox = gtk.HBox()
	button = gtk.Button("打开文件")
	button.set_size_request(200, 70)
	button.connect("clicked", on_open_clicked, window, vbox)
	vbox.pack_start(hbox, fill=False)
	hbox.pack_start(button, fill=False)
	window.add(vbox)
	window.show_all()


def to_html(swf, button):
	html_template = """
<!DOCTYPE HTML>
<html>
<head>
	<meta charset="UTF-8" />
	<style type="text/css" media="screen">
		html,body,#flash {{
			margin: 0px;
			padding: 0px;
			height: 100%;
			width: 100%;
			overflow: hidden;
			font-size: 13px;
		}}
		#flash{{
			position: fixed;
			z-index: 0;
		}}
		.button{{
			position: fixed;
			top: 0px;
			right: 0px;
			opacity: 0.1;
			z-index: 1;
		}}
		.button:hover{{
			opacity: 1;
			color: black;
		}}
		ul,li{{
			margin: 0px;
			padding: 0px;
		}}
		.menu{{
			position: absolute;
			width: 12em;
			border-radius: 4px;
			list-style-type: none;
			padding-top: 5px;
			padding-bottom: 5px;
			background: #FFFFFF;
			border:1px solid #E1E1E1;
			box-shadow: 0px 5px 15px -5px black;
		}}
		.menu li{{
			position: relative;
			height: 24px;
			line-height: 24px;
			text-indent: 1.5em;
			vertical-align: middle;
		}}
		.menu li:hover{{
			background: #2CA7F8;
		}}
		.menu li a{{
			display: block;
			color: #303030;
			text-decoration: none;
		}}
		.menu hr{{
			background-color: #E1E1E1;
			border: none;
			height: 1px;
			margin-top: 2px;
			margin-bottom: 2px;
			width: 95%;
		}}
		.menu span{{
			float: right;
			font-size: 12px;
			margin-right: 1.5em;
			color: #D1D1D1;
			text-indent: 0em;
		}}
		.menu li:hover a{{
			color: #FFFFFF;
			cursor: default;
		}}
		.menu li a:focus{{
			outline: none;
		}}
	</style>
	<script type="text/javascript">
		window.onload = function(){{
			var rightMenu = document.getElementById("context-menu");
			rightMenu.style.display = "none";
			document.oncontextmenu = function(event){{
				var style = rightMenu.style;
				style.display = "block";
				var m = 15;
				if ((event.clientX + rightMenu.clientWidth + m) > window.innerWidth) {{
					style.left = window.innerWidth - rightMenu.clientWidth - m + "px";
				}} else if (event.clientX < m) {{
					style.left = m + "px";
				}} else {{
					style.left = event.clientX + "px";
				}}
				if ((event.clientY + rightMenu.clientHeight + m) > window.innerHeight) {{
					style.top = window.innerHeight - rightMenu.clientHeight - m + "px";
				}} else if (event.clientY < m) {{
					style.top = m + "px";
				}} else {{
					style.top = event.clientY + "px";
				}}
				return false;
			}};
			document.onclick = function(){{
				rightMenu.style.display = "none";
			}};
		}};
		document.onkeydown = function(event){{
			if(event.ctrlKey && event.keyCode == 13){{
				if(flash.IsPlaying()){{
					flash.StopPlay();
				}}
				else{{
					flash.Play();
				}};
			}}
			else if(event.ctrlKey && event.keyCode == 70){{
				window.location.replace('#fullscreen');
			}}
			else if(event.keyCode == 27){{
				window.location.replace('#unfullscreen');
			}}
			else if(event.ctrlKey && event.keyCode == 81){{
				window.close();
			}};
		}};
	</script>
</head>
<body>
	<object id="flash" type="application/x-shockwave-flash" width="100%" height="100%">
		<param name="movie" value="{swf}" />
		<param name="quality" value="high" />
		<param name="allowFullScreen" value="true" />
		<param name="wmode" value="opaque" />
	</object>
	<script type="text/javascript">
		var flash=document.getElementById("flash");
	</script>
	<ul id="context-menu" class="menu">
		<li><a href="javascript:flash.Play();">播放<span>Ctrl+Enter</span></a></li>
		<li><a href="javascript:flash.StopPlay();">暂停<span>Ctrl+Enter</span></a></li>
		<hr/>
		<li><a href="#fullscreen">全屏<span>Ctrl+F</span></a></li>
		<li><a href="#unfullscreen">退出全屏<span>Esc</span></a></li>
		<hr/>
		<li><a href="javascript:window.close();">退出<span>Ctrl+Q</span></a></li>
	</ul>
	{close_button}
</body>
</html>
"""
	close_button = '<input class="button" type="button" value="关闭窗口" onClick="window.close()" />'
	if button == True:
		return html_template.format(swf=urllib.quote(swf), close_button=close_button)
	else:
		return html_template.format(swf=urllib.quote(swf), close_button='')


def pre_play(swf):
	play_args = {}
	swf_abspath= os.path.abspath(swf)
	dir_path = os.path.dirname(swf_abspath)
	play_args['swf_file'] = os.path.basename(swf_abspath)
	swf_info = swfheader(swf_abspath)

	play_args['width'] = swf_info['width']
	play_args['height'] = swf_info['height']
	play_args['base'] = 'file://' + urllib.quote(dir_path) + '/'
	play_args['title'] = play_args['swf_file']

	opt_map = {
		'-X': 'x',
		'-Y': 'y',
		'-j': 'width',
		'-k': 'height'
	}

	for opt,arg in opts:
		if opt in ('--hide-menubar'):
			play_args['title'] = False
			if 'button' not in play_args:
				play_args['button'] = True
		elif opt in ('--window-type'):
			play_args['window-type'] = arg
			if 'button' not in play_args:
				play_args['button'] = True
		elif opt in ('--hide-button'):
			play_args['button'] = False
		elif opt in ('--screenshot-file'):
			play_args['screenshot-file'] = arg
		elif opt in ('-X', '-Y', '-j', '-k'):
			play_args[opt_map.get(opt, 'Pass')] = int(arg)

	play_args['html'] = to_html(play_args['swf_file'], play_args.get('button', False))
	return play_args


def save_screenshot(window, output):
	width, height = window.get_size()
	pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)
	screenshot = pixbuf.get_from_drawable(window.window, window.get_colormap(), 0, 0, 0, 0, width, height)
	screenshot.save(output, 'png')
	gtk.main_quit()


def main():
	if len(args) <= 0:
		open_file()
	else:
		play_args = pre_play(args[0])
		play(play_args)

	gtk.main()


main()
