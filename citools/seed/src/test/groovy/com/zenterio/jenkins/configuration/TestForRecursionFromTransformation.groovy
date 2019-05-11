package com.zenterio.jenkins.configuration

import groovy.transform.AutoClone
import groovy.transform.Canonical
import groovy.transform.EqualsAndHashCode

class TestForRecursionFromTransformation extends GroovyTestCase  {

    public void testToStringIsNotLoopingForever() {
        Project p = Project.testData
        assert p.toString().class == String
    }

    public void testEqualIsNotLoopingForever() {
        Project p1 = Project.testData
        Project p2 = Project.testData
        assert !p1.is(p2)
        assert p1 == p2
    }

    public void testEqualItemsAreReducedByUnique() {
        Repository data = Repository.testData
        Repository clone = data.clone()
        assert data == clone
        assert !data.is(clone)
        assert [data, clone].unique().size() == 1
    }

    @Canonical
    @EqualsAndHashCode(includeFields=true)
    @AutoClone
    private class ArrayContainer {
        def array

        public ArrayContainer(Project member) {
            this.array = [member] as Project[]
        }
    }

    public void testAutoCloneUseShallowCopyForArrays()
    {
        ArrayContainer arrayContainer = new ArrayContainer(Project.testData)
        ArrayContainer clone = arrayContainer.clone()

        assert arrayContainer == clone
        assert !arrayContainer.is(clone)
        assert arrayContainer.array[0].is(clone.array[0])
    }

    @Canonical
    @EqualsAndHashCode(includeFields=true)
    @AutoClone
    private class ArrayListContainer {
        ArrayList<Project> arrayList

        public ArrayListContainer(Project member) {
            this.arrayList = [member]
        }
    }

    public void testAutoCloneUseShallowCopyForArrayLists()
    {
        ArrayListContainer arrayListContainer = new ArrayListContainer(Project.testData)
        ArrayListContainer clone = arrayListContainer.clone()

        assert arrayListContainer == clone
        assert !arrayListContainer.is(clone)
        assert arrayListContainer.arrayList[0].is(clone.arrayList[0])
    }
}
