require "minitest/autorun"
require_relative '../extension'
require_relative './utils'

class TestRecursiveHide < Minitest::Test

  def setup
    $stdout = StringIO.new
  end

  def test_exclude_all_on_level
    data = DocumentData.new(['all'], ['all'])
    ZpiderTreeProcessor.new.recursive_hide data.parent, data.levels, data.level_name

    assert_equal data.parent.blocks, [data.sublevel_section]
  end

  def test_exclude_summary_on_level
    data = DocumentData.new(['all'], ['summary'])
    ZpiderTreeProcessor.new.recursive_hide data.parent, data.levels, data.level_name

    assert_equal data.parent.blocks, [data.other_paragraph, data.magic_title_section, data.sublevel_section, data.other_section]
  end

  def test_exclude_other_on_level
    data = DocumentData.new(['all'], ['other'])
    ZpiderTreeProcessor.new.recursive_hide data.parent, data.levels, data.level_name

    assert_equal data.parent.blocks, [data.summary, data.magic_title_section, data.sublevel_section]
  end

  def test_exclude_magictitle_on_level
    data = DocumentData.new(['all'], ['magictitle'])
    ZpiderTreeProcessor.new.recursive_hide data.parent, data.levels, data.level_name

    assert_equal data.parent.blocks, [data.summary, data.other_paragraph, data.sublevel_section, data.other_section]
  end

  def test_include_summary_on_level
    data = DocumentData.new(['summary'], [])
    ZpiderTreeProcessor.new.recursive_hide data.parent, data.levels, data.level_name

    assert_equal data.parent.blocks, [data.summary, data.sublevel_section]
  end

  def test_include_other_on_level
    data = DocumentData.new(['other'], [])
    ZpiderTreeProcessor.new.recursive_hide data.parent, data.levels, data.level_name

    assert_equal data.parent.blocks, [data.other_paragraph, data.sublevel_section, data.other_section]
  end

  def test_include_magictitle_on_level
    data = DocumentData.new(['magictitle'], [])
    ZpiderTreeProcessor.new.recursive_hide data.parent, data.levels, data.level_name

    assert_equal data.parent.blocks, [data.magic_title_section, data.sublevel_section]
  end

  def test_recursive_hide_performed_on_sublevel
    data = DocumentData.new(['all'], ['all'])
    ZpiderTreeProcessor.new.recursive_hide data.parent, data.levels, data.level_name

    assert_equal data.sublevel_section.blocks, []
  end
end


class DocumentData
  attr_accessor :summary, :other_paragraph, :magic_title_section, :sublevel_section, :other_section
  attr_accessor :level_name, :levels, :parent

  def initialize(includes, excludes)
    @parent = BlockMock.new

    @summary = BlockMock.new parent: @parent
    @other_paragraph = BlockMock.new parent: @parent
    @magic_title_section = SectionMock.new parent: @parent, title: 'MagicTitle'
    @sublevel_section = SectionMock.new parent: @parent, roles: ['sublevel']
    @other_section = SectionMock.new parent: @parent
    @parent.blocks = [@summary, @other_paragraph, @magic_title_section, @sublevel_section, @other_section]

    @sublevel_summary = BlockMock.new parent: @sublevel_section
    @sublevel_section.blocks = [@sublevel_summary]

    @level_name = 'level'
    @levels = {
      @level_name => Level.new(@level_name, includes, excludes, ['magictitle']),
      'sublevel' => Level.new('sublevel', [], [], []),
    }
  end
end