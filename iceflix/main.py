"""Main service for IceFlix"""
#!/usr/bin/env python3
#pylint: disable=invalid-name, unused-argument, import-error, no-member, wrong-import-position

import logging

import sys

import threading

import uuid

import Ice

import IceStorm

Ice.loadSlice('iceflix/iceflix.ice')

import IceFlix

mainId = str(uuid.uuid4())

class Announcement(IceFlix.Announcement):
    """Announcement interface"""

    def __init__(self):
        self.authenticators = {}
        self.mediaCatalogs = {}
        self.fileServices = {}

    def announce(self, proxy, service_id, current=None):
        "Announcements handler."

        timer = threading.Timer(10.0,function=self.removeProxy,args=([service_id]))
        timer.daemon = True
        if proxy.ice_isA('::IceFlix::Authenticator'):
            print(f'Authenticator service: {service_id}')
            self.authenticators[str(service_id)] = IceFlix.AuthenticatorPrx.uncheckedCast(proxy)
            timer.start()

        elif proxy.ice_isA('::IceFlix::MediaCatalog'):
            print(f'MediaCatalog service: {service_id}')
            self.mediaCatalogs[str(service_id)] = IceFlix.MediaCatalogPrx.uncheckedCast(proxy)
            timer.start()

        elif proxy.ice_isA('::IceFlix::FileService'):
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
        self.last_auth = None
        self.last_catalog = None
        self.last_file= None

    def getAuthenticator(self, current=None):
        "Return the stored Authenticator proxy."
        authList = list(self.announcement.authenticators.values())
        if len(authList) != 0:
            for i in authList:
                if self.last_auth is None or len(authList) == 1:
                    try:
                        if i.ice_ping() is None:
                            self.last_auth = i
                            return IceFlix.AuthenticatorPrx.checkedCast(i)
                    except Exception:
                        continue
                else:
                    if i == self.last_auth:
                        continue
                    try:
                        if i.ice_ping() is None:
                            self.last_auth = i
                            return IceFlix.AuthenticatorPrx.checkedCast(i)
                    except Exception:
                        continue
        #Si no funciona un proxy distinto, se comprueba el ultimo enviado
        if self.last_auth is not None:
            if self.last_auth.ice_ping() is None:
                return IceFlix.AuthenticatorPrx.checkedCast(self.last_auth)
        raise IceFlix.TemporaryUnavailable()

    def getCatalog(self, current=None):
        "Return the stored MediaCatalog proxy."
        catList = list(self.announcement.mediaCatalogs.values())
        if len(catList) != 0:
            for i in catList:
                if self.last_catalog is None or len(catList) == 1:
                    try:
                        if i.ice_ping() is None:
                            self.last_catalog = i
                            return IceFlix.MediaCatalogPrx.checkedCast(i)
                    except Exception:
                        continue
                else:
                    if i == self.last_catalog:
                        continue
                    try:
                        if i.ice_ping() is None:
                            self.last_catalog = i
                            return IceFlix.MediaCatalogPrx.checkedCast(i)
                    except Exception:
                        continue
        #Si no funciona un proxy distinto, se comprueba el ultimo enviado
        if self.last_catalog is not None:
            if self.last_catalog.ice_ping() is None:
                return IceFlix.MediaCatalogPrx.checkedCast(self.last_catalog)
        raise IceFlix.TemporaryUnavailable()

    def getFileService(self, current=None):
        "Return the stored FileService proxy."
        fsList = list(self.announcement.fileServices.values())
        if len(fsList) != 0:
            for i in fsList:
                if self.last_file is None or len(fsList) == 1:
                    try:
                        if i.ice_ping() is None:
                            self.last_file = i
                            return IceFlix.FileServicePrx.checkedCast(i)
                    except Exception:
                        continue
                else:
                    if i == self.last_file:
                        continue
                    try:
                        if i.ice_ping() is None:
                            self.last_file = i
                            return IceFlix.FileServicePrx.checkedCast(i)
                    except Exception:
                        continue
        #Si no funciona un proxy distinto, se comprueba el ultimo enviado
        if self.last_file is not None:
            if self.last_file.ice_ping() is None:
                return IceFlix.FileServicePrx.checkedCast(self.last_file)
        raise IceFlix.TemporaryUnavailable()

class MainApp(Ice.Application):
    """Example Ice.Application for a Main service."""

    def __init__(self):
        super().__init__()
        self.announcementServant = Announcement()
        self.servant = Main(self.announcementServant)
        self.proxy = None
        self.adapter = None

    def announceMain(self, announcer):
        """Function that announces main in the topic "Announcement" every 10 secs."""
        announcer.announce(self.proxy, mainId)
        timer = threading.Timer(10.0,function=self.announceMain,args=([announcer]))
        timer.daemon = True
        timer.start()


    def run(self, args):
        """Run the application, adding the needed objects to the adapter."""

        logging.info("Running Main application")

        comm = self.communicator()
        self.adapter = comm.createObjectAdapter("MainAdapter")
        self.adapter.activate()

        self.proxy = self.adapter.addWithUUID(self.servant)

        topic_manager = IceStorm.TopicManagerPrx.checkedCast(
            comm.propertyToProxy("IceStorm.TopicManager")
        )
        subscriber = self.adapter.addWithUUID(self.announcementServant)

        topic = topic_manager.retrieve("Announcements")
        topic.subscribeAndGetPublisher({},subscriber)

        publisher = topic.getPublisher()
        announcer = IceFlix.AnnouncementPrx.uncheckedCast(publisher)

        self.announceMain(announcer)

        self.shutdownOnInterrupt()
        comm.waitForShutdown()

        topic.unsubscribe(subscriber)

        return 0


main = MainApp()
sys.exit(main.main(sys.argv))
