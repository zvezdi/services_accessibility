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
  default_params = {
    'urban_planning_unit_id' => '273',
    'length_type' => 'length_m',
    'max_distance' => '1000',
    'k' => '200',
    'max_amenities' => '3',
    'f' => '0.5'
  }

  if params.empty?
    redirect to("/building_accessibility?#{URI.encode_www_form(default_params)}")
  end

  # Override default values with parameters from the request if present
  merged_params = default_params.merge(params)

  @colors = ['maroon', 'chocolate', 'orange', 'gold', 'yellowgreen', 'forestgreen', 'darkgreen']
  @show_legend = true

  @urban_planning_units = fetch_data('/urban_planning_units')
  @buildings_in_upu = fetch_data('/residential_buildings_with_accessibility_index', merged_params)

  erb :accessibility
end

get '/precomputed_building_accessibility' do
  # http://localhost:4567/precomputed_building_accessibility?length_type=length_m&max_distance=1000&k=300&max_amenities=3&f=0.5
  default_params = {
    'length_type' => 'length_m',
    'max_distance' => '1000',
    'k' => '300',
    'max_amenities' => '3',
    'f' => '0.5'
  }

  if params.empty?
    redirect to("/precomputed_building_accessibility?#{URI.encode_www_form(default_params)}")
  end

  # Override default values with parameters from the request if present
  merged_params = default_params.merge(params)

  @colors = ['maroon', 'chocolate', 'orange', 'gold', 'yellowgreen', 'forestgreen', 'darkgreen']
  @show_legend = true

  @urban_planning_units = fetch_data('/urban_planning_units')
  @buildings = fetch_data('/precomputed_residential_accessibility_index', merged_params)

  erb :precomputed_accessibility
end

