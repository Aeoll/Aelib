"""
<<<<<<< HEAD
		From QLIB
=======
		Adapted from QLIB
>>>>>>> 87047bf7ffc8203a6a98a0461b92961204d15cc7
		Note: this script is automatically reloaded on each node creation!
"""
import hou
import os
import sys
import datetime

# ================================
# RS
# ================================
# If a Redshift ROP is present in the scene, auto-add the obj spare params. Also auto-populate Cd in vertex and pt?
# Split this into another module?
def redshiftDefaults(kwargs):
	n = kwargs['node']
	n.setSelected(True, True) # set selected to obj spare params works properly

	rsrops = []
	try:
		rsrop_type = hou.nodeType(hou.ropNodeTypeCategory(), "Redshift_ROP")
		rsrops = rsrop_type.instances()
	except:
		# Redshift is not installed
		pass

	if(len(rsrops) > 0):		
		if (n.type().name() == "geo"):
			hou.hscript('Redshift_objectSpareParameters')
			n.parm("RS_objprop_attr_points").set("Cd")
			n.parm("RS_objprop_attr_points").set("Alpha")
			n.parm("RS_objprop_attr_vertex").set("Cd")
		elif(n.type().name() == "cam"):
			hou.hscript('Redshift_cameraSpareParameters')

# =================================
# Node colours
# =================================

def msg(m):
	msg = "[%s OnCreated.py] %s" % (datetime.datetime.now().strftime("%y%m%d %H:%M.%S"), m)
	sys.__stderr__.write(msg+"\n")
	#print msg

def colorize_op(kwargs):
	'''.'''

	# node type names and default colors
	#
	cs = {
		'cam':           (0.5, 0.5, 0.5),
		'geo':           (0.6, 0.6, 0.6),
		'hlight':        (1.0, 1.0, 0.8),
		'indirectlight': (1.0, 1.0, 0.6),
		'instance':      (1.0, 0.8, 0.8),

		'shopnet':       (1.0, 1.0, 0.8),

		'null':          (0.0, 0.533, 0.0),

		'chopnet':       (0.0, 1.0, 0.0),

		'material':      (0.6, 0.6, 1.0),

		'cache':         (1.0, 0.4, 0.0),
		'filecache':     (1.0, 0.4, 0.0),
		'ae_FileCache_1':     (1.0, 0.4, 0.0),

		'dopnet':        (0.8, 0.0, 0.0),

		'object_merge':  (0.0, 0.2, 1.0),
		'dopio':  (0.0, 0.2, 1.0),
		'dopimport':  (0.0, 0.2, 1.0),

		'switch':  (0.5, 0.0, 1.0),

		'ropnet':        (0.2, 0.0, 0.4),
		'rop_geometry':  (0.2, 0.0, 0.4),
		'rop_alembic':   (0.2, 0.0, 0.4),
		
		'attribwrangle':   (1.0,0.65,0.0),

		'explodedview':  (0.0, 0.4, 1.0),

		'ifd':           (0.8, 0.8, 1.0),

		'oceansource':       (1.0, 1.0, 1.0),
		'whitewatersource':  (1.0, 1.0, 1.0),

		'lastone':       (0,0,0)
	}

	# list of nodes to be created as bypassed by default
	#
	bypass = [
		'cache',
		'filecache',
		'lastone'
	]

	try:
		N = kwargs['node']
		n = kwargs['node'].name()
		t = kwargs['type'].name()
		dbg('node=%s type=%s' % (n, t, ))


		# set all solver nodes to white
		#
		if 'solver' in t.lower():
			N.setColor( hou.Color((1, 1, 1)) )


		# set node types to certain colors
		#
		if t in cs:
			N.setColor( hou.Color( cs[t] ) )


		# bypass some node types by default
		#
		if t in bypass:
			N.bypass(True)

	except:
		pass # ignore errors silently

colorize_op(kwargs)
redshiftDefaults(kwargs)