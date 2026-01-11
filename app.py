from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
import io
import logging
from openai import OpenAIError, APIError, RateLimitError, APIConnectionError

from llm.generate_synthetic_data import generate_synthetic_data
from llm.augment_existing_data import augment_existing_data
from llm.mask_pii_data import mask_pii_data
from llm.generate_edge_case_data import generate_edge_case_data
from utils.validators import validate_csv_file, validate_csv_content, validate_prompt, sanitize_input
from utils.cache import llm_cache

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG to see more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def landing():
    """Landing page with tool cards"""
    return render_template("landing.html")


@app.route("/data-augmentor")
def data_augmentor():
    """DataAugmentor tool"""
    return render_template("index.html")


@app.route("/file-comparison")
def file_comparison():
    """File Comparison tool"""
    return render_template("file_comparison.html")


@app.route("/code-review")
def code_review():
    """Code Review & Testing Engine"""
    return render_template("code_review.html")


@app.route("/download-review-config")
def download_review_config():
    """Download language-specific code review configuration"""
    import os
    
    language = request.args.get('language', 'python')
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    
    # Languages with detailed configs
    detailed_languages = ['python', 'pyspark', 'sql', 'sparksql']
    
    # Try to load language-specific config
    if language in detailed_languages:
        lang_config_path = os.path.join(config_dir, f'code_review_config_{language}.json')
    else:
        # Use generic config for other languages
        lang_config_path = os.path.join(config_dir, 'code_review_config_generic.json')
    
    if os.path.exists(lang_config_path):
        config_path = lang_config_path
    else:
        # Fall back to default Python config
        config_path = os.path.join(config_dir, 'code_review_config.json')
    
    logger.info(f"Downloading config for language: {language}, using: {os.path.basename(config_path)}")
    return send_file(config_path, as_attachment=True, download_name=f'code_review_config_{language}.json')


@app.route("/analyze-code", methods=["POST"])
def analyze_code():
    """Analyze code and generate tests"""
    try:
        import json
        from utils.code_analyzer import detect_language, parse_notebook, analyze_code_structure
        from llm.code_review_llm import (
            review_code_with_llm,
            generate_unit_tests_with_llm,
            generate_functional_tests_with_llm,
            generate_failure_scenarios_with_llm
        )
        
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file uploaded"}), 400
        
        # Read file content
        filename = file.filename
        selected_language = request.form.get('selected_language', '')
        
        # Use selected language if provided, otherwise detect from file
        if selected_language:
            language = selected_language
            logger.info(f"Using user-selected language: {language}")
        else:
            language = detect_language(filename)
            logger.info(f"Auto-detected language: {language}")
        
        if language == 'unknown':
            return jsonify({"error": f"Unsupported file type: {filename}"}), 400
        
        # Parse content
        content = file.read().decode('utf-8')
        if filename.endswith('.ipynb'):
            code = parse_notebook(content)
        else:
            code = content
        
        # Get options
        review_code = request.form.get('review_code') == 'true'
        generate_unit_tests = request.form.get('generate_unit_tests') == 'true'
        generate_functional_tests = request.form.get('generate_functional_tests') == 'true'
        generate_failure_data = request.form.get('generate_failure_data') == 'true'
        
        # Get custom config if provided
        custom_config = request.form.get('custom_config')
        if custom_config:
            config = json.loads(custom_config)
            logger.info(f"Using custom config for code review")
        
        # Analyze code structure
        structure = analyze_code_structure(code, language)
        
        result = {
            "language": language,
            "filename": filename,
            "structure": structure
        }
        
        # Perform requested analyses
        if review_code:
            logger.info(f"Reviewing {language} code")
            review_response = review_code_with_llm(code, language, filename)
            result["review"] = json.loads(review_response)
        
        if generate_unit_tests:
            logger.info(f"Generating unit tests for {language}")
            result["unit_tests"] = generate_unit_tests_with_llm(
                code, language, structure['test_framework']
            )
        
        if generate_functional_tests:
            logger.info(f"Generating functional tests for {language}")
            result["functional_tests"] = generate_functional_tests_with_llm(
                code, language, structure['test_framework']
            )
        
        if generate_failure_data:
            logger.info(f"Generating failure scenarios for {language}")
            failure_response = generate_failure_scenarios_with_llm(code, language)
            failure_data = json.loads(failure_response)
            result["failure_scenarios"] = failure_data.get("scenarios", [])
        
        logger.info(f"Code analysis completed for {filename}")
        return jsonify(result)
        
    except ValueError as e:
        logger.error(f"Validation error in code analysis: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Unexpected error in code analysis")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/cache/stats")
def cache_stats():
    """Endpoint to view cache statistics."""
    stats = llm_cache.get_stats()
    return jsonify(stats)


@app.route("/compare", methods=["POST"])
def compare():
    """Compare two files"""
    try:
        from utils.file_comparator import compare_files
        
        file1 = request.files.get("file1")
        file2 = request.files.get("file2")
        
        if not file1 or not file2:
            return jsonify({"error": "Both files are required"}), 400
        
        # Read file contents
        file1_content = file1.read().decode('utf-8')
        file2_content = file2.read().decode('utf-8')
        
        # Compare files
        result = compare_files(file1.filename, file2.filename, file1_content, file2_content)
        
        logger.info(f"Compared {file1.filename} and {file2.filename}")
        return jsonify(result)
        
    except ValueError as e:
        logger.error(f"Validation error in file comparison: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Unexpected error in file comparison")
        return jsonify({"error": f"Comparison failed: {str(e)}"}), 500



@app.route("/process", methods=["POST"])
def process():
    action = request.form.get("action")
    prompt = request.form.get("prompt", "")
    file = request.files.get("file")

    logger.info(f"Processing request - Action: {action}")

    try:
        # Map frontend action names to backend action names
        action_map = {
            "generate_synthetic_data": "generate",
            "augment_existing_data": "augment",
            "mask_pii_data": "mask",
            "generate_edge_case_data": "edge",
            # Also accept short names directly
            "generate": "generate",
            "augment": "augment",
            "mask": "mask",
            "edge": "edge"
        }
        
        # Validate and map action
        if not action or action not in action_map:
            logger.warning(f"Invalid action: {action}")
            return jsonify({
                "error": f"Invalid action. Must be one of: generate_synthetic_data, augment_existing_data, mask_pii_data, generate_edge_case_data"
            }), 400
        
        action = action_map[action]

        # Handle different actions
        if action == "generate":
            # Validate prompt
            prompt = sanitize_input(prompt)
            is_valid, error_msg = validate_prompt(prompt)
            if not is_valid:
                logger.warning(f"Invalid prompt: {error_msg}")
                return jsonify({"error": error_msg}), 400

            logger.info("Generating synthetic data")
            df_out = generate_synthetic_data(prompt)

        elif action in ["augment", "mask", "edge"]:
            # Validate file upload
            is_valid, error_msg = validate_csv_file(file)
            if not is_valid:
                logger.warning(f"Invalid file: {error_msg}")
                return jsonify({"error": error_msg}), 400

            # Validate CSV content
            df, error_msg = validate_csv_content(file)
            if df is None:
                logger.warning(f"Invalid CSV content: {error_msg}")
                return jsonify({"error": error_msg}), 400

            logger.info(f"Processing CSV with {len(df)} rows and {len(df.columns)} columns")

            # Execute action
            if action == "augment":
                logger.info("Augmenting existing data")
                # Get number of rows to add (default: 10)
                augment_row_count = request.form.get("augment_row_count", "10")
                try:
                    num_rows = int(augment_row_count)
                    num_rows = max(1, min(num_rows, 100))  # Clamp between 1 and 100
                except ValueError:
                    num_rows = 10
                logger.info(f"Adding {num_rows} new rows")
                df_out = augment_existing_data(df, num_rows=num_rows)
            elif action == "mask":
                logger.info("Masking PII data")
                df_out = mask_pii_data(df)
            elif action == "edge":
                logger.info("Generating edge case data")
                # Get number of edge cases to generate (default: 10)
                edge_case_row_count = request.form.get("edge_case_row_count", "10")
                try:
                    num_rows = int(edge_case_row_count)
                    num_rows = max(1, min(num_rows, 50))  # Clamp between 1 and 50
                except ValueError:
                    num_rows = 10
                logger.info(f"Generating {num_rows} edge cases")
                df_out = generate_edge_case_data(df, num_rows=num_rows)

        # Convert to CSV for download
        buffer = io.StringIO()
        df_out.to_csv(buffer, index=False)
        buffer.seek(0)

        logger.info(f"Successfully processed request - Output: {len(df_out)} rows")

        return send_file(
            io.BytesIO(buffer.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name="output.csv"
        )

    except RateLimitError as e:
        logger.error(f"Rate limit error: {str(e)}")
        return jsonify({
            "error": "API rate limit exceeded. Please try again in a few moments."
        }), 429

    except APIConnectionError as e:
        logger.error(f"API connection error: {str(e)}")
        return jsonify({
            "error": "Failed to connect to AI service. Please check your internet connection and try again."
        }), 503

    except APIError as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            "error": f"AI service error: {str(e)}"
        }), 502

    except OpenAIError as e:
        logger.error(f"OpenAI error: {str(e)}")
        return jsonify({
            "error": f"AI service error: {str(e)}"
        }), 500

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 400

    except pd.errors.ParserError as e:
        logger.error(f"CSV parsing error: {str(e)}")
        return jsonify({
            "error": f"Failed to parse CSV file: {str(e)}"
        }), 400

    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


if __name__ == "__main__":
    logger.info("Starting DataAugmentor application")
    app.run(debug=True)

