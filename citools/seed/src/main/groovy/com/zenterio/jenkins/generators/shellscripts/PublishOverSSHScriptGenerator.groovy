package com.zenterio.jenkins.generators.shellscripts

import com.zenterio.jenkins.generators.IEntityGenerator
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.ModelProperty

class PublishOverSSHScriptGenerator implements IPropertyGenerator, IEntityGenerator{

    private String outputFolder

    public PublishOverSSHScriptGenerator(String outputDirectory) {
        this.outputFolder = outputDirectory
    }

    @Override
    public void generate(ModelEntity model) {
        this.renderModel(model)
    }

    @Override
    public void generate(ModelProperty model, Object entity) {
        this.renderModel(model)
    }

    private void renderModel(IModel model) {
        if (model.hasProperty('publishOverSSHList'))
            for (publish in model.publishOverSSHList.getEnabled()) {
                for (transferSet in publish.transferSets) {
                    File scriptFile = new File(outputFolder+'/'+model.hashCode())
                    if (!scriptFile.exists() && transferSet.command.length() > 0) {
                        scriptFile.getParentFile().mkdirs()
                        scriptFile.write(transferSet.command)
                    }
                }
            }
    }

}
