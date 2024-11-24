import sys
import os
from datetime import datetime
from threading import Thread
import time
import ollama
import hashlib

fast = "llama3.2:3b"
powerful = "qwen2.5-coder:32b"


def get_concise_input(user_input, max_words=10):
    return ' '.join(user_input.split()[:max_words])


def get_hashed_input(user_input):
    # For alternative naming strategy using hash
    # Using first 8 chars of MD5 hash
    return hashlib.md5(user_input.encode()).hexdigest()[:8]


# Directory for output files
OUTPUT_DIR = f'output/{datetime.now().strftime('%Y%m%d_%H%M')}'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def stream_print(message, end='\n', delay=0.09):
    def print_message():
        for line in message.split('\n'):
            sys.stdout.write(line + '\n')
            sys.stdout.flush()
            time.sleep(delay)  # Pause between lines
        if end:
            sys.stdout.write(end)
            sys.stdout.flush()

    thread = Thread(target=print_message)
    thread.daemon = True  # So it exits when main program finishes
    thread.start()


def save_as_markdown(content, filename):
    """
    Create a function to convert the output as Markdown

    Args:
        content (string): longform text of the agent
        filename (string): name of the output file created
    """
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.md")
    with open(filepath, 'w') as file:
        file.write(content)
    stream_print(f"--- **Saved to {filepath}** ---")


def create_agent(step_number):
    """
    Creates an agent responsible for generating detailed implementations for a specific step.

    Args:
        step_number (int): The step number this agent is focused on.

    Returns:
        function: An agent function that takes a task and returns its implementation.
    """
    def agent(task):
        stream_print(f"--- **Agent {step_number} Activated** ---\r")
        stream_print(f"Received Task: {task}\r")
        stream_print(f"Generating Implementation for Step {step_number}...\r")

        response = ollama.chat(
            model=powerful,
            messages=[
                {
                    'role': 'system',
                    'content': f"""
                    You are Agent {step_number},
                    focused ONLY on implementing step
                    {step_number}. Provide a detailed but concise
                    implementation of this specific step. Ignore
                    all other steps.
                    """
                },
                {
                    'role': 'user',
                    'content': f"""
                    Given this task: {task}. Provide the
                    implementation for step {step_number} only.
                    """
                }
            ]
        )
        stream_print(
            f"--- **Received Response from Agent {step_number}** ---\n")

        # Save response as Markdown
        save_as_markdown(response['message']['content'],
                         f"Agent_{step_number}_Response")

        return response['message']['content']
    return agent


def ceo_agent(user_input, is_final=False):
    """
    Simulates the CEO Agent's role in generating either an initial plan or a final summary based on input.

    Args:
        user_input (str): The task or plan to process.
        is_final (bool, optional): Indicates whether to generate a final summary. Defaults to False.

    Returns:
        str: The generated plan or summary.
    """
    if not is_final:
        stream_print("--- **CEO Agent: Generating Initial Plan** ---\n")
        stream_print("Received Task: " + user_input + "\n")
    else:
        stream_print("--- **CEO Agent: Summarizing Final Strategy** ---\n")
        stream_print("Received Input for Summary:\n" +
                     user_input[:100] + "...\n")

    # Different prompt based on whether we're creating initial plan or final summary
    system_prompt = 'You are o1, an AI assistant focused on clear step-by-step reasoning. Break every task into actionable steps.' if not is_final else 'Summarize the following plan and its implementations into a cohesive final strategy.'

    response = ollama.chat(
        model=powerful,
        messages=[
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': user_input
            }
        ]
    )
    if not is_final:
        stream_print("--- **Received Initial Plan from CEO Agent** ---\n")
    else:
        stream_print("--- **Received Final Summary from CEO Agent** ---\n")

    # Save final response as Markdown
    if is_final:
        concise_input = get_concise_input(
            user_input, max_words=5)  # Adjust max_words as needed
        # Alternatively, use hashed input for uniqueness
        # hashed_input = get_hashed_input(user_input)
        save_as_markdown(response['message']['content'],
                         f"{concise_input}_Final_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    return response['message']['content']


def process_task(user_input):
    stream_print("--- **Task Processing Initiated** ---\n")
    stream_print("User Input: " + user_input + "\n")

    # Step 1: Get high-level plan from CEO
    stream_print("\n--- **Step 1: Retrieving Initial Plan** ---\n")
    initial_plan = ceo_agent(user_input)
    stream_print("Initial Plan Generated.\n")

    # Step 2: Create agents and get detailed implementation for each step
    stream_print(
        "\n--- **Step 2: Activating Agents for Detailed Implementations** ---\n")
    agents = [create_agent(i) for i in range(1, 5)]
    implementations = []
    for agent in agents:
        implementation = agent(initial_plan)
        implementations.append(implementation)
        stream_print("\n")  # Spacer for readability

    # Step 3: Combine everything and get final summary from CEO
    stream_print("\n--- **Step 3: Generating Final Summary** ---\n")
    final_input = f"Initial Plan: \n{
        initial_plan} \n\nImplementations: \n"+"\n".join(implementations)

    final_result = ceo_agent(final_input, is_final=True)
    stream_print("\n--- **Final Result Generated** ---\n")
    return final_result


# Example usage
if __name__ == "__main__":
    question = input("I am o1; ask me anything: ")
    result = process_task(question)
    stream_print("--- **Application Started** ---\n")
    final_result = process_task(result)
    stream_print("\n--- **FINAL OUTPUT** ---\n")
    stream_print(final_result + "\n")
    stream_print("--- **Process Completed** ---\n")
