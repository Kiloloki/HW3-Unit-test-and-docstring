import pytest
from unittest import mock
from meal_max.models.kitchen_model import Meal, create_meal, delete_meal, get_leaderboard, get_meal_by_id, get_meal_by_name, update_meal_stats, clear_meals

@pytest.fixture
def meal_data():
    """Fixture for a sample meal data."""
    return {
        'meal': 'Pizza',
        'cuisine': 'Italian',
        'price': 10.0,
        'difficulty': 'MED'
    }

@pytest.fixture
def meal():
    """Fixture for a Meal object."""
    return Meal(id=1, meal='Pizza', cuisine='Italian', price=10.0, difficulty='MED')


def test_create_meal(meal_data, mocker):
    """Test creating a meal."""
    mock_get_db_connection = mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock.Mock())
    
    create_meal(**meal_data)
    
    # Ensure that the database insertion was called with the correct values
    mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.execute.assert_called_once_with(
        "INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)",
        (meal_data['meal'], meal_data['cuisine'], meal_data['price'], meal_data['difficulty'])
    )


def test_create_meal_invalid_price(mocker):
    """Test creating a meal with an invalid price."""
    with pytest.raises(ValueError, match="Invalid price: -1. Price must be a positive number."):
        create_meal('Pizza', 'Italian', -1, 'MED')


def test_create_meal_invalid_difficulty(mocker):
    """Test creating a meal with an invalid difficulty."""
    with pytest.raises(ValueError, match="Invalid difficulty level: INVALID. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal('Pizza', 'Italian', 10, 'INVALID')


def test_delete_meal(meal, mocker):
    """Test deleting a meal."""
    mock_get_db_connection = mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock.Mock())
    mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = (False,)
    
    delete_meal(meal.id)

    # Ensure that the meal was marked as deleted
    mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.execute.assert_called_with(
        "UPDATE meals SET deleted = TRUE WHERE id = ?", (meal.id,)
    )


def test_delete_meal_not_found(mocker):
    """Test deleting a meal that does not exist."""
    mock_get_db_connection = mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock.Mock())
    mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        delete_meal(1)


def test_clear_meals(mocker):
    """Test clearing all meals."""
    mock_get_db_connection = mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock.Mock())
    
    clear_meals()
    
    # Ensure that the create table script was executed
    with open("mock_path", "r") as file:
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value.executescript.assert_called_once()


def test_get_leaderboard(mocker):
    """Test retrieving the leaderboard."""
    mock_get_db_connection = mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock.Mock())
    mock_cursor = mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value
    
    # Mock the data returned by the database
    mock_cursor.fetchall.return_value = [
        (1, 'Pizza', 'Italian', 10.0, 'MED', 5, 3, 0.6),
        (2, 'Sushi', 'Japanese', 12.0, 'HIGH', 4, 4, 1.0)
    ]

    leaderboard = get_leaderboard()
    
    assert len(leaderboard) == 2
    assert leaderboard[0]['meal'] == 'Pizza'
    assert leaderboard[1]['meal'] == 'Sushi'


def test_get_meal_by_id(meal, mocker):
    """Test retrieving a meal by ID."""
    mock_get_db_connection = mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock.Mock())
    mock_cursor = mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = (meal.id, meal.meal, meal.cuisine, meal.price, meal.difficulty, False)

    retrieved_meal = get_meal_by_id(meal.id)
    
    assert retrieved_meal.id == meal.id
    assert retrieved_meal.meal == meal.meal


def test_get_meal_by_id_not_found(mocker):
    """Test retrieving a meal by ID that does not exist."""
    mock_get_db_connection = mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock.Mock())
    mock_cursor = mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        get_meal_by_id(1)


def test_get_meal_by_name(meal, mocker):
    """Test retrieving a meal by name."""
    mock_get_db_connection = mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock.Mock())
    mock_cursor = mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = (meal.id, meal.meal, meal.cuisine, meal.price, meal.difficulty, False)

    retrieved_meal = get_meal_by_name(meal.meal)
    
    assert retrieved_meal.id == meal.id
    assert retrieved_meal.meal == meal.meal


def test_get_meal_by_name_not_found(mocker):
    """Test retrieving a meal by name that does not exist."""
    mock_get_db_connection = mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock.Mock())
    mock_cursor = mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with name Pizza not found"):
        get_meal_by_name('Pizza')


def test_update_meal_stats_win(meal, mocker):
    """Test updating meal stats for a win."""
    mock_get_db_connection = mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock.Mock())
    mock_cursor = mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = (False,)

    update_meal_stats(meal.id, 'win')

    mock_cursor.execute.assert_called_with("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (meal.id,))


def test_update_meal_stats_loss(meal, mocker):
    """Test updating meal stats for a loss."""
    mock_get_db_connection = mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock.Mock())
    mock_cursor = mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = (False,)

    update_meal_stats(meal.id, 'loss')

    mock_cursor.execute.assert_called_with("UPDATE meals SET battles = battles + 1 WHERE id = ?", (meal.id,))


def test_update_meal_stats_invalid_result(meal, mocker):
    """Test updating meal stats with an invalid result."""
    with pytest.raises(ValueError, match="Invalid result: INVALID. Expected 'win' or 'loss'."):
        update_meal_stats(meal.id, 'INVALID')
