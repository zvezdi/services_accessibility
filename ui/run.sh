bundle install
npm run build:css
bundle exec rerun 'rackup config.ru -p 4567'