require "minitest/autorun"
require_relative '../extension'
require_relative './utils'

class TestRecursiveRemoveEmptySections < Minitest::Test

  def setup
    $stdout = StringIO.new
  end

  def test_recursively_remove_sections
    parent = BlockMock.new
    section_with_blocks = SectionMock.new parent: parent
    summary = BlockMock.new parent: section_with_blocks
    section_with_blocks.blocks = [summary]
    section_without_blocks = SectionMock.new parent: parent
    parent.blocks = [section_with_blocks, section_without_blocks]

    ZpiderTreeProcessor.new.recursive_remove_empty_sections parent

    assert_equal 1, parent.blocks.length
    assert_equal [section_with_blocks], parent.blocks
  end

  def test_remove_section_that_is_empty_after_removing_subsection
    parent = BlockMock.new
    section_with_subsection = SectionMock.new parent: parent
    subsection = SectionMock.new parent: section_with_subsection
    section_with_subsection.blocks = [subsection]
    parent.blocks = [section_with_subsection]

    ZpiderTreeProcessor.new.recursive_remove_empty_sections parent

    assert_empty parent.blocks
  end
end
