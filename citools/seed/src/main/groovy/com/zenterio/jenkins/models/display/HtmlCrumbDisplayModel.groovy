package com.zenterio.jenkins.models.display

import com.zenterio.jenkins.models.job.JobDescriptionModel;
import com.zenterio.jenkins.models.common.UrlModel;
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.IPropertySelector
import com.zenterio.jenkins.models.ModelEntity


class HtmlCrumbDisplayModel extends JobDescriptionModel {

    /**
     * The name shown in the Crumb path
     */
    String displayName

    /**
     * If true, the entity will only appear if it is the top item.
     * This is to prevent structures showing build flows showing up
     * in the crumb path.
     */
    Boolean onlyAsTop

    public HtmlCrumbDisplayModel(String displayName, Boolean onlyAsTop = false) {
        super("");
        this.displayName = displayName;
        this.onlyAsTop = onlyAsTop
    }

    /**
     * Parses the model tree to find any parents that has this kind of property
     * and creates a HTML bread crumb trail to the entity that has this
     * instance of the property model.
     * @return 	String with HTML, bread crumbs, of parent entity and its
     * 		 	relevant parents.
     */
    @Override
    public String getDescription() {
        /*
         * Get all parents that are an entity model and
         * that has the HtmlCrumbDisplay property in any of its children.
         * This will include the parent entity of this model, and it is
         * that model that is the top node.
         */
        List<IModel> crumbs = this.getParents(ModelEntity, false,
            { IPropertySelector item, ArrayList result ->
            HtmlCrumbDisplayModel crumbs = item.getProperty(HtmlCrumbDisplayModel, false, true)
            (crumbs && !(crumbs.onlyAsTop && !result.empty))
        })
        /* Want them in reverse order,
           starting root from left to right. */
        crumbs = crumbs.reverse()

        String result = crumbs.collect({ IPropertySelector m ->
            String url = m.getProperty(UrlModel, false, true)?.url
            String displayName = m.getProperty(HtmlCrumbDisplayModel, false, true)?.displayName
            if (url != null && url != "") {
                "<a href='${url}'>${displayName}</a>"
            } else {
                displayName
            }
        }).join(' :: ')
        result = "\n<h2>${result}</h2>"
        return result
    }

}
