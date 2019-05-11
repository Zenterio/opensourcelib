RUBY_ENGINE == 'opal' ? (require 'raw-block-macro/extension') : (require_relative 'raw-block-macro/extension')

Asciidoctor::Extensions.register do
  block_macro RawBlockMacro
end
