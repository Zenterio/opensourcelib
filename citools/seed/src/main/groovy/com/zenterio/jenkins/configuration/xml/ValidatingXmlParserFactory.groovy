package com.zenterio.jenkins.configuration.xml

class ValidatingXmlParserFactory
{
    static XmlParser getXmlParser()
    {
        XmlParser xmlParser=new XmlParser(true,true)
        xmlParser.setFeature("http://apache.org/xml/features/disallow-doctype-decl", false)
        xmlParser.setProperty("http://javax.xml.XMLConstants/property/accessExternalDTD", "all")
        xmlParser.setErrorHandler(new XmlErrorHandler())
        return xmlParser
    }

}
