from typing import Any
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from app.services.quiz_config import TASK_CONFIGURATIONS, SCHEMAS, PROMPT_TEMPLATES
from app.llm_config import MODEL_CONFIGS
from app.services.llm_factory import get_llm_client


def generate_response(task: str, **kwargs: Any) -> Any:
    # 1. Get Task Configuration
    task_config = TASK_CONFIGURATIONS.get(task)
    if not task_config:
        raise ValueError(f"Unknown task: {task}")

    # 2. Retrieve Components based on names in task_config
    schema_name = task_config.get("schema_name")
    model_config_name = task_config.get("model_config_name")
    prompt_template_name = task_config.get("prompt_template_name")
    prompt_input_vars = task_config.get("prompt_input_variables", [])
    default_params = task_config.get("default_params", {})

    schema = SCHEMAS.get(schema_name)
    model_config = MODEL_CONFIGS.get(model_config_name)
    prompt_template_str = PROMPT_TEMPLATES.get(prompt_template_name)

    if not model_config:
        raise ValueError(f"Model configuration '{model_config_name}' not found for task '{task}'.")
    if not prompt_template_str:
        raise ValueError(f"Prompt template '{prompt_template_name}' not found for task '{task}'.")

    # 3. Setup Parser (if schema exists)
    parser = None
    format_instructions = ""
    if schema:
        try:
            parser = PydanticOutputParser(pydantic_object=schema)
            format_instructions = parser.get_format_instructions()
        except Exception as e:
            print(f"Warning: Could not create parser for schema '{schema_name}'. Error: {e}")
            # Decide if you want to raise an error or proceed without parsing
            # raise ValueError(f"Failed to create parser for schema '{schema_name}': {e}") from e

    # 4. Prepare Prompt Inputs
    # Merge default params with provided kwargs, kwargs take precedence
    prompt_inputs = {**default_params, **kwargs}

    # Check if all required input variables (excluding partials) are present
    required_vars = set(prompt_input_vars)
    provided_vars = set(prompt_inputs.keys())
    missing_vars = required_vars - provided_vars
    if missing_vars:
        raise ValueError(f"Missing required input variables for task '{task}', prompt '{prompt_template_name}': {missing_vars}")

    # 5. Create and Format Prompt
    # 'format_instructions' is always provided as a partial variable
    partial_vars = {"format_instructions": format_instructions}
    # Include any other variables from prompt_inputs that are NOT in prompt_input_vars
    # (Though typically, all variables needed by the template string should be listed in prompt_input_vars)
    template_vars = required_vars # Variables expected in the template string itself

    print("creating prompt template")
    prompt = PromptTemplate(
        template=prompt_template_str,
        input_variables=list(template_vars), # Use the list from task config
        partial_variables=partial_vars,
    )
    print("prompt template created")

    try:
        # Only pass the variables listed in prompt_input_vars to the format method
        format_args = {k: v for k, v in prompt_inputs.items() if k in template_vars}
        formatted_prompt = prompt.format(**format_args)
    except KeyError as e:
        raise ValueError(f"Error formatting prompt '{prompt_template_name}'. Input variable mismatch? Missing key: {e}. Provided: {prompt_inputs.keys()}") from e

    # 6. Get LLM Client
    model = get_llm_client(model_config)

    # 7. Invoke LLM
    response = model.invoke(formatted_prompt)
    print("response received")

    raw_content = response.content

    # 8. Parse Output (if parser exists)
    if parser:
        try:
            parsed_output = parser.parse(raw_content)
            print("parsed output")
            return parsed_output
        except Exception as e:
            print(f"Error parsing LLM output for task '{task}' with schema '{schema_name}'. Error: {e}")
            print("Returning raw content instead.")
            return raw_content
    else:
        return raw_content
