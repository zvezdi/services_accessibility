require 'sinatra'
require 'sinatra/json'
require 'httparty'
require 'json'

def fetch_data(endpoint)
  response = HTTParty.get("http://localhost:8000#{endpoint}")
  response.parsed_response
end

get '/' do
  @pedestrian_network = fetch_data('/pedestrian_network')
  @schools = fetch_data('/schools')
  @urban_planning_units = fetch_data('/urban_planning_units')
  erb :index
end
