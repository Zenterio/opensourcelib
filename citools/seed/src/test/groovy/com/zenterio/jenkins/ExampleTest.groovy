
package com.zenterio.jenkins


/**
 * Code examples until we get used to Groovy.
 */
class ExampleTest
    extends GroovyTestCase
{

    /**
     * Shows the use of shouldFail()
     */
    void testException()
    {
        shouldFail(Exception, { throw new Exception() })
    }


}
