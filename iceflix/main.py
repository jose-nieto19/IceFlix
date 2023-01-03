"""Main service for IceFlix"""
#!/usr/bin/env python3
#pylint: disable=invalid-name, unused-argument, import-error

import logging

import sys

import threading

import uuid

import Ice

import IceStorm

Ice.loadSlice('iceflix/iceflix.ice')

import IceFlix

class Announcement(IceFlix.Announcement):
    """Announcement interface"""

    def __init__(self):
        self.authenticators = {}
        self.mediaCatalogs = {}
        self.fileServices = {}

    def announce(self, proxy, service_id, current=None):
        "Announcements handler."

        timer = threading.Timer(10.0,function=self.removeProxy,args=([service_id]))
        if proxy.ice_isA('::IceFlix::Authenticator'):
            if str(service_id) not in self.authenticators:
                return
            print(f'Authenticator service: {service_id}')
            self.authenticators[str(service_id)] = IceFlix.AuthenticatorPrx.uncheckedCast(proxy)
            timer.start()

        elif proxy.ice_isA('::IceFlix::MediaCatalog'):
            if str(service_id) not in self.mediaCatalogs:
                return
            print(f'MediaCatalog service: {service_id}')
            self.mediaCatalogs[str(service_id)] = IceFlix.MediaCatalogPrx.uncheckedCast(proxy)
            timer.start()

        elif proxy.ice_isA('::IceFlix::FileService'):
            if str(service_id) not in self.fileServices:
                return
            print(f'FileService service: {service_id}')
            self.fileServices[str(service_id)] = IceFlix.FileServicePrx.uncheckedCast(proxy)
            timer.start()

    def removeProxy(self, service_id):
        "Function that removes proxys from the proxys lists after 10 secs"
        if str(service_id) in self.authenticators:
            self.authenticators.pop(str(service_id))

        elif str(service_id) in self.mediaCatalogs:
            self.mediaCatalogs.pop(str(service_id))

        elif str(service_id) in self.fileServices:
            self.fileServices.pop(str(service_id))

class Main(IceFlix.Main):
    """Services provided by the main service."""

    def __init__(self, announcement):
        self.announcement = announcement

    def getAuthenticator(self, current=None):
        "Return the stored Authenticator proxy."
        authList = list(self.announcement.authenticators.values())
        if len(authList) != 0:
            for i in authList:
                try:
                    if i.ice_ping() is None:
                        return IceFlix.AuthenticatorPrx.checkedCast(i)
                except Exception:
                    continue
        raise IceFlix.TemporaryUnavailable()

    def getCatalog(self, current=None):
        "Return the stored MediaCatalog proxy."
        catList = list(self.announcement.mediaCatalogs.values())
        if len(catList) != 0:
            for i in catList:
                try:
                    if i.ice_ping() is None:
                        return IceFlix.MediaCatalogPrx.checkedCast(i)
                except Exception:
                    continue
        raise IceFlix.TemporaryUnavailable()

    def getFileService(self, current=None):
        "Return the stored FileService proxy."
        fsList = list(self.announcement.fileServices.values())
        if len(fsList) != 0:
            for i in fsList:
                try:
                    if i.ice_ping() is None:
                        return IceFlix.FileServicePrx.checkedCast(i)
                except Exception:
                    continue
        raise IceFlix.TemporaryUnavailable()

class MainApp(Ice.Application):
    """Example Ice.Application for a Main service."""

    def __init__(self):
        super().__init__()
        self.announcementServant = Announcement()
        self.servant = Main(self.announcementServant)
        self.proxy = None
        self.mainId = str(uuid.uuid4())
        self.adapterMain = None
        self.adapterAnnouncement = None

    def announceMain(self, announcer):
        """Function that announces main in the topic "Announcement" every 10 secs."""
        announcer.announce(self.proxy, self.mainId)
        timer = threading.Timer(10.0,function=self.announceMain,args=([announcer]))
        timer.start()


    def run(self, args):
        """Run the application, adding the needed objects to the adapter."""

        logging.info("Running Main application")

        comm = self.communicator()
        self.adapterMain = comm.createObjectAdapter("MainAdapter")
        self.adapterMain.activate()

        self.proxy = self.adapterMain.addWithUUID(self.servant)

        topicManagerPrx = comm.stringToProxy("IceStorm/TopicManager:tcp -p 10000")
        topicManager = IceStorm.TopicManagerPrx.checkedCast(topicManagerPrx)
        self.adapterAnnouncement = comm.createObjectAdapter("AnnouncementAdapter")
        subscriber = self.adapterAnnouncement.addWithUUID(self.announcementServant)

        topic = topicManager.retrieve("Announcements")
        topic.subscribeAndGetPublisher({},subscriber)

        publisher = topic.getPublisher()
        announcer = IceFlix.AnnouncementPrx.uncheckedCast(publisher)

        self.announceMain(announcer)

        self.adapterAnnouncement.activate()
        self.shutdownOnInterrupt()
        comm.waitForShutdown()

        return 0


main = MainApp()
sys.exit(main.main(sys.argv))
