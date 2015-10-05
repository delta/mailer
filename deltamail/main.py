from deltamail.campaign import CampaignFactory


def console_main():
    print "it works"

'''

class TestCampaignFactory():
    def setUp(self):
        subject = "Greetings from {{company}}"
        fMailingList = "./tests/testCampaignFactory-files/mailingList.ml"
        fTemplate = "./tests/testCampaignFactory-files/template.mmtpl"
        fGlobalVars = "./tests/testCampaignFactory-files/globalVars.mvar"

        mailingList = ['FOB@bob.com', 'pop@bob.com']

        self.bmc = CampaignFactory(subject, mailingList,
                                   fTemplate, fGlobalVars)
        self.tmc = CampaignFactory(subject, fMailingList,
                                   fTemplate, fGlobalVars)

    def tearDown(self):
        pass

    def testInitilization(self):
    	print "Hello"
        loc1 = './tests/email-preview-bulk/'
        loc2 = './tests/testCampaignFactory-files/email-preview-transaction/'

        self.bmc.preview(loc1)
        self.tmc.preview(loc2)

def smartSend():
	return [subject, fMailingList, fTemplate, fGlobalVars]

def noobSend():
	return [subject, fMailingList, fTemplate, fGlobalVars]

def console_main():
    if smartsend in options
    	camobj = CampaignFactory( *smartsend() )
    else
    	camobj = CampaignFactory( *noobSend() )

    if preview option is there
    	camobj.preview(options["preview"] || "")
    else
    	camobj.send()
'''
