from flask import Flask, render_template, request
import random
import os
import tempfile
import shutil
import urllib.request
import zipfile
from urllib.error import HTTPError
from risk.identifier import analyze_complexity
from defect.predictor import predict_defect_probability
from optimization.selector import select_regression_tests
from generation.generator import generate_test_case

app = Flask(__name__)

def download_and_extract_repo(repo_url, extract_to):
    """Fallback to download zip since Git might not be installed."""
    base_url = repo_url
    if base_url.endswith('.git'):
        base_url = base_url[:-4]
    
    zip_urls = [
        f"{base_url}/archive/refs/heads/main.zip",
        f"{base_url}/archive/refs/heads/master.zip"
    ]
    
    zip_path = os.path.join(extract_to, "repo.zip")
    success = False
    
    for z_url in zip_urls:
        try:
            req = urllib.request.Request(z_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            success = True
            break
        except Exception as e:
            continue
            
    if not success:
        raise Exception("Could not download repository zip (tried main and master branches).")
        
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

@app.route("/", methods=["GET", "POST"])
def index():
    default_repo = "https://github.com/pallets/flask.git"
    repo_url = request.form.get("repo_url", default_repo)
    
    # Defaults in case of error or before run
    pr_data = {
        "title": repo_url.split('/')[-1].replace('.git', '') if repo_url else "No Repo",
        "description": f"Analyzing repository: {repo_url}",
        "churn": 0
    }
    risk_results = []
    defect_prob = 0
    optimization_stats = {"savings_pct": 0, "total_tests": 0, "selected_tests": 0, "tests_to_run": []}
    generated_tests = []
    error_msg = None

    if request.method == "POST" and repo_url:
        temp_dir = tempfile.mkdtemp()
        try:
            # Download and extract the repository zip
            download_and_extract_repo(repo_url, temp_dir)
            
            # Find up to 20 python files
            py_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.py'):
                        py_files.append(os.path.join(root, file))
                        if len(py_files) >= 20:
                            break
                if len(py_files) >= 20:
                    break
            
            # Process Pillars
            raw_code = ""
            for pf in py_files:
                try:
                    with open(pf, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(raw_code) + len(content) < 50000: # Limit to 50k chars
                            raw_code += content + "\n\n"
                except:
                    pass
            
            relative_files = [os.path.relpath(f, temp_dir) for f in py_files]
            
            # 1. Risk
            risk_results = analyze_complexity(raw_code)
            
            # 2. Defect Prediction
            avg_complexity = 0
            if risk_results and "error" not in risk_results[0]:
                # Sort and take top 10 most complex to save display space and execution time of generator
                risk_results = sorted(risk_results, key=lambda x: x.get('complexity', 0), reverse=True)[:10]
                avg_complexity = sum(r.get('complexity', 0) for r in risk_results) / len(risk_results)
            
            pr_data["churn"] = len(py_files) * 5 # Mocking churn based on file count
            defect_prob = predict_defect_probability({
                "churn": pr_data["churn"],
                "complexity": avg_complexity
            })
            
            # 3. Optimization
            if relative_files:
                optimization_stats = select_regression_tests(relative_files)
            
            # 4. Generation
            if risk_results and "error" not in risk_results[0]:
                for res in risk_results:
                    if res.get('risk') in ['High', 'Moderate']: # Only generate for complex ones
                        generated_tests.append({
                            "function": res['function'],
                            "code": generate_test_case(res['function'])
                        })
                    if len(generated_tests) >= 5: # Limit generated tests
                        break
                        
        except Exception as e:
            error_msg = f"Error analyzing repository: {str(e)}"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    return render_template("index.html", 
        repo_url=repo_url,
        pr_data=pr_data,
        risk_results=risk_results,
        defect_prob=defect_prob * 100,
        optimization_stats=optimization_stats,
        generated_tests=generated_tests,
        error_msg=error_msg
    )

if __name__ == "__main__":
    app.run(debug=True, port=8000)
