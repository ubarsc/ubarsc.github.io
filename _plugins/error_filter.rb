module Jekyll
  module ExceptionFilter
    def raise_error(msg)
      current_file = @context.registers[:page]['path'] rescue "Unknown file"
      raise "Jekyll Build Error [#{current_file}]: #{msg}"
    end
  end
end

Liquid::Template.register_filter(Jekyll::ExceptionFilter)
