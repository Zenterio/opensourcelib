package com.zenterio.jenkins.configuration

public interface IProductVariantHolder {
    public ProductVariant getDebug()
    public void setDebug(ProductVariant debug)

    public ProductVariant getRelease()
    public void setRelease(ProductVariant release)

    public ProductVariant getProduction()
    public void setProduction(ProductVariant production)
}
