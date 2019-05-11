require "minitest/autorun"
require_relative '../extension'

class TestListAttribute < Minitest::Test

  def test_list_attribute_splits_on_comma
    attributes = {
        'list' => 'a,b,c'
    }
    actual = list_attribute attributes, 'list'
    assert_equal actual, %w[a b c]
  end

  def test_list_attribute_strips_whitespaces
    attributes = {
        'list' => 'a, b, c '
    }
    actual = list_attribute attributes, 'list'
    assert_equal actual, %w[a b c]
  end

  def test_list_attribute_default_is_empty_list
    attributes = {}
    actual = list_attribute attributes, 'list'
    assert_equal actual, []
  end

  def test_list_attribute_default_can_be_specified
    attributes = {}
    actual = list_attribute attributes, 'list', %w[a b c]
    assert_equal actual, %w[a b c]
  end
end