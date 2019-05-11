RUBY_ENGINE == 'opal' ? (require 'zpider-tree-processor/extension') : (require_relative 'zpider-tree-processor/extension')

Asciidoctor::Extensions.register do
  treeprocessor ZpiderTreeProcessor
end
