require "minitest/autorun"
require_relative '../extension'
require_relative './utils'

class TestFindLevel < Minitest::Test
  def setup
    @levels = {'level' => Level.new('level', [], [], [])}
  end

  def test_level_can_be_retrieved_from_single_value_docrole_attribute
    block = BlockMock.new attributes: {'docrole' => 'level'}
    assert_equal ZpiderTreeProcessor.new.find_level(block, @levels), 'level'
  end

  def test_level_can_be_retrieved_from_multiple_value_docrole_attribute
    block = BlockMock.new attributes: {'docrole' => 'other level other2'}
    assert_equal ZpiderTreeProcessor.new.find_level(block, @levels), 'level'
  end

  def test_level_can_be_retrieved_from_string_single_value_role
    block = BlockMock.new roles: 'level'
    assert_equal ZpiderTreeProcessor.new.find_level(block, @levels), 'level'
  end

  def test_level_can_be_retrieved_from_string_multiple_value_role
    block = BlockMock.new roles: 'other level other2'
    assert_equal ZpiderTreeProcessor.new.find_level(block, @levels), 'level'
  end

  def test_level_can_be_retrieved_from_array_role
    block = BlockMock.new roles: %w[other level other2]
    assert_equal ZpiderTreeProcessor.new.find_level(block, @levels), 'level'
  end

  def test_level_not_found_returns_nil
    block = BlockMock.new
    assert_equal ZpiderTreeProcessor.new.find_level(block, @levels), nil
  end
end
