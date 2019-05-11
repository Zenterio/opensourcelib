include Asciidoctor

class TestData
  attr_reader :include_all_level, :include_summary_level, :include_other_level, :include_magic_level
  attr_reader :exclude_all_level, :exclude_summary_level, :exclude_other_level, :exclude_magic_level
  attr_reader :summary, :summary_parent
  attr_reader :section, :section_parent
  attr_reader :magic_section, :magic_section_parent
  attr_reader :second_paragraph, :second_paragraph_parent

  def initialize
    @include_all_level = Level.new 'name', ['all'], [], ['magic']
    @include_summary_level = Level.new 'name', ['summary'], [], ['magic']
    @include_other_level = Level.new 'name', ['other'], [], ['magic']
    @include_magic_level = Level.new 'name', ['magic'], [], ['magic']

    @exclude_all_level = Level.new 'name', ['all'], ['all'], ['magic']
    @exclude_summary_level = Level.new 'name', ['all'], ['summary'], ['magic']
    @exclude_other_level = Level.new 'name', ['all'], ['other'], ['magic']
    @exclude_magic_level = Level.new 'name', ['all'], ['magic'], ['magic']

    @summary = BlockMock.new
    @summary_parent = BlockMock.new context: :section, blocks: [@summary]
    @summary.parent = @summary_parent

    @section = BlockMock.new context: :section
    @section_parent = BlockMock.new context: :section, blocks: [@section]
    @section.parent = @section_parent

    @magic_section = BlockMock.new context: :section, title: 'Magic'
    @magic_section_parent = BlockMock.new context: :section, blocks: [@magic_section]
    @magic_section.parent = @magic_section_parent

    @second_paragraph = BlockMock.new
    @second_paragraph_parent = BlockMock.new context: :section, blocks: ['dummy', @second_paragraph]
    @second_paragraph.parent = @second_paragraph_parent
  end
end

class BlockMock
  attr_accessor :context, :parent, :blocks, :roles, :title, :attributes

  def initialize(context: :paragraph, blocks: [], parent: nil, roles: [], title: 'Title', attributes: {})
    @context = context
    @blocks = blocks
    @parent = parent
    @roles = roles
    @title = title
    @attributes = attributes
  end

end

class SectionMock < Section
  attr_accessor :blocks, :parent, :roles, :title, :attributes

  def initialize(blocks: [], parent: nil, roles: [], title: 'Title', attributes: {})
    @blocks = blocks
    @parent = parent
    @roles = roles
    @title = title
    @attributes = attributes
  end

end