def generate_test_case(function_name, context=None):
    """
    Mock LLM generator. Returns a boilerplate pytest template.
    """
    template = f"""import pytest
# Auto-generated tests for {function_name}
# Note: Provide appropriate imports and mocking where necessary.

def test_{function_name}_happy_path():
    # Arrange
    expected_output = "SUCCESS"
    
    # Act
    # result = {function_name}()
    
    # Assert
    # assert result == expected_output
    pass

def test_{function_name}_edge_case():
    # Arrange
    # Configure mock for edge cases
    
    # Act
    # with pytest.raises(ValueError):
    #     {function_name}(invalid_input=True)
    pass
"""
    return template
