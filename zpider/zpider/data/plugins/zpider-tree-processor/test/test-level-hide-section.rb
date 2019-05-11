require "minitest/autorun"
require_relative '../extension'
require_relative './utils'

class TestLevelHideSection < Minitest::Test
  def setup
    @data = TestData.new
  end

  def test_hide_other_if_exclude_all
    assert @data.exclude_all_level.hide_section? @data.section
  end

  def test_hide_other_if_exclude_other
    assert @data.exclude_other_level.hide_section? @data.section
  end

  def test_do_not_hide_other_if_include_all
    assert !@data.include_all_level.hide_section?(@data.section)
  end

  def test_do_not_hide_other_if_include_other
    assert !@data.include_other_level.hide_section?(@data.section)
  end

  def test_hide_magic_if_exclude_all
    assert @data.exclude_all_level.hide_section? @data.magic_section
  end

  def test_hide_magic_if_exclude_magic_title
    assert @data.exclude_magic_level.hide_section? @data.magic_section
  end

  def test_do_not_hide_not_magic_if_exclude_magic_title
    assert !@data.exclude_magic_level.hide_section?(@data.section)
  end

  def test_do_not_hide_magic_if_include_all
    assert !@data.include_all_level.hide_section?(@data.magic_section)
  end

  def test_do_not_hide_other_if_include_magic_title
    assert !@data.include_magic_level.hide_section?(@data.magic_section)
  end

end