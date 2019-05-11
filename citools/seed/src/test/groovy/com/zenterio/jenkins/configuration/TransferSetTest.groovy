package com.zenterio.jenkins.configuration

class TransferSetTest extends GroovyTestCase {
    public void testDefaultValues() {
        TransferSet transfer = new TransferSet('src', 'dir', null, null, null, false, false, false, false, 0, false, null)
        assert transfer.src == 'src'
        assert transfer.remoteDir == 'dir'
        assert transfer.removePrefix == ""
        assert transfer.excludeFiles == ""
        assert transfer.patternSeparator == "[, ]+"
        assert !transfer.noDefaultExcludes
        assert !transfer.makeEmptyDirs
        assert !transfer.flattenFiles
        assert !transfer.remoteDirIsDateFormat
        assert transfer.execTimeout == 120000
        assert !transfer.execInPTTY
        assert transfer.command == ""
    }

    public void testNullSrc() {
        TransferSet transfer = new TransferSet(null, 'dir', null, null, null, false, false, false, false, null, false, 'COMMAND')
        assert transfer.src == ''
    }

    public void testNullRemoteDir() {
        TransferSet transfer = new TransferSet('src', null, null, null, null, false, false, false, false, null, false, 'COMMAND')
        assert transfer.remoteDir == ''
    }

    public void testThatNoSrcAndNoCommandThrowsException() {
        shouldFail(IllegalArgumentException, {
            new TransferSet(null, null, null, null, null, false, false, false, false, null, false, null)
        })
    }
}
