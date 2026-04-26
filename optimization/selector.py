def select_regression_tests(changed_files):
    """
    Mock regression test selector.
    In reality, this would use pytest-testmon or an AST map to find dependencies.
    """
    # Dummy logic to calculate fake savings
    total_tests = 582
    selected_tests = max(10, len(changed_files) * 5)
    savings_pct = (1 - (selected_tests / total_tests)) * 100
    
    selected_names = [f"test_{f.split('.')[0]}_{i}" for f in changed_files for i in range(1, 6)]
    
    return {
        "total_tests": total_tests,
        "selected_tests": selected_tests,
        "savings_pct": savings_pct,
        "tests_to_run": selected_names
    }
