require "minitest/autorun"
require_relative '../extension'
require_relative './utils'

class TestRecursiveHideIds < Minitest::Test

  def setup
    $stdout = StringIO.new

    # Minitest captures stdout and stderr by default and we don't know how to stop it from doing so.
    # As a workaround, a user can do something like this to get stdout and stderr printed to the console:
    #
    # assert_equal $stdout.string, "abc"
  end

  def test_find_highest_versions_with_no_versions_present
    data = NonVersionedTestData.new
    max_versions = ZpiderTreeProcessor.new.find_highest_versions data.top_level

    assert_equal max_versions, {}
  end

  def test_find_highest_versions_with_versions_present
    data = VersionedIdsTestData.new
    max_versions = ZpiderTreeProcessor.new.find_highest_versions data.top_level

    assert_equal max_versions, {'a' => '0.2'}
  end

  def test_max_versions_can_be_capped
    data = VersionedIdsTestData.new
    max_versions = ZpiderTreeProcessor.new.find_highest_versions data.top_level, {}, '0.1'

    assert_equal max_versions, {'a' => '0.1'}
  end

  def test_everything_is_included_if_no_version_is_specified
    data = VersionedIdsTestData.new
    ZpiderTreeProcessor.new.recursive_hide_versioned_ids data.top_level, {}

    assert_equal data.top_level.blocks, [data.feature_a_level]
    assert_equal data.feature_a_level.blocks, [data.feature_a_version_0_2_sublevel, data.feature_a_version_0_1_sublevel]
    assert_equal data.feature_a_version_0_1_sublevel.blocks, [data.feature_a_version_0_1_sublevel_content]
    assert_equal data.feature_a_version_0_2_sublevel.blocks, [data.feature_a_version_0_2_sublevel_content]
  end

  def test_only_specified_version_included
    data = VersionedIdsTestData.new
    ZpiderTreeProcessor.new.recursive_hide_versioned_ids data.top_level, {'a' => '0.1'}

    assert_equal data.top_level.blocks, [data.feature_a_level]
    assert_equal data.feature_a_level.blocks, [data.feature_a_version_0_1_sublevel]
    assert_equal data.feature_a_version_0_1_sublevel.blocks, [data.feature_a_version_0_1_sublevel_content]
  end
end

class NonVersionedTestData
  attr_accessor :top_level
  attr_accessor :feature_a_level
  attr_accessor :feature_a_version_0_1_sublevel, :feature_a_version_0_1_sublevel_content

  def initialize
    @top_level = SectionMock.new title: 'Top Level'

    @feature_a_level = SectionMock.new parent: @top_level, title: 'Feature A', roles: ['level']

    @feature_a_sublevel = SectionMock.new parent: @feature_a_level, title: 'Feature A', attributes: {'id' => 'a'}, roles: ['sublevel']
    @feature_a_sublevel_content = BlockMock.new parent: @feature_a_sublevel

    @top_level.blocks = [@feature_a_level]
    @feature_a_level.blocks = [@feature_a_sublevel]
  end
end

class VersionedIdsTestData
  attr_accessor :top_level
  attr_accessor :feature_a_level
  attr_accessor :feature_a_version_0_2_sublevel, :feature_a_version_0_2_sublevel_content
  attr_accessor :feature_a_version_0_1_sublevel, :feature_a_version_0_1_sublevel_content

  def initialize
    @top_level = SectionMock.new title: 'Top Level'

    @feature_a_level = SectionMock.new parent: @top_level, title: 'Feature A', roles: ['level']

    @feature_a_version_0_2_sublevel = SectionMock.new parent: @feature_a_level, title: 'Feature A (version 0.2)', attributes: {'id' => 'a', 'version' => '0.2'}, roles: ['sublevel']
    @feature_a_version_0_2_sublevel_content = BlockMock.new parent: @feature_a_version_0_2_sublevel

    @feature_a_version_0_1_sublevel = SectionMock.new parent: @feature_a_level, title: 'Feature A (version 0.1)', attributes: {'id' => 'a', 'version' => '0.1'}, roles: ['sublevel']
    @feature_a_version_0_1_sublevel_content = BlockMock.new parent: @feature_a_version_0_1_sublevel

    @top_level.blocks = [@feature_a_level]
    @feature_a_level.blocks = [@feature_a_version_0_2_sublevel, @feature_a_version_0_1_sublevel]
    @feature_a_version_0_1_sublevel.blocks = [@feature_a_version_0_1_sublevel_content]
    @feature_a_version_0_2_sublevel.blocks = [@feature_a_version_0_2_sublevel_content]

  end
end