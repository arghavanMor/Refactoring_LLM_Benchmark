from tqdm import tqdm
from src.generator.scripts.pdf_extractor import fowlerpdf_to_json
from src.generator.scripts.prompt_generator import generate_llm_json, clean_llm_output
from src.generator.scripts.metrics_calculator import combine_runs_into_json
from src.generator.scripts.codebleu_calculator import add_codebleu_to_raw_data
from src.integrator.scripts.integrator_launcher import refact_integrator_launcher, review_refact_integrator_launcher

gpt_api_key_path = "src/generator/OpenAI_key.txt"
deepseek_api_key_path = "src/generator/DeepSeek_key.txt"

fowlerpdf_to_json()

NB_RUNS = 5
GPT_RUN_OUTPUT_PREFIX = "gpt_run#"
DEEPSEEK_RUN_OUTPUT_PREFIX = "ds_run#"

GPT_MODEL_NAME = "gpt-4o-mini"
DEEPSEEK_MODEL_NAME = "deepseek-chat"

for x in tqdm(range(NB_RUNS)):
    gpt_filename = GPT_RUN_OUTPUT_PREFIX + str(x) + ".json"
    ds_filename = DEEPSEEK_RUN_OUTPUT_PREFIX + str(x) + ".json"

    generate_llm_json(filename=gpt_filename, api_key_path=gpt_api_key_path, model_name=GPT_MODEL_NAME)
    generate_llm_json(filename=ds_filename, api_key_path= deepseek_api_key_path, model_name=DEEPSEEK_MODEL_NAME)

    clean_llm_output(filename=gpt_filename)
    clean_llm_output(filename=ds_filename)


refact_integrator_launcher()

combine_runs_into_json(nb_runs=NB_RUNS)

# Set is_fowler_ex to False if applicable.
add_codebleu_to_raw_data(nb_runs=NB_RUNS, is_fowler_ex=True)