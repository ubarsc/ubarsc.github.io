
# To install all the packages locally:

- sudo apt install ruby-rubygems
- bundle install

# To serve locally:

- bundle exec jekyll serve

# To create again with new versions of the packages

- sudo gem install jekyll bundler minima

On Mac, see: https://jekyllrb.com/docs/installation/macos/

# A note about categories

format of the categories tag is:
```
categories: ubarsc <type> <software1> ... <softwareX>
```

'ubarsc' is just to make the path unique (github does funny things if the first category 
matches an existing project).
<type> should be tutorial, update etc
and <software> is the names(s) of the software this relates to
