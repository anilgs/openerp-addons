import os
import uno
import unohelper
import string
import tempfile
import base64
import sys
reload(sys)
sys.setdefaultencoding("latin1")
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from LoginTest import *
    from lib.error import *
    from lib.tools import *
    database="placement1"
    uid = 3

class ExportToRML( unohelper.Base, XJobExecutor ):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "openerp_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)

        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()

        # Read Data from sxw file
        tmpsxw = tempfile.mktemp('.'+"sxw")

        if not doc.hasLocation():
            mytype = Array(makePropertyValue("MediaType","application/vnd.sun.xml.writer"),)
            doc.storeAsURL("file://"+tmpsxw,mytype)

	data = read_data_from_file( get_absolute_file_path( doc.getURL()[7:] ) )

        if docinfo.getUserFieldValue(2) == "":
            ErrorDialog("Please Save this file on server","Use Send To Server Option in OpenERP Report Menu","Error")
            exit(1)

	filename = self.GetAFileName()
	if not filename:
	    exit(1)

        global passwd
        self.password = passwd

        try:
            sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
            res = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'sxwtorml',base64.encodestring(data))
	    if res['report_rml_content']:
		write_data_to_file( get_absolute_file_path( filename[7:] ), res['report_rml_content'] )
        except Exception,e:
	    ErrorDialog("Can't save the file to the hard drive.", "Exception: %s" % e, "Error" )

    def GetAFileName(self):
        sFilePickerArgs = Array(10)
        oFileDialog = createUnoService("com.sun.star.ui.dialogs.FilePicker")
        oFileDialog.initialize(sFilePickerArgs)
        oFileDialog.appendFilter("OpenERP Report File Save To ....","*.rml")

	f_path = "OpenERP-"+ os.path.basename( tempfile.mktemp("","") ) + ".rml"
	initPath = tempfile.gettempdir()
        oUcb = createUnoService("com.sun.star.ucb.SimpleFileAccess")
        if oUcb.exists(initPath):
	    oFileDialog.setDisplayDirectory('file://' + ( os.name == 'nt' and '/' or '' ) + initPath )

        oFileDialog.setDefaultName(f_path )

	sPath = oFileDialog.execute() == 1 and oFileDialog.Files[0] or None
        oFileDialog.dispose()
        return sPath

if __name__<>"package" and __name__=="__main__":
    ExportToRML(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( ExportToRML, "org.openoffice.openerp.report.exporttorml", ("com.sun.star.task.Job",),)
