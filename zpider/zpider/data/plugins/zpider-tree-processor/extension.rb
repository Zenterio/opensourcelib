require 'asciidoctor/extensions' unless RUBY_ENGINE == 'opal'

include Asciidoctor

class ZpiderTreeProcessor < Asciidoctor::Extensions::TreeProcessor
  def process(document)
    levels = create_levels_from_attributes(document.attributes)
    include_ids = list_attribute document.attributes, 'include-ids'
    exclude_ids = list_attribute document.attributes, 'exclude-ids'

    ensure_ids_are_unique document
    recursive_hide_ids document, include_ids, exclude_ids
    recursive_hide document, levels, find_level(document, levels)

    if !document.attributes.key?('keep-all-versions')
      if document.attributes.key?('max-allowed-version')
        version_cap = document.attributes['max-allowed-version']
        highest_versions = find_highest_versions(document, {}, version_cap)
        recursive_hide_versioned_ids(document, highest_versions, version_cap)
      else
        highest_versions = find_highest_versions(document)
        recursive_hide_versioned_ids(document, highest_versions)
      end
    end

    if !document.attributes.key?('keep-empty-sections')
      recursive_remove_empty_sections(document)
    end

    document.reindex_sections
  end

  def create_levels_from_attributes(attributes)
    magic_titles = list_attribute attributes, 'magic-titles'
    levels = {}

    list_attribute(attributes, 'levels-ids').each do |level|
      includes = list_attribute attributes, 'levels-' + level + '-includes', ['all']
      excludes = list_attribute attributes, 'levels-' + level + '-excludes'
      levels[level] = Level.new level, includes, excludes, magic_titles
    end
    levels
  end

  def find_level(section, levels)
    roles = \
      if section.attributes.key? 'docrole'
        section.attributes['docrole']
      else
        section.roles
      end

    if roles.class <= String
      roles = roles.split(' ')
    end

    for role in roles
      if levels.key? role
        return role
      end
    end
    nil
  end

  def ensure_ids_are_unique(block, ids = [], versions = {})
    block.blocks.each do |block|
      if block.class <= Section
        ensure_ids_are_unique block, ids, versions
      end
    end

    if block.attributes.key?('id') && !block.attributes.key?('version')
      if ids.include?(block.attributes['id']) || versions.key?(block.attributes['id'])
        raise 'IDs must be unique. Seen ID ' + block.attributes['id'] + ' multiple times.'
      end
      ids.push(block.attributes['id'])
    end

    if block.attributes.key?('id') && block.attributes.key?('version')
      if ids.include?(block.attributes['id'])
        raise 'Versioned and non-versioned IDs can not be mixed. Mixed use for ID ' + block.attributes['id']
      end
      if versions.key?(block.attributes['id'])
        if versions[block.attributes['id']].include?(block.attributes['version'])
          raise 'ID version numbers must be unique. Seen version ' + block.attributes['version'] +
                ' for ID ' + block.attributes['id'] + ' multiple times'
        else
          versions[block.attributes['id']].push(block.attributes['version'])
        end
      else
        versions[block.attributes['id']] = [block.attributes['version']]
      end
    end
  end

  def find_highest_versions(block, versions = {}, version_cap = nil)
    block.blocks.each do |block|
      if block.class <= Section
        find_highest_versions block, versions, version_cap
      end
    end

    if block.attributes.key?('id') && block.attributes.key?('version')
      seen_version = Gem::Version.new(versions[block.attributes['id']])
      current_version = Gem::Version.new(block.attributes['version'])
      if !versions.key?(block.attributes['id']) || current_version > seen_version
        if !version_cap || current_version <= Gem::Version.new(version_cap)
          versions[block.attributes['id']] = block.attributes['version']
        end
      end
    end

    versions
  end

  def recursive_hide(parent, levels, current_level)
    parent.blocks.delete_if do |block|
      if block.class <= Section
        if find_level(block, levels).nil? && levels.key?(current_level) && levels[current_level].hide_section?(block)
          puts 'Deleting section: ' + block.to_s
          true
        end
      elsif current_level && levels[current_level].hide_block?(block)
        puts 'Deleting block: ' + block.to_s
        true
      end
    end

    parent.blocks.each do |block|
      if block.class <= Section
        level = find_level block, levels
        recursive_hide block, levels, level
      end
    end
  end

  def recursive_hide_ids(block, include_ids, exclude_ids)
    has_included_child = false
    block.blocks.clone.each do |child|
      if child.class <= Section
        has_included_child |= recursive_hide_ids(child, include_ids, exclude_ids)
      end
    end

    current_block_included = !include_ids.empty? &&
        block.attributes.key?('id') &&
        include_ids.include?(block.attributes['id'])

    if block.attributes.key?('id') && exclude_ids.include?(block.attributes['id'])
      block.parent.blocks.delete block
    elsif !include_ids.empty? &&
        block.attributes.key?('id') &&
        !include_ids.include?(block.attributes['id']) &&
        !has_included_child
      block.parent.blocks.delete(block)
    end
    return has_included_child || current_block_included
  end

  def recursive_hide_versioned_ids(block, versions, version_cap = nil)
    block.blocks.clone.each do |child|
      if child.class <= Section
        recursive_hide_versioned_ids(child, versions, version_cap)
      end
    end

    if version_cap && block.attributes.key?('version') &&
       Gem::Version.new(version_cap) < Gem::Version.new(block.attributes['version'])
      block.parent.blocks.delete block
    end

    if block.attributes.key?('id') && block.attributes.key?('version') && versions.key?(block.attributes['id']) &&
       block.attributes['version'] != versions[block.attributes['id']]
      block.parent.blocks.delete block
    end
  end

  def recursive_remove_empty_sections(parent)
    parent.blocks.each do |block|
      if block.class <= Section
        recursive_remove_empty_sections block
      end
    end

    parent.blocks.delete_if do |block|
      if block.class <= Section
        if block.blocks.empty?
          puts 'Deleting empty section: ' + block.to_s
          true
        end
      end
    end
  end
end

def list_attribute attributes, key, default=[]
  if not attributes.key? key
    default
  else
    attributes[key].split(',').map &:strip.downcase
  end
end

class Level
  attr_reader :name, :magic_titles, :includes, :excludes

  def initialize(name, includes, excludes, magic_titles)
    @name = name
    @includes = includes
    @excludes = excludes
    @magic_titles = magic_titles
  end

  def eval_includes(is_magic_title, title_downcase)
    if @includes.include? 'all'
      true
    elsif !is_magic_title
      @includes.include? 'other'
    else
      @includes.include? title_downcase
    end
  end

  def eval_excludes(is_magic_title, title_downcase)
    if @excludes.include? 'all'
      true
    elsif !is_magic_title
      @excludes.include? 'other'
    else
      @excludes.include? title_downcase
    end
  end

  def hide_section?(section)
    title_downcase = section.title.downcase
    is_magic_title = @magic_titles.include? title_downcase
    inc = eval_includes is_magic_title, title_downcase
    exc = eval_excludes is_magic_title, title_downcase

    !inc || exc
  end

  def hide_block?(block)
    if @excludes.include?('all')
      true
    elsif is_summary? block
      if @excludes.include?('summary')
        true
      else
        !(@includes.include?('all') || @includes.include?('summary'))
      end
    else
      if @excludes.include?('other')
        true
      else
        !(@includes.include?('all') || @includes.include?('other'))
      end
    end
  end

  def is_summary?(block)
    block.context == :paragraph && block.parent.blocks.index(block).zero?
  end
end
