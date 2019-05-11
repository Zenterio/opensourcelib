
def test_uninstall(Command, Package, Sudo):
    with Sudo():
        Command.run_expect([0], "apt-get remove zenterio-git-project -y")
    assert not Package("zenterio-git-project").is_installed