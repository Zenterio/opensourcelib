package com.zenterio.jenkins.models.view


class CategoryViewModel extends ViewModel {

    CategoryGroupingRule[] groupingRules

    /**
     *
     * @param name
     * @param displayName
     * @param description
     * @param url
     * @param fullName
     * @param jobNames
     * @param jobRegEx
     * @param groupingRules
     */
    public CategoryViewModel(String name, String displayName,
            String description, String url, String fullName, String[] jobNames,
            String jobRegEx, CategoryGroupingRule[] groupingRules) {
        super(name, displayName, description, url, fullName, jobNames, jobRegEx)
        this.groupingRules = groupingRules
    }




}
