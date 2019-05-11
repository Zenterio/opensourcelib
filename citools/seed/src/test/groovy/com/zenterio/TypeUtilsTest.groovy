package com.zenterio

import static com.zenterio.TypeUtils.isMap
import static com.zenterio.TypeUtils.isCollection
import static com.zenterio.TypeUtils.isArray
import static com.zenterio.TypeUtils.isZeroSizedArrayLike
import static com.zenterio.TypeUtils.isArrayLike

class TypeUtilsTest extends GroovyTestCase {

    public void testIsMap() {
        assert isMap([:]) == true
        assert isMap([]) == false
    }

    public void testIsCollection() {
        assert isCollection([]) == true
        assert isCollection(new ArrayList<Integer>()) == true

        assert isCollection(new Object()) == false
        assert isCollection(new Object[0]) == false
        assert isCollection([:]) == false
    }

    public void testIsArray() {
        assert isArray(new Object[0]) == true
        assert isArray(new int[0]) == true

        assert isArray(new Object()) == false
        assert isArray(new ArrayList<Integer>()) == false
        assert isArray([]) == false
        assert isArray([:]) == false
    }

    public void testIsArrayLike() {
        assert isArrayLike([]) == true
        assert isArrayLike(new int[1]) == true
        assert isArrayLike(new ArrayList<String>()) == true
        assert isArrayLike([:]) == true

        assert isZeroSizedArrayLike(new Object()) == false
        assert isZeroSizedArrayLike("string") == false
    }

    public void testIsZeroSizedArrayLike() {
        assert isZeroSizedArrayLike([]) == true
        assert isZeroSizedArrayLike(new int[0]) == true
        assert isZeroSizedArrayLike(new ArrayList<String>()) == true

        assert isZeroSizedArrayLike(new Object()) == false
        assert isZeroSizedArrayLike("string") == false
        assert isZeroSizedArrayLike(new int[1]) == false
    }

}
