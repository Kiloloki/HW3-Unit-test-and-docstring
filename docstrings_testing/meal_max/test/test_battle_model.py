import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal



@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture()
def sample_meal1():
    """Fixture for a sample Meal object."""
    return Meal(id=1, meal='Pizza', price=10.0, cuisine='Italian', difficulty='MED')

@pytest.fixture()
def sample_meal2():
    """Fixture for another sample Meal object."""
    return Meal(id=2, meal='Sushi', price=12.0, cuisine='Japanese', difficulty='HIGH')

@pytest.fixture()
def sample_meal3():
    """Fixture for a third sample Meal object."""
    return Meal(id=3, meal='Burger', price=8.0, cuisine='American', difficulty='LOW')

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a combatant to the BattleModel."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.get_combatants()) == 1
    assert battle_model.get_combatants()[0].meal == 'Pizza'

def test_prep_combatant_full_list(battle_model, sample_meal1, sample_meal2):
    """Test attempting to add a combatant when the list is full."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal3)

def test_battle_not_enough_combatants(battle_model):
    """Test that a battle cannot start with fewer than two combatants."""
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

def test_battle(battle_model, sample_meal1, sample_meal2, mocker):
    """Test the battle logic between two meals."""
    # Prepare combatants
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    # Mocking the random number generation for predictable results
    mock_get_random = mocker.patch("meal_max.utils.random_utils.get_random", return_value=0.1)
    mock_update_meal_stats = mocker.patch("meal_max.models.kitchen_model.update_meal_stats")

    # Run battle
    winner = battle_model.battle()

    # Assert winner is one of the combatants
    assert winner in [sample_meal1, sample_meal2]

    # Assert stats were updated correctly
    mock_update_meal_stats.assert_any_call(sample_meal1.id, 'win')
    mock_update_meal_stats.assert_any_call(sample_meal2.id, 'loss')

def test_clear_combatants(battle_model, sample_meal1, sample_meal2):
    """Test clearing the combatants list."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    assert len(battle_model.get_combatants()) == 2
    battle_model.clear_combatants()
    assert len(battle_model.get_combatants()) == 0

def test_get_battle_score(battle_model, sample_meal1, sample_meal2):
    """Test the battle score calculation for a meal."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    score1 = battle_model.get_battle_score(sample_meal1)
    score2 = battle_model.get_battle_score(sample_meal2)

    assert score1 != score2  # Scores should differ based on meal properties


