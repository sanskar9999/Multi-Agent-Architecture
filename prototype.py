import anthropic
import re
import time

client = anthropic.Anthropic(api_key="YOUR_KEY_HERE")
MODEL_NAME = "claude-3-haiku-20240307"
MAX_TOKEN = 800

def extract_between_tags(tag, string, strip=False):
    ext_list = re.findall(fr"<{tag}>(.+?)</{tag}>", string, re.DOTALL)
    if strip:
        ext_list = [e.strip() for e in ext_list]
    return ext_list

def construct_system_prompt(agent_name, agent_prompt):
    return f"System Prompt: {agent_prompt}\nYou are the {agent_name} Agent."

def construct_agent_prompt(agent_name, agent_input):
    return f"You are the {agent_name} Agent. {agent_input}"

problem_definer_prompt = construct_system_prompt("Problem Definer", "Your role is to understand the problem statement provided by the user and clarify any ambiguities through clarifying questions.")
decomposer_prompt = construct_system_prompt("Decomposer", "Your task is to break down the problem into specific subtasks related to the problem statement provided by the Problem Definer Agent.")
generator_prompt = construct_system_prompt("Generator", "Based on the subtasks provided by the Decomposer Agent, generate prompts for the Worker Agents to write Python code or provide solutions for those specific subtasks.")
worker_prompt = construct_system_prompt("Worker", "You are a Worker Agent tasked with writing Python code or providing a solution for the specific subtask assigned to you by the Generator Agent. Follow the prompt provided and do not deviate from the assigned task. EXAMPLE: <worker_prompt>Prompt for the Worker Agent:</worker_prompt><worker_prompt>Given the following system of linear equations:\n\n2x + 5y = 0\n3x - 2y = 0\n\nWrite a Python function to solve this system of linear equations and find the value(s) of x and y. The function should return a tuple containing the values of x and y, or None if no solution exists.\n\nYou can use any appropriate method to solve the system, such as Gaussian elimination, substitution, or elimination.\n\nHere's an example of how the function should be structured:\n\ndef solve_linear_system():\n    # Your code to solve the system of linear equations\n    # ...\n\n    # If a solution exists, return a tuple (x, y)\n    # Otherwise, return None\n\n    return (x, y)\n</worker_prompt>")
compiler_prompt = construct_system_prompt("Compiler", "Your role is to combine the solutions provided by the Worker Agents into a unified final solution without introducing any new content or solutions.")
tester_prompt = construct_system_prompt("Tester", "Test the final solution provided by the Compiler Agent against the original problem statement and provide clear feedback on its correctness and completeness.")
error_identifier_prompt = construct_system_prompt("Error Identifier", "Based on the feedback from the Tester Agent, identify and categorize any missing components, errors, or flaws in the final solution in detail.")
editor_prompt = construct_system_prompt("Editor", "Based on the detailed feedback from the Error Identifier, suggest specific improvements or additions to the workflow or the final solution to address the identified issues.")

def solve_problem(user_prompt, delay=2, max_iterations=10):
    problem_solved = False
    iteration = 1
    revised_problem_statement = user_prompt
    conversation_history = ""

    while not problem_solved and iteration <= max_iterations:
        print(f"Iteration {iteration}:")

        # Step 1: Problem Definer Agent
        problem_definer_messages = [{"role": "user", "content": construct_agent_prompt("Problem Definer", revised_problem_statement)}]
        problem_definition = client.messages.create(model=MODEL_NAME, max_tokens=MAX_TOKEN, messages=problem_definer_messages, system=problem_definer_prompt).content[0].text
        print("Problem Definer Output:")
        print(problem_definition)
        time.sleep(delay)
        revised_problem_statement = problem_definition
        conversation_history += "\n" + problem_definition

        # Step 2: Decomposer Agent
        decomposer_messages = [{"role": "user", "content": construct_agent_prompt("Decomposer", f"Based on the problem definition provided by the Problem Definer Agent, decompose the problem into smaller subtasks.\n\n{conversation_history}")}]
        subtasks = client.messages.create(model=MODEL_NAME, max_tokens=MAX_TOKEN, messages=decomposer_messages, system=decomposer_prompt).content[0].text
        print("\nDecomposer Output:")
        print(subtasks)
        time.sleep(delay)
        conversation_history += "\n" + subtasks

        # Step 3: Generator Agent
        generator_messages = [{"role": "user", "content": construct_agent_prompt("Generator", f"Based on the subtasks provided by the Decomposer Agent, generate prompts for the Worker Agents to write Python code or provide solutions for those specific subtasks.\n\n{conversation_history}")}]
        worker_prompts = client.messages.create(model=MODEL_NAME, max_tokens=MAX_TOKEN, messages=generator_messages, system=generator_prompt).content[0].text
        print("\nGenerator Output:")
        print(worker_prompts)
        time.sleep(delay)
        conversation_history += "\n" + worker_prompts

        # Step 4: Worker Agents
        worker_solutions = []
        for worker_prompt in extract_between_tags("worker_prompt", worker_prompts):
            worker_messages = [{"role": "user", "content": construct_agent_prompt("Worker", worker_prompt, conversation_history)}]
            worker_solution = client.messages.create(model=MODEL_NAME, max_tokens=MAX_TOKEN, messages=worker_messages, system=worker_prompt).content[0].text
            print(f"\nWorker Agent Output for Task '{worker_prompt}':")
            print(worker_solution)

            # Check if the Worker Agent provided a valid solution
            if "Unable to provide a solution" in worker_solution or worker_solution.strip() == "":
                print("Worker Agent unable to provide a solution for this task. Skipping to the next task.")
                continue
            elif "Clarification needed" in worker_solution:
                # Implement a mechanism for the Worker Agent to request clarification
                # and collaborate with other agents to resolve the issue
                pass

            worker_solutions.append(worker_solution)
            conversation_history += f"\nWorker Agent Output for Task '{worker_prompt}':\n{worker_solution}"
            time.sleep(delay)

        # Step 5: Compiler Agent
        compiler_messages = [{"role": "user", "content": construct_agent_prompt("Compiler", f"Combine the solutions provided by the Worker Agents into a unified final solution without introducing any new content or solutions. If any Worker Agent did not provide a valid solution, skip that subtask and move on to the next.\n\n{''.join(worker_solutions)}")}]
        final_solution = client.messages.create(model=MODEL_NAME, max_tokens=MAX_TOKEN, messages=compiler_messages, system=compiler_prompt).content[0].text
        print("\nCompiler Output:")
        print(final_solution)
        time.sleep(delay)
        conversation_history += "\n" + final_solution

        # Step 6: Tester Agent
        tester_messages = [{"role": "user", "content": construct_agent_prompt("Tester", f"Test the final solution provided by the Compiler Agent against the original problem statement. Provide detailed feedback on the correctness and completeness of the solution, including any missing or incorrect components.\n\n{conversation_history}")}]
        test_result = client.messages.create(model=MODEL_NAME, max_tokens=MAX_TOKEN, messages=tester_messages, system=tester_prompt).content[0].text
        print("\nTester Output:")
        print(test_result)
        time.sleep(delay)
        conversation_history += "\n" + test_result

        # Calculate the solution quality score
        solution_quality_score = evaluate_solution_quality(test_result)
        print(f"Solution Quality Score: {solution_quality_score}")

        # Step 7: Error Identifier
        error_identifier_messages = [{"role": "user", "content": construct_agent_prompt("Error Identifier", f"Based on the feedback from the Tester Agent, identify and categorize any missing components, errors, or flaws in the final solution in detail.\n\n{conversation_history}")}]
        identified_errors = client.messages.create(model=MODEL_NAME, max_tokens=MAX_TOKEN, messages=error_identifier_messages, system=error_identifier_prompt).content[0].text

        print("\nError Identifier Output:")
        print(identified_errors)
        time.sleep(delay)
        conversation_history += "\n" + identified_errors

        # Step 8: Editor Agent
        editor_messages = [{"role": "user", "content": construct_agent_prompt("Editor", f"Based on the detailed feedback from the Error Identifier, suggest specific improvements or additions to the workflow or the final solution to address the identified issues.\n\n{conversation_history}")}]
        suggested_edits = client.messages.create(model=MODEL_NAME, max_tokens=MAX_TOKEN, messages=editor_messages, system=editor_prompt).content[0].text
        print("\nEditor Output:")
        print(suggested_edits)
        time.sleep(delay)
        conversation_history += "\n" + suggested_edits

        if solution_quality_score >= 0.9:
            problem_solved = True
            print("\nProblem solved successfully!")
        else:
            revised_problem_statement = suggested_edits
            iteration += 1

    return final_solution

def evaluate_solution_quality(test_result):
    if "no issues" in test_result.lower() or "correct" in test_result.lower():
        return 1.0
    elif "minor issues" in test_result.lower():
        return 0.7
    elif "significant issues" in test_result.lower():
        return 0.4
    else:
        return 0.1

user_prompt = ""
solution = solve_problem(user_prompt, delay=5, max_iterations=3)
print(f"\nFinal Solution:\n{solution}")
