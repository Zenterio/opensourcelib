
package com.zenterio.jenkins.configuration.xml
import org.xml.sax.SAXParseException;


class ValidatingXmlParserFactoryTest extends GroovyTestCase {

    void testIncompleteXmlShouldThrowException()
    {
        def txt = """\
<?xml version="1.0"?>
<!DOCTYPE projects SYSTEM "config/config.dtd"> 
<projects>
 <project name="projname">
  <origin name="oriname">
   <repository name="reponame"
	       dir="repodir"
	       remote="reporemote"
	       branch="repobranch"/>
  </origin>
 </project>
</projects>
"""
        shouldFail(SAXParseException, { def parsedProjectXml = ValidatingXmlParserFactory.getXmlParser().parseText(txt) })
    }

}
