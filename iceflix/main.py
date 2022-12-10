"""Main service for IceFlix"""
#!/usr/bin/env python3
#pylint: disable=invalid-name, unused-argument, import-error, inconsistent-return-statements, wrong-import-position, too-few-public-methods

import logging

import sys

import threading

import Ice

Ice.loadSlice('iceflix.ice')

import IceFlix


class Main(IceFlix.Main):
    """Services provided by the main service."""

    def __init__(self):
        self.authenticators = []
        self.mediaCatalogs = []
        self.fileServices = []

    def getAuthenticator(self, current=None):
        "Return the stored Authenticator proxy."
        if len(self.authenticators) != 0:
            for i in self.authenticators:
                try:
                    if i.ice_ping() is None:
                        return IceFlix.AuthenticatorPrx.checkedCast(i)
                except Exception as e:
                    raise IceFlix.TemporaryUnavailable() from e
        else:
            raise IceFlix.TemporaryUnavailable()

    def getCatalog(self, current=None):
        "Return the stored MediaCatalog proxy."
        if len(self.mediaCatalogs) != 0:
            for i in self.mediaCatalogs:
                try:
                    if i.ice_ping() is None:
                        return IceFlix.MediaCatalogPrx.checkedCast(i)
                except Exception as e:
                    raise IceFlix.TemporaryUnavailable() from e
        else:
            raise IceFlix.TemporaryUnavailable()

    def getFileService(self, current=None):
        "Return the stored FileService proxy."
        if len(self.fileServices) != 0:
            for i in self.fileServices:
                try:
                    if i.ice_ping() is None:
                        return IceFlix.FileServicePrx.checkedCast(i)
                except Exception as e:
                    raise IceFlix.TemporaryUnavailable() from e
        else:
            raise IceFlix.TemporaryUnavailable()

    def newService(self, proxy, service_id, current=None):
        "Receive a proxy of a new service."

        if IceFlix.AuthenticatorPrx.uncheckedCast(service_id) in self.authenticators:
            self.authenticators.remove(IceFlix.AuthenticatorPrx.uncheckedCast(service_id))

        elif IceFlix.MediaCatalogPrx.uncheckedCast(service_id) in self.mediaCatalogs:
            self.mediaCatalogs.remove(IceFlix.MediaCatalogPrx.uncheckedCast(service_id))

        elif IceFlix.FileServicePrx.uncheckedCast(service_id) in self.fileServices:
            self.fileServices.remove(IceFlix.FileServicePrx.uncheckedCast(service_id))

        else:
            timer = threading.Timer(30.00,self.eliminarProxy(service_id))
            if proxy.ice_isA('::IceFlix::Authenticator'):
                self.authenticators.append(IceFlix.AuthenticatorPrx.uncheckedCast(service_id))
                timer.start()

            elif proxy.ice_isA('::IceFlix::MediaCatalog'):
                self.mediaCatalogs.append(IceFlix.MediaCatalogPrx.uncheckedCast(service_id))
                timer.start()

            elif proxy.ice_isA('::IceFlix::FileService'):
                self.fileServices.append(IceFlix.FileServicePrx.uncheckedCast(service_id))
                timer.start()

    def announce(self, proxy, service_id, current=None):
        "Announcements handler."

        timer = threading.Timer(30.00,self.eliminarProxy(service_id))
        if proxy.ice_isA('::IceFlix::Authenticator'):
            if IceFlix.AuthenticatorPrx.uncheckedCast(service_id) not in self.authenticators:
                return
            print(f'Authenticator service: {service_id}')
            self.authenticators.append(IceFlix.AuthenticatorPrx.uncheckedCast(service_id))
            timer.start()

        elif proxy.ice_isA('::IceFlix::MediaCatalog'):
            if IceFlix.MediaCatalogPrx.uncheckedCast(service_id) not in self.mediaCatalogs:
                return
            print(f'MediaCatalog service: {service_id}')
            self.mediaCatalogs.append(IceFlix.MediaCatalogPrx.uncheckedCast(service_id))
            timer.start()

        elif proxy.ice_isA('::IceFlix::FileService'):
            if IceFlix.FileServicePrx.uncheckedCast(service_id) not in self.fileServices:
                return
            print(f'FileService service: {service_id}')
            self.fileServices.append(IceFlix.FileServicePrx.uncheckedCast(service_id))
            timer.start()

    def eliminarProxy(self, service_id):
        "Function that removes proxys from the proxys lists after 30 secs"
        if IceFlix.AuthenticatorPrx.uncheckedCast(service_id) in self.authenticators:
            self.authenticators.remove(IceFlix.AuthenticatorPrx.uncheckedCast(service_id))

        elif IceFlix.MediaCatalogPrx.uncheckedCast(service_id) in self.mediaCatalogs:
            self.mediaCatalogs.remove(IceFlix.MediaCatalogPrx.uncheckedCast(service_id))

        elif IceFlix.FileServicePrx.uncheckedCast(service_id) in self.fileServices:
            self.fileServices.remove(IceFlix.FileServicePrx.uncheckedCast(service_id))

class MainApp(Ice.Application):
    """Example Ice.Application for a Main service."""

    def __init__(self):
        super().__init__()
        self.servant = Main()
        self.proxy = None
        self.adapter = None

    def run(self, args):
        """Run the application, adding the needed objects to the adapter."""

        logging.info("Running Main application")

        comm = self.communicator()
        self.adapter = comm.createObjectAdapter("MainAdapter")
        self.adapter.activate()

        self.proxy = self.adapter.addWithUUID(self.servant)
        print(self.proxy)

        self.shutdownOnInterrupt()
        comm.waitForShutdown()

        return 0


main = MainApp()
sys.exit(main.main(sys.argv))
