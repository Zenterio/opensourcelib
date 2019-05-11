package com.zenterio.jenkins.configuration

import com.zenterio.jenkins.RetentionPolicy;

import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

class BaseStructureConfigTest extends GroovyTestCase {

    Project p

    @Override
    protected void setUp() {
        this.p = Project.testData
    }

    public void testGetAllContacts() {
        assert this.p.getAllContacts().size() == 4
        assert this.p.getAllContacts().getEmailList().join(' ') == 'project.manager@mail.com tech.lead@mail.com w1@example.com second@example.com'
    }

    public void testGetAllContactsWithNoPM() {
        this.p.pm = null
        assert this.p.getAllContacts().size() == 3
    }

    public void testAddWatcher() {
        assert this.p.watchers.size() == 2
        this.p.addWatchers([Watcher.testData] as ContactInformationCollection)
        assert this.p.watchers.size() == 3
    }

    public void testInheritAsClone() {

        assert parent == child
        assert !parent.is(child)
    }

    public void testInheritInProjectIsClone() {
        shouldFail(CloneNotSupportedException) {
            Project child = this.p.inherit()
        }
    }

    public void testDeepClone() {
        BaseStructureConfigImp bsc = BaseStructureConfigImp.testData
        BaseStructureConfigImp clone = bsc.clone()
        assert bsc == clone
        assert !bsc.is(clone)
    }
}


@Canonical()
@EqualsAndHashCode(callSuper=true, includeFields=true)
class BaseStructureConfigImp extends BaseStructureConfig {

    public BaseStructureConfigImp() { super() }

    public BaseStructureConfigImp(BaseStructureConfigImp other) {
        super(other)
    }

    @Override
    public BaseStructureConfigImp clone() throws CloneNotSupportedException {
        return new BaseStructureConfigImp(this)
    }

    public static BaseStructureConfigImp getTestData() {
        BaseStructureConfigImp data = new BaseStructureConfigImp()
        data.pm = ProjectManager.testData
        data.techLead = TechLead.testData
        data.watchers = ContactInformationCollection.testData
        data.publishOverSSHList = PublishOverSSHList.testData
        return data
    }

}
