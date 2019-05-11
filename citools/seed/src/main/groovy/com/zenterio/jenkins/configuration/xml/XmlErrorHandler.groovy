package com.zenterio.jenkins.configuration.xml

import org.xml.sax.ErrorHandler
import org.xml.sax.SAXParseException

class XmlErrorHandler implements ErrorHandler {

    public void warning(SAXParseException exception) throws SAXParseException {
        throw exception
    }

    public void error(SAXParseException exception) throws SAXParseException {
        throw exception
    }

    public void fatalError(SAXParseException exception) throws SAXParseException {
        throw exception
    }
}
