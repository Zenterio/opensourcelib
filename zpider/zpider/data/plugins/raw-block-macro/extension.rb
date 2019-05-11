require 'asciidoctor/extensions' unless RUBY_ENGINE == 'opal'
require 'yaml'

include Asciidoctor

# A block macro that shows the raw contents of a file in a literal block
#
class RawBlockMacro < Asciidoctor::Extensions::BlockMacroProcessor
  include_dsl
  named :raw

  TO_ESCAPE_RX = /(^(:?include:|ifdef:|ifndef).*$)/
  TO_ESCAPE_SUB = '\\1'

  def process parent, target, attrs
    content = IO.read target
    escaped_content = content.gsub TO_ESCAPE_RX, TO_ESCAPE_SUB

    create_literal_block parent, escaped_content, attrs
  end
end
