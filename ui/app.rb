require 'sinatra'
require 'sinatra/json'
require 'httparty'
require 'json'

def fetch_data(endpoint, params = {})
  url = "http://localhost:8000#{endpoint}"
  response = HTTParty.get(url, query: params, format: :json)

  response.parsed_response
end

get '/' do
  @pedestrian_network = fetch_data('/pedestrian_network')
  @schools = fetch_data('/schools')
  @urban_planning_units = fetch_data('/urban_planning_units')

  erb :index
end

get '/building_accessibility' do
  # http://localhost:4567/building_accessibility?urban_planning_unit_id=21&length_type=length_m&max_distance=1000&k=100&max_amenities=3&f=0.2
  @urban_planning_units = fetch_data('/urban_planning_units')
  @buildings_in_upu = fetch_data('/residential_buildings_with_accessibility_index', params)
  erb :accessibility
end
