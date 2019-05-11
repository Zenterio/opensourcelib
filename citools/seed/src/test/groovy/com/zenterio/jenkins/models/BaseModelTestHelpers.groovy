package com.zenterio.jenkins.models

class BaseModelTestHelpers extends GroovyTestCase {

    class Base extends BaseModel {}
    class Sub extends Base {}

    @Override
    void setUp() throws Exception {
    }

    void testMatchClassSingleClassStrict() {
        BaseModel m = new BaseModel()

        assert ! m.matchClass(new Base(), [Sub], true)
        assert m.matchClass(new Sub(), [Sub], true)
        assert ! m.matchClass(new Sub(), [Base], true)
    }

    void testMatchClassSingleClassNoneStrict() {
        BaseModel m = new BaseModel()

        assert ! m.matchClass(new Base(), [Sub], false)
        assert m.matchClass(new Sub(), [Sub], false)
        assert m.matchClass(new Sub(), [Base], false)
    }

    void testMatchClassMultiClassStrict() {
        BaseModel m = new BaseModel()

        assert m.matchClass(new Base(), [Sub, Base], true)
        assert ! m.matchClass(new Base(), [Sub, Object], true)
        assert m.matchClass(new Sub(), [Sub, Base], true)
        assert ! m.matchClass(new Sub(), [Base, Object], true)
    }

    void testMatchClassMultiClassNoneStrict() {
        BaseModel m = new BaseModel()

        assert m.matchClass(new Base(), [Sub, Base], false)
        assert m.matchClass(new Base(), [Sub, Object], false)
        assert m.matchClass(new Sub(), [Sub, Base], false)
        assert m.matchClass(new Sub(), [Base, Object], false)
    }
}

