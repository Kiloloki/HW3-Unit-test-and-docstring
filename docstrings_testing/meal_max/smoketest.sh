#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Meal Management
#
##########################################################

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Creating meal: $meal, $cuisine, $price, $difficulty..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Meal created successfully."
  else
    echo "Failed to create meal."
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

##########################################################
#
# Battle Management
#
##########################################################

prep_combatant() {
  meal_name=$1

  echo "Preparing combatant: $meal_name..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" -d "{\"meal\":\"$meal_name\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatant prepared successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to prepare combatant."
    exit 1
  fi
}

battle() {
  echo "Initiating battle..."
  response=$(curl -s -X GET "$BASE_URL/battle")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle completed successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to complete battle."
    exit 1
  fi
}

##########################################################
#
# Leaderboard
#
##########################################################

get_leaderboard() {
  echo "Getting leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve leaderboard."
    exit 1
  fi
}

##########################################################
#
# Test Execution
#
##########################################################

# Health checks
check_health
check_db

# Create a meal
create_meal "Pizza" "Italian" 12.99 "MED"
create_meal "Sushi" "Japanese" 15.99 "HIGH"

# Get a meal by ID (assuming ID 1 exists)
get_meal_by_id 1

# Battle: Prepare and initiate a battle
prep_combatant "Pizza"
prep_combatant "Sushi"
battle

# Get the leaderboard
get_leaderboard

# Clean up: Delete a meal
delete_meal_by_id 1

echo "All tests passed successfully!"
