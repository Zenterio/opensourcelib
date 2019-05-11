require 'asciidoctor'

require 'yaml'

class YamlConverter
  include Asciidoctor::Converter
  include Asciidoctor::Writer

  register_for 'yaml'

  def initialize backend, opts
    super
    @documents = []
  end

  def convert node, transform = nil
    if node.class <= Array
      node.each.map do |item| convert(item) end
    elsif node.class == Document
      {
          'type' => 'document',
          'file' => node.attributes['docfile'],
          'title' => node.title,
          'blocks' => node.blocks.map do |block| convert(block) end,
      }
    elsif node.class == Block
      {
          'type' => 'block',
          'title' => node.title,
          'caption' => node.caption,
          'content_model' => node.content_model,
          'content' => node.content,
          'blocks' => node.blocks.map do |block| convert(block) end,
      }
    elsif node.class == Section
      {
          'type' => 'section',
          'title' => node.title,
          'caption' => node.caption,
          'section_type' => node.sectname,
          'number' => node.sectnum,
          'blocks' => node.blocks.map do |block| convert(block) end,
      }
    elsif node.class == Inline
      {
          'type' => 'inline',
          'text' => node.text,
          'inline_type' => node.type,
          'target' => node.target,
      }
    elsif node.class == List
      {
          'type' => 'list',
          'title' => node.title,
          'caption' => node.caption,
          'is_outline' => node.outline?,
          'items' => node.items.map do |item| convert(item) end,
      }
    elsif node.class == ListItem
      {
          'type' => 'listitem',
          'title' => node.title,
          'caption' => node.caption,
          'marker' => node.marker,
          'text' => node.text,
          'item_type' => node.simple? ? 'simple' : 'compound',
          'blocks' => node.blocks.map do |block| convert(block) end,
      }
    elsif node.class == Table
      {
           'type' => 'table',
           'title' => node.title,
           'caption' => node.caption,
           'has_header' => node.has_header_option,
           'columns' => node.columns.map do |col| convert(col) end,
           'head_rows' => node.rows.head.map do |row| convert(row) end,
           'body_rows' => node.rows.body.map do |row| convert(row) end,
           'foot_rows' => node.rows.foot.map do |row| convert(row) end,
           'blocks' => node.blocks.map do |block| convert(block) end,
       }
    elsif node.class == Table::Column
      {
          'type' => 'tablecolumn',
      }
    elsif node.class == Table::Cell
      {
          'type' => 'tablecell',
          'text' => node.text,
          'blocks' => node.inner_document != nil ? node.inner_document.blocks.map do |block| convert(block) end : [],
      }
    end
  end

  def write output, target
    File.open(target, "w") do |f|
      f.write(output.to_yaml)
    end
  end
end
