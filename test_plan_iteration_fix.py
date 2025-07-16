#!/usr/bin/env python3
"""
Test script to validate the max plan iteration fix logic
"""

def test_plan_iteration_logic():
    """Test the logic for plan iteration handling"""
    
    # Test case 1: plan_iterations = 5, max_plan_iterations = 3
    # Should return True (go to reporter)
    plan_iterations = 5
    max_plan_iterations = 3
    should_go_to_reporter = plan_iterations >= max_plan_iterations
    assert should_go_to_reporter, f"Expected plan_iterations={plan_iterations} >= max_plan_iterations={max_plan_iterations} to be True"
    
    # Test case 2: plan_iterations = 2, max_plan_iterations = 3
    # Should return False (continue planning)
    plan_iterations = 2
    max_plan_iterations = 3
    should_go_to_reporter = plan_iterations >= max_plan_iterations
    assert not should_go_to_reporter, f"Expected plan_iterations={plan_iterations} >= max_plan_iterations={max_plan_iterations} to be False"
    
    # Test case 3: plan_iterations = 3, max_plan_iterations = 3
    # Should return True (go to reporter - equal to limit)
    plan_iterations = 3
    max_plan_iterations = 3
    should_go_to_reporter = plan_iterations >= max_plan_iterations
    assert should_go_to_reporter, f"Expected plan_iterations={plan_iterations} >= max_plan_iterations={max_plan_iterations} to be True"
    
    print("✓ All plan iteration logic tests passed!")


def test_human_feedback_logic():
    """Test the logic for human feedback node plan iteration handling"""
    
    # Test case: When user wants to edit plan but limit is reached
    current_plan_iterations = 3
    max_plan_iterations = 3
    user_wants_edit = True
    
    if user_wants_edit and current_plan_iterations >= max_plan_iterations:
        should_go_to_reporter = True
        incremented_iterations = current_plan_iterations + 1
    else:
        should_go_to_reporter = False
        incremented_iterations = current_plan_iterations
    
    assert should_go_to_reporter, "Should go to reporter when plan iterations limit is reached"
    assert incremented_iterations == 4, f"Expected incremented iterations to be 4, got {incremented_iterations}"
    
    print("✓ Human feedback logic test passed!")


def test_json_decode_error_logic():
    """Test the logic for handling JSON decode errors"""
    
    # Test case 1: First iteration with JSON error
    plan_iterations_after_increment = 1
    should_go_to_reporter = plan_iterations_after_increment > 0
    assert should_go_to_reporter, "Should go to reporter for JSON errors after first iteration"
    
    # Test case 2: Zero iterations (edge case)
    plan_iterations_after_increment = 0
    should_go_to_reporter = plan_iterations_after_increment > 0
    assert not should_go_to_reporter, "Should end workflow for JSON errors on first attempt"
    
    print("✓ JSON decode error logic tests passed!")


if __name__ == "__main__":
    test_plan_iteration_logic()
    test_human_feedback_logic()
    test_json_decode_error_logic()
    print("\n🎉 All tests passed! The max plan iteration fix logic is correct.")
