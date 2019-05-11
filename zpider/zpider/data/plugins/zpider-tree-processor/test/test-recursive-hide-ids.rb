require "minitest/autorun"
require_relative '../extension'
require_relative './utils'

class TestRecursiveHideIds < Minitest::Test

  def setup
    $stdout = StringIO.new
  end

  def test_everything_included
    data = IdsTestData.new
    ZpiderTreeProcessor.new.recursive_hide_ids data.top_level, [], []

    assert_equal data.top_level.blocks, [data.level_section]
    assert_equal data.level_section.blocks, [data.level_summary, data.level_subsection]
    assert_equal data.level_subsection.blocks, [data.sublevel_summary, data.level_subsubsection_3, data.level_subsubsection_4]
    assert_equal data.level_subsubsection_3.blocks, [data.subsublevel_content_3]
    assert_equal data.level_subsubsection_4.blocks, [data.subsublevel_content_4]
  end

  def test_exclude_id_removes_section_and_subsections
    data = IdsTestData.new
    ZpiderTreeProcessor.new.recursive_hide_ids data.top_level, [], ['a']
    
    assert_equal data.top_level.blocks, []
  end

  def test_include_subsection_id_in_excluded_section_has_no_effect
    data = IdsTestData.new
    ZpiderTreeProcessor.new.recursive_hide_ids data.top_level, ['b'], ['a']
    
    assert_equal data.top_level.blocks, []
  end

  def test_exclude_id_has_priority_over_include_id
    data = IdsTestData.new
    ZpiderTreeProcessor.new.recursive_hide_ids data.top_level, ['a'], ['a']
    
    assert_equal data.top_level.blocks, []
  end

  def test_excluded_subsection_in_included_section_is_excluded
    data = IdsTestData.new
    ZpiderTreeProcessor.new.recursive_hide_ids data.top_level, ['a'], ['b']
    
    assert_equal data.top_level.blocks, [data.level_section]
    assert_equal data.level_section.blocks, [data.level_summary]
  end

  def test_include_section_id_makes_other_ids_default_excluded
    data = IdsTestData.new
    ZpiderTreeProcessor.new.recursive_hide_ids data.top_level, ['a'], []
    
    assert_equal data.top_level.blocks, [data.level_section]
    assert_equal data.level_section.blocks, [data.level_summary]
  end

  def test_include_subsection_id_also_includes_parent_id
    data = IdsTestData.new
    value = ZpiderTreeProcessor.new.recursive_hide_ids data.top_level, ['b'], []
    assert_equal value, true
    assert_equal data.top_level.blocks, [data.level_section]
    assert_equal data.level_section.blocks, [data.level_summary, data.level_subsection]
    assert_equal data.level_subsection.blocks, [data.sublevel_summary]
  end

end


class IdsTestData
  attr_accessor :top_level, :level_section, :level_summary, :level_subsection, :sublevel_summary
  attr_accessor :level_subsubsection_3, :level_subsubsection_4, :subsublevel_content_3, :subsublevel_content_4

  def initialize
    @top_level = SectionMock.new title: 'Top Level'

    @level_section = SectionMock.new parent: @top_level, title: 'Level Section', attributes: {'id' => 'a'}, roles: ['level']
    @level_summary = BlockMock.new parent: @level_section

    @level_subsection = SectionMock.new parent: @level_section, title: 'Level Subsection', attributes: {'id' => 'b'}, roles: ['sublevel']
    @sublevel_summary = BlockMock.new parent: @level_subsection

    @level_subsubsection_3 = SectionMock.new parent: @level_subsection, title: 'Level Subsubsection 3', attributes: {'id' => 'c'}, roles: ['subsublevel']
    @subsublevel_content_3 = BlockMock.new parent: @level_subsubsection_3

    @level_subsubsection_4 = SectionMock.new parent: @level_subsection, title: 'Level Subsubsection 4', attributes: {'id' => 'd'}, roles: ['subsublevel']
    @subsublevel_content_4 = BlockMock.new parent: @level_subsubsection_4

    @top_level.blocks = [@level_section]
    @level_section.blocks = [@level_summary, @level_subsection]
    @level_subsection.blocks = [@sublevel_summary, @level_subsubsection_3, @level_subsubsection_4 ]
    @level_subsubsection_3.blocks = [@subsublevel_content_3]
    @level_subsubsection_4.blocks = [@subsublevel_content_4]

  end
end