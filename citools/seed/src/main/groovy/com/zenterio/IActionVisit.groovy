package com.zenterio

import java.beans.PropertyDescriptor

interface IActionVisit<T> {
    public void perform(Object obj, List<T> context, String propertyName)
    public void perform(Object[] obj, List<T> context, String propertyName)
}
