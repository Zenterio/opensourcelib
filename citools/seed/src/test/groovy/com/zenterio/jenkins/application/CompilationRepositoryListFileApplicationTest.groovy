package com.zenterio.jenkins.application

import groovy.util.GroovyTestCase

class CompilationRepositoryListFileApplicationTest   extends GroovyTestCase {

    public void testGenerate() {
        def compileWriterMock = new StringWriter()
        def testWriterMock = new StringWriter()

        def compileFileMock = new File('path/to/compile.txt')
        def testFileMock = new File('path/to/test.txt')

        compileFileMock.metaClass.with {
            withWriter = { String encoding, Closure c -> c.call(compileWriterMock) }
            mkdirs = {}
        }
        testFileMock.metaClass.with {
            withWriter = { String encoding, Closure c -> c.call(testWriterMock) }
            mkdirs = {}
        }

        String testConfDir = 'src/test/resources/repo-list'

        CompilationRepositoryListFileApplication.generate(testConfDir,
                                                          compileFileMock,
                                                          testFileMock)

        String expectedCompile='''\
NAME REMOTE_I
NAME3 REMOTE_III
RNAME RREMOTE_I
RNAME3 RREMOTE_III
TNAME TREMOTE_I
TNAME3 TREMOTE_III
'''
        String expectedTest='''\
TNAME TREMOTE_I
TNAME3 TREMOTE_III
'''
        assert compileWriterMock.toString() == expectedCompile
        assert testWriterMock.toString() == expectedTest

    }
}
