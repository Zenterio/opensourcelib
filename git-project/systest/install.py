
def test_install(Command, Package, Sudo):
    with Sudo():
        Command.run_expect([0], "gdebi --non-interactive /vagrant/dist/$(lsb_release -c -s)/zenterio-git-project_*.deb")
    assert Package("zenterio-git-project").is_installed
    assert Package("git").is_installed
    assert Package("git-doc").is_installed
