package com.zenterio.jenkins.configuration.macroexpansion

import java.beans.PropertyDescriptor

interface ITransform<T> {
    public Object transform(Object obj, List<T> context)
}
