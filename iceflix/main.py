#!/usr/bin/env python3

import logging

import sys

import Ice

Ice.loadSlice('iceflix.ice')

import IceFlix  # pylint:disable=import-error


class Main(IceFlix.Main):

    def __init__(self):
        self.authenticators = []
        self.mediaCatalogs = []
        self.fileServices = []

    def getAuthenticator(self, current):  # pylint:disable=invalid-name, unused-argument
        "Return the stored Authenticator proxy."
        try:
            
        except:
            raise IceFlix.TemporaryUnavailable()

    def getCatalog(self, current):  # pylint:disable=invalid-name, unused-argument
        "Return the stored MediaCatalog proxy."
            try:

            except:
                raise IceFlix.TemporaryUnavailable()

    def getFileService(self, current):
        "Return the stored FileService proxy."
            try:
                
            except:
                raise IceFlix.TemporaryUnavailable()

    def newService(self, proxy, service_id, current):  # pylint:disable=invalid-name, unused-argument
        "Receive a proxy of a new service."

    def announce(self, proxy, service_id, current=None):  # pylint:disable=invalid-name, unused-argument
        "Announcements handler."
        if proxy.ice_isA('::IceFlix::Authenticator'):
            print(f'Authenticator service: {service_id}')
            self.authenticators.append(IceFlix.AuthenticatorPrx.uncheckedCast(service_id))

        elif proxy.ice_isA('::IceFlix::MediaCatalog'):
            print(f'Mediacatalog service: {service_id}')
            self.mediaCatalogs.append(IceFlix.MediaCatalogPrx.uncheckedCast(service_id))

        elif proxy.ice_isA('::IceFlix::FileService'):
            print(f'FileService service: {service_id}')
            self.fileServices.append(IceFlix.AuthenticatorPrx.uncheckedCast(service_id))


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

        authenticator = self.getAuthenticator()
        catalog = self.getCatalog()
        fileService = self.getFileService()

        comm = self.communicator()
        self.adapter = comm.createObjectAdapter("MainAdapter")
        self.adapter.activate()

        self.proxy = self.adapter.addWithUUID(self.servant)

        self.shutdownOnInterrupt()
        comm.waitForShutdown()

        return 0


main = MainApp()
sys.exit(main.main(sys.argv))
