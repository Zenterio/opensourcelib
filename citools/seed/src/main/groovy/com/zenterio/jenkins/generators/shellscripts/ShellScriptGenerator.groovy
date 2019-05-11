package com.zenterio.jenkins.generators.shellscripts

import com.zenterio.jenkins.generators.IEntityGenerator
import com.zenterio.jenkins.generators.IPropertyGenerator
import com.zenterio.jenkins.models.IModel
import com.zenterio.jenkins.models.ModelEntity
import com.zenterio.jenkins.models.ModelProperty

import java.security.MessageDigest


class ShellScriptGenerator implements IPropertyGenerator, IEntityGenerator {

    private String outputFolder
    private MessageDigest md5calculator

    public ShellScriptGenerator(String outputDirectory) {
        this.outputFolder = outputDirectory
        this.md5calculator = MessageDigest.getInstance("MD5")
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
        if (model.hasProperty('script')) {
            String content = model.script
            String md5sum = calcMD5Sum(content)
            File scriptFile = new File(outputFolder+'/'+md5sum)
            if (!scriptFile.exists()) {
                scriptFile.getParentFile().mkdirs()
                scriptFile.write(content)
            }
        }
    }

    private String calcMD5Sum(String content) {
        return this.md5calculator.digest(content.bytes).encodeHex().toString()
    }
}
