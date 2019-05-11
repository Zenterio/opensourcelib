package com.zenterio.jenkins.configuration.xml

import org.xml.sax.ErrorHandler
import org.xml.sax.SAXParseException

import com.zenterio.jenkins.configuration.BaseConfig

abstract class ConfigXmlParserTestCase extends GroovyTestCase {

    XmlParser xp = null
    XmlParser xpNoneVal = null
    ConfigXmlParser parser = null
    String topElement = null

    void setUp(String topElement) {
        super.setUp()
        this.xp = new XmlParser(true, true)
        this.xp.setErrorHandler(new XmlErrorHandler())
        this.xp.setFeature("http://apache.org/xml/features/disallow-doctype-decl", false)
        this.xp.setProperty("http://javax.xml.XMLConstants/property/accessExternalDTD", "all")
        this.parser = new ConfigXmlParser()

        this.xpNoneVal = new XmlParser(false, true)
        this.xpNoneVal.setErrorHandler(new XmlErrorHandler())
        this.xpNoneVal.setFeature("http://apache.org/xml/features/disallow-doctype-decl", false)
        this.xpNoneVal.setProperty("http://javax.xml.XMLConstants/property/accessExternalDTD", "all")

        this.topElement = topElement
    }

    public BaseConfig parse(String xml, validate=true) {
        xml = """\
<?xml version="1.0"?>
<!DOCTYPE ${this.topElement} SYSTEM "config/config.dtd">
""" + xml

        def parsedXml = (validate) ? this.xp.parseText(xml) : this.xpNoneVal.parseText(xml)
        return this.parser.parse(parsedXml)
    }

    /*
     * Error handler for the XML Parser to generate an exception on failed
     * validation of the XML file.
     */
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

}
