require "minitest/autorun"
require_relative '../extension'
require_relative './utils'

class TestLevelHideBlock < Minitest::Test

  def setup
    @data = TestData.new
  end

  def test_hide_summary_if_exclude_all
    assert @data.exclude_all_level.hide_block? @data.summary
  end

  def test_hide_summary_if_exclude_summary
    assert @data.exclude_all_level.hide_block? @data.summary
  end

  def test_do_not_hide_summary_if_include_all
    assert !@data.include_all_level.hide_block?(@data.summary)
  end

  def test_do_not_hide_summary_if_include_summary
    assert !@data.include_summary_level.hide_block?(@data.summary)
  end

  def test_hide_summary_if_include_does_not_contain_summary_or_all
    assert @data.include_other_level.hide_block?(@data.summary)
  end

  def test_hide_other_if_exclude_all
    assert @data.exclude_all_level.hide_block? @data.second_paragraph
  end

  def test_hide_other_if_exclude_other
    assert @data.exclude_all_level.hide_block? @data.second_paragraph
  end

  def test_do_not_hide_other_if_include_all
    assert !@data.include_all_level.hide_block?(@data.second_paragraph)
  end

  def test_do_not_hide_other_if_include_other
    assert !@data.include_other_level.hide_block?(@data.second_paragraph)
  end

  def test_hide_other_if_include_does_not_contain_other_or_all
    assert @data.include_summary_level.hide_block?(@data.second_paragraph)
  end
end
