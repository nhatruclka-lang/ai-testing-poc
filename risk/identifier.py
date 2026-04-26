from radon.complexity import cc_visit
import ast

def analyze_complexity(code_string):
    """
    Parses python code and determines cyclomatic complexity using Radon.
    Returns a list of functions and their complexity scores.
    """
    try:
        blocks = cc_visit(code_string)
        results = []
        for block in blocks:
            # block has .name, .complexity, .lineno, etc.
            risk_level = "High" if block.complexity > 10 else "Moderate" if block.complexity > 5 else "Low"
            results.append({
                "function": block.name,
                "complexity": block.complexity,
                "risk": risk_level
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]
