require "minitest/autorun"
require_relative '../extension'
require_relative './utils'

class TestCreateLevelsFromAttributes < Minitest::Test

  def test_magic_titles_added_to_all_levels
    levels = ZpiderTreeProcessor.new.create_levels_from_attributes(
      'levels-ids' => 'level,sublevel',
      'magic-titles' => 'm1,m2'
    )

    assert_equal levels['level'].magic_titles, %w[m1 m2]
    assert_equal levels['sublevel'].magic_titles, %w[m1 m2]
  end

  def test_includes_attributes_handled_for_all_levels
    levels = ZpiderTreeProcessor.new.create_levels_from_attributes(
      'levels-ids' => 'level,sublevel',
      'levels-level-includes' => 'i1,i2',
      'levels-sublevel-includes' => 'i3,i4'
    )

    assert_equal levels['level'].includes, %w[i1 i2]
    assert_equal levels['sublevel'].includes, %w[i3 i4]
  end

  def test_excludes_attributes_handled_for_all_levels
    levels = ZpiderTreeProcessor.new.create_levels_from_attributes(
      'levels-ids' => 'level,sublevel',
      'levels-level-excludes' => 'e1,e2',
      'levels-sublevel-excludes' => 'e3,e4'
    )

    assert_equal levels['level'].excludes, %w[e1 e2]
    assert_equal levels['sublevel'].excludes, %w[e3 e4]
  end
end
