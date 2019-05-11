require "minitest/autorun"
require_relative '../extension'
require_relative './utils'

class TestLevelIsSummary < Minitest::Test

  def setup
    @data = TestData.new
  end

  def test_is_summary_is_true_if_paragraph_and_has_index_0
    assert @data.include_all_level.is_summary?(@data.summary)
  end

  def test_is_summary_is_false_if_block_is_not_paragraph
    assert !@data.include_all_level.is_summary?(@data.section)
  end

  def test_is_summary_is_false_if_block_does_not_have_index_0
    assert !@data.include_all_level.is_summary?(@data.second_paragraph)
  end
end