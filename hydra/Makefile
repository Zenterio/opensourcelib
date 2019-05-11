
.PHONY: help check clean cleamvm cleanup
.PHONY: install install_tests
.PHONY: test systest
.PHONY: vagrant_systest vagrant_install

help:
	@$(MAKE) -pRrq -f $(MAKEFILE_LIST) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs

check: vagrant_systest


clean:
	@rm -rf phpunit-*-result.xml

cleanvm:
	vagrant destroy -f || true

cleanup: clean cleanvm

lint:
	@echo "PHP lint:"
	@ls controllers/*.php | xargs -L1 php -l
	@ls views/*.php | xargs -L1 php -l
	@ls helpers/*.php | xargs -L1 php -l
	@ls tests/*/*.php | xargs -L1 php -l

# Install the application on the current system
install:
	@install/install_hydra

# Install the application and tests on the current system
install_tests: install
	@install/install_tests

# Install on the current system and
# execute system tests against the installation
# ! Should only be run in the context of a throw away system since it
# makes modifications to the installed system.
systest: install_tests lint
	@echo "Run PHPUnit"
	@sudo -u www-data phpunit --log-junit /var/lib/hydra/phpunit-result.xml -c /usr/share/hydra/phpunit.xml; status=$$?;mv /var/lib/hydra/phpunit-result.xml ./phpunit-$$(hostname)-result.xml; exit $$status

vagrant_systest: vagrant_systest_halt_u12 vagrant_systest_halt_u14 vagrant_systest_halt_u16

vagrant_install: vagrant_install_halt_u12 vagrant_install_halt_u14 vagrant_install_halt_u16

vagrant_systest_halt_u%: vagrant_systest_u%
	@vagrant halt --force u$*

vagrant_install_halt_u%: vagrant_install_u%
	@vagrant halt --force u$*

# start vagrant and run system tests in the VM
vagrant_systest_u%:
	@vagrant up u$*
	@vagrant ssh u$* --command "cd /vagrant/ && sudo $(MAKE) systest"

# start vagrant and install the application
vagrant_install_u%:
	@vagrant up u$*
	@vagrant ssh u$* --command "cd /vagrant/ && sudo $(MAKE) install"
