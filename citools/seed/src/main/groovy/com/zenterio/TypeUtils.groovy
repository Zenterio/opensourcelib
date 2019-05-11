package com.zenterio

class TypeUtils {

    /**
     * @param obj
     */
    public static boolean isZeroSizedArrayLike(Object obj) {
        return ((isArray(obj) && obj.length == 0) ||
            (isCollection(obj) && obj.size == 0)) ||
            (isMap(obj) && obj.size == 0)
    }

    public static boolean isArrayLike(Object obj) {
        return isArray(obj) || isCollection(obj) || isMap(obj)
    }

    /**
     * @param obj
     */
    public static boolean isCollection(Object obj) {
        return Collection.class.isAssignableFrom(obj.getClass())
    }

    /**
     * @param obj
     */
    public static boolean isArray(Object obj) {
        return obj.getClass().isArray()
    }

    /**
     * @param obj
     */
    public static boolean isMap(Object obj) {
        return Map.class.isAssignableFrom(obj.getClass())
    }

}
