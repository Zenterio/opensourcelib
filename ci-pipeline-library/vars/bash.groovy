
def call(command, setFlags='-eux') {
    sh "#!/bin/bash\nset ${setFlags}\n ${command}"
}
